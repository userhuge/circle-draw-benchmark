import math
import xml.etree.ElementTree as ET
import re
import itertools
import argparse
from dataclasses import dataclass
from typing import List, Tuple, Set

# ==========================================
# 1. THE BENCHMARK DEFINITION
# ==========================================

@dataclass
class CircleRequest:
    color: str
    id: int

class OverlapTask:
    def __init__(self, num_circles: int, overlaps_needed: List[Tuple[str, str]]):
        self.colors = ["Red", "Blue", "Green", "Yellow", "Purple", "Orange"]
        if num_circles > len(self.colors):
            raise ValueError("Too many circles for defined colors.")
        
        self.circles = [self.colors[i] for i in range(num_circles)]
        self.overlaps_needed = set(tuple(sorted(pair)) for pair in overlaps_needed)

    def get_prompt(self) -> str:
        prompt = (
            f"Create a valid SVG code block containing exactly {len(self.circles)} circles. "
            f"The circles must be filled with these colors: {', '.join(self.circles)}. \n"
            "Use standard <circle cx='...' cy='...' r='...' fill='...' /> tags.\n\n"
            "CRITICAL GEOMETRY REQUIREMENTS:\n"
        )
        
        # Describe required overlaps
        if not self.overlaps_needed:
            prompt += "- No circles should overlap.\n"
        else:
            for c1, c2 in self.overlaps_needed:
                prompt += f"- The {c1} circle MUST overlap with the {c2} circle.\n"
            
        prompt += "- Any pair of circles not listed above must NOT overlap.\n"
        prompt += "Return only the SVG code."
        return prompt

# ==========================================
# 2. THE EVALUATOR (DETERMINISTIC MATH)
# ==========================================

class SVGEvaluator:
    def __init__(self, svg_text: str):
        self.svg_text = self._extract_svg(svg_text)
        self.circles = []
        self.parse_error = False
        self._parse_svg()

    def _extract_svg(self, text: str) -> str:
        # Extract content between ```svg or ```xml or just find the <svg> tag
        match = re.search(r'<svg.*?>.*?</svg>', text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(0)
        return text

    def _parse_svg(self):
        try:
            # Remove potential xmlns to simplify parsing
            clean_xml = re.sub(r'\sxmlns="[^"]+"', '', self.svg_text, count=1)
            root = ET.fromstring(clean_xml)
            
            for child in root.findall(".//circle"):
                # Extract geometry
                try:
                    cx = float(child.attrib.get('cx', 0))
                    cy = float(child.attrib.get('cy', 0))
                    r = float(child.attrib.get('r', 0))
                    fill = child.attrib.get('fill', 'black').lower()
                    self.circles.append({'color': fill, 'cx': cx, 'cy': cy, 'r': r})
                except ValueError:
                    continue # Skip malformed circles
        except ET.ParseError:
            self.parse_error = True

    def check_overlaps(self, required_overlaps: Set[Tuple[str, str]], all_required_colors: List[str]):
        if self.parse_error:
            return {"error": "Invalid SVG XML"}

        detected_circles = [c['color'] for c in self.circles]
        detected_overlaps = set()

        # normalize input colors to lowercase for comparison
        req_colors_lower = [c.lower() for c in all_required_colors]
        
        # Check geometry for every pair
        for c1, c2 in itertools.combinations(self.circles, 2):
            dist = math.sqrt((c1['cx'] - c2['cx'])**2 + (c1['cy'] - c2['cy'])**2)
            radius_sum = c1['r'] + c2['r']
            
            # If distance < radius_sum, they overlap
            if dist < radius_sum:
                # Store overlapping pair sorted by color name
                pair = tuple(sorted([c1['color'], c2['color']]))
                detected_overlaps.add(pair)

        # --- CALCULATE SCORES ---

        # 1. Circle Count Score
        circles_found_count = len(self.circles)
        expected_count = len(all_required_colors)
        
        # 2. Correct Overlaps (True Positives)
        # Convert required overlaps to lowercase for matching
        req_overlaps_lower = set(tuple(sorted((p[0].lower(), p[1].lower()))) for p in required_overlaps)
        
        true_positives = detected_overlaps.intersection(req_overlaps_lower)
        correct_overlaps_score = len(true_positives)

        # 3. Incorrect Overlaps (False Positives)
        # Overlaps that exist but were not asked for
        false_positives = detected_overlaps.difference(req_overlaps_lower)
        incorrect_overlaps_score = len(false_positives)

        # 4. Missed Overlaps (False Negatives)
        false_negatives = req_overlaps_lower.difference(detected_overlaps)

        return {
            "metric_circle_count": f"{circles_found_count}/{expected_count}",
            "metric_correct_overlaps_found": f"{correct_overlaps_score}/{len(req_overlaps_lower)}",
            "metric_incorrect_overlaps_made": incorrect_overlaps_score,
            "details": {
                "found_pairs": list(detected_overlaps),
                "missed_pairs": list(false_negatives),
                "hallucinated_pairs": list(false_positives)
            }
        }

# ==========================================
# 3. DEMO / USAGE
# ==========================================

def mock_llm_generate(prompt):
    """
    This simulates an LLM response. 
    In a real scenario, replace this with openai.ChatCompletion.create(...)
    """
    print(f"\n--- PROMPT SENT TO LLM ---\n{prompt}\n--------------------------")
    
    # SIMULATING A FLAWED RESPONSE:
    # It draws 3 circles. 
    # It successfully overlaps Red and Blue.
    # BUT it accidentally overlaps Blue and Green (which might not be requested).
    return """
    ```svg
    <svg width="300" height="300">
      <!-- Red Circle -->
      <circle cx="100" cy="100" r="50" fill="Red" />
      <!-- Blue Circle (Overlaps Red) -->
      <circle cx="160" cy="100" r="50" fill="Blue" />
      <!-- Green Circle (Accidentally overlaps Blue) -->
      <circle cx="220" cy="100" r="50" fill="Green" />
    </svg>
    ```
    """

def main():
    parser = argparse.ArgumentParser(
        description="Benchmark SVG circle drawing and overlap detection."
    )
    parser.add_argument(
        "--num-circles",
        type=int,
        default=3,
        help="Number of circles to generate (default: 3)"
    )
    parser.add_argument(
        "--overlaps",
        type=str,
        nargs="+",
        default=["Red,Blue"],
        help="List of circle pairs that should overlap, e.g., 'Red,Blue' 'Blue,Green' (default: 'Red,Blue')"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Parse overlaps from command line
    overlaps_needed = []
    for overlap_pair in args.overlaps:
        parts = overlap_pair.split(",")
        if len(parts) == 2:
            overlaps_needed.append((parts[0].strip(), parts[1].strip()))
    
    # Define the Task
    task = OverlapTask(num_circles=args.num_circles, overlaps_needed=overlaps_needed)
    
    if args.verbose:
        print(f"Task: {args.num_circles} circles with overlaps: {overlaps_needed}")
    
    # Get LLM Output
    svg_response = mock_llm_generate(task.get_prompt())
    
    # Evaluate
    evaluator = SVGEvaluator(svg_response)
    results = evaluator.check_overlaps(task.overlaps_needed, task.circles)
    
    print("\n--- EVALUATION RESULTS ---")
    print(f"1. Circle Count Accuracy: {results['metric_circle_count']}")
    print(f"2. Correct Overlaps:      {results['metric_correct_overlaps_found']}")
    print(f"3. Incorrect Overlaps:    {results['metric_incorrect_overlaps_made']}")
    
    if args.verbose:
        print("\nDebug Details:", results['details'])

if __name__ == "__main__":
    main()
