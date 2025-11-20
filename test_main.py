#run with python -m unittest test_main.py # in Codespace
import unittest
import sys
from io import StringIO
from main import OverlapTask, SVGEvaluator, mock_llm_generate, main


class TestOverlapTask(unittest.TestCase):
    """Test the OverlapTask class."""

    def test_overlap_task_creation(self):
        """Test creating an OverlapTask with valid parameters."""
        task = OverlapTask(num_circles=3, overlaps_needed=[("Red", "Blue")])
        self.assertEqual(len(task.circles), 3)
        self.assertIn("Red", task.circles)
        self.assertIn("Blue", task.circles)

    def test_overlap_task_too_many_circles(self):
        """Test that OverlapTask raises error for too many circles."""
        with self.assertRaises(ValueError):
            OverlapTask(num_circles=10, overlaps_needed=[])

    def test_overlap_task_prompt_generation(self):
        """Test that prompt is generated correctly."""
        task = OverlapTask(num_circles=2, overlaps_needed=[("Red", "Blue")])
        prompt = task.get_prompt()
        self.assertIn("Red", prompt)
        self.assertIn("Blue", prompt)
        self.assertIn("MUST overlap", prompt)


class TestSVGEvaluator(unittest.TestCase):
    """Test the SVGEvaluator class."""

    def test_svg_parsing_valid(self):
        """Test parsing a valid SVG."""
        svg_text = """
        <svg width="300" height="300">
            <circle cx="100" cy="100" r="50" fill="Red" />
            <circle cx="160" cy="100" r="50" fill="Blue" />
        </svg>
        """
        evaluator = SVGEvaluator(svg_text)
        self.assertFalse(evaluator.parse_error)
        self.assertEqual(len(evaluator.circles), 2)

    def test_svg_parsing_invalid_xml(self):
        """Test parsing invalid XML."""
        svg_text = "<svg><circle cx='100' cy='100' r='50' fill='Red' />"
        evaluator = SVGEvaluator(svg_text)
        self.assertTrue(evaluator.parse_error)

    def test_svg_extraction_from_markdown(self):
        """Test extracting SVG from markdown code block."""
        svg_text = """
        ```svg
        <svg width="300" height="300">
            <circle cx="100" cy="100" r="50" fill="Red" />
        </svg>
        ```
        """
        evaluator = SVGEvaluator(svg_text)
        self.assertFalse(evaluator.parse_error)
        self.assertEqual(len(evaluator.circles), 1)

    def test_overlap_detection(self):
        """Test overlap detection between circles."""
        svg_text = """
        <svg width="300" height="300">
            <circle cx="100" cy="100" r="50" fill="Red" />
            <circle cx="160" cy="100" r="50" fill="Blue" />
        </svg>
        """
        evaluator = SVGEvaluator(svg_text)
        results = evaluator.check_overlaps(
            {("red", "blue")}, ["Red", "Blue"]
        )
        self.assertEqual(results['metric_circle_count'], '2/2')
        self.assertIn("1/1", results['metric_correct_overlaps_found'])

    def test_no_overlap_detection(self):
        """Test detection when circles don't overlap."""
        svg_text = """
        <svg width="300" height="300">
            <circle cx="50" cy="100" r="30" fill="Red" />
            <circle cx="200" cy="100" r="30" fill="Blue" />
        </svg>
        """
        evaluator = SVGEvaluator(svg_text)
        results = evaluator.check_overlaps(
            {("red", "blue")}, ["Red", "Blue"]
        )
        self.assertIn("0/1", results['metric_correct_overlaps_found'])


class TestMockLLM(unittest.TestCase):
    """Test the mock LLM generation."""

    def test_mock_llm_returns_svg(self):
        """Test that mock LLM returns valid SVG content."""
        result = mock_llm_generate("test prompt")
        self.assertIn("<svg", result)
        self.assertIn("</svg>", result)
        self.assertIn("circle", result)


class TestArgparse(unittest.TestCase):
    """Test argparse integration."""

    def setUp(self):
        """Capture stdout for tests."""
        self.original_stdout = sys.stdout
        self.original_argv = sys.argv

    def tearDown(self):
        """Restore stdout and argv."""
        sys.stdout = self.original_stdout
        sys.argv = self.original_argv

    def test_argparse_defaults(self):
        """Test that argparse uses sensible defaults."""
        sys.argv = ["main.py"]
        sys.stdout = StringIO()
        try:
            main()
        except SystemExit:
            pass
        output = sys.stdout.getvalue()
        self.assertIn("EVALUATION RESULTS", output)

    def test_argparse_num_circles(self):
        """Test the --num-circles argument."""
        sys.argv = ["main.py", "--num-circles", "2"]
        sys.stdout = StringIO()
        try:
            main()
        except SystemExit:
            pass
        output = sys.stdout.getvalue()
        self.assertIn("EVALUATION RESULTS", output)

    def test_argparse_overlaps(self):
        """Test the --overlaps argument."""
        sys.argv = ["main.py", "--num-circles", "4", "--overlaps", "Red,Blue", "Green,Yellow"]
        sys.stdout = StringIO()
        try:
            main()
        except SystemExit:
            pass
        output = sys.stdout.getvalue()
        self.assertIn("EVALUATION RESULTS", output)

    def test_argparse_verbose(self):
        """Test the --verbose flag."""
        sys.argv = ["main.py", "--verbose"]
        sys.stdout = StringIO()
        try:
            main()
        except SystemExit:
            pass
        output = sys.stdout.getvalue()
        self.assertIn("Task:", output)
        self.assertIn("Debug Details:", output)


if __name__ == "__main__":
    unittest.main()
