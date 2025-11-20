# Circle Draw Benchmark

A Python benchmarking suite for evaluating LLM performance on geometric SVG generation tasks. This tool measures how well language models can generate SVG circles with precise overlap constraints.

## Features

- **Geometric Overlap Detection**: Uses deterministic mathematics to verify circle overlaps
- **Multiple LLM Provider Support**: Works with any LLM via liteLLM integration
- **Mock LLM Testing**: Built-in mock LLM for testing without API calls
- **Comprehensive Test Suite**: 13+ unit tests covering all major functionality
- **Flexible Configuration**: YAML-like JSON config for easy LLM switching
- **Detailed Metrics**: Evaluates circle count accuracy, overlap correctness, and false positives

## Installation

### Prerequisites
- Python 3.8+
- pip or uv package manager

### Setup

1. **Clone the repository**:
```bash
git clone https://github.com/userhuge/circle-draw-benchmark.git
cd circle-draw-benchmark
```

2. **Create a virtual environment** (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
# For mock LLM testing (no API required)
pip install -r requirements-dev.txt

# For real LLM integration with liteLLM
pip install litellm
# Or install all optional dependencies:
pip install -e ".[llm]"
```

## Quick Start

### Run with Mock LLM (No API Keys Required)

```bash
# Basic run with defaults
python main.py

# With custom parameters
python main.py --num-circles 4 --overlaps "Red,Blue" "Green,Yellow" --verbose

# Show help
python main.py --help
```

### Run Tests

```bash
# Run all tests
python -m unittest test_main -v

# Run specific test class
python -m unittest test_main.TestArgparse -v
```

## Configuration

### Using Mock LLM (Default)

The tool runs with a mock LLM by default, perfect for testing without API credentials:

```bash
python main.py --num-circles 3 --use-mock --verbose
```

### Using Real LLM Provider with liteLLM

1. **Create a config file** (`llm_config.json`):
```json
{
  "title": "Codestral",
  "provider": "mistral",
  "model": "codestral-latest",
  "apiBase": "https://codestral.mistral.ai/v1",
  "apiKey": "YOUR_API_KEY_HERE"
}
```

2. **Run with the config**:
```bash
python main.py --llm-config llm_config.json --verbose
```

Or set as environment variable:
```bash
export LLM_CONFIG='{"title":"Codestral","provider":"mistral","model":"codestral-latest","apiBase":"https://codestral.mistral.ai/v1","apiKey":"YOUR_KEY"}'
python main.py --verbose
```

### Example Config Templates

**Mistral (Codestral)**:
```json
{
  "title": "Codestral",
  "provider": "mistral",
  "model": "codestral-latest",
  "apiBase": "https://codestral.mistral.ai/v1",
  "apiKey": "YOUR_API_KEY"
}
```

**OpenAI**:
```json
{
  "title": "GPT-4",
  "provider": "openai",
  "model": "gpt-4",
  "apiBase": "https://api.openai.com/v1",
  "apiKey": "YOUR_API_KEY"
}
```

**Anthropic Claude**:
```json
{
  "title": "Claude 3 Opus",
  "provider": "anthropic",
  "model": "claude-3-opus-20240229",
  "apiBase": "https://api.anthropic.com",
  "apiKey": "YOUR_API_KEY"
}
```

## Command-Line Arguments

```
usage: main.py [-h] [--num-circles NUM_CIRCLES] [--overlaps OVERLAPS [OVERLAPS ...]]
               [--verbose] [--llm-config LLM_CONFIG] [--use-mock]

Benchmark SVG circle drawing and overlap detection.

options:
  -h, --help                    show this help message and exit
  --num-circles NUM_CIRCLES     Number of circles to generate (default: 3)
  --overlaps OVERLAPS           Circle pairs that should overlap, format: "Color1,Color2"
                               (default: "Red,Blue")
  --verbose                     Enable verbose output with debug details
  --llm-config LLM_CONFIG       Path to LLM config JSON file
  --use-mock                    Force using mock LLM instead of provider
```

## Usage Examples

### Example 1: Basic Benchmark
```bash
python main.py
```

Output:
```
--- EVALUATION RESULTS ---
1. Circle Count Accuracy: 3/3
2. Correct Overlaps:      1/1
3. Incorrect Overlaps:    1

Debug Details: {...}
```

### Example 2: Multi-Overlap Task
```bash
python main.py --num-circles 4 --overlaps "Red,Blue" "Green,Yellow" --verbose
```

### Example 3: Using Codestral API
```bash
python main.py --llm-config llm_config.json --num-circles 5 --verbose
```

### Example 4: Run Tests
```bash
python -m unittest test_main.TestArgparse::test_argparse_verbose -v
```

## Understanding the Output

### Metrics

- **Circle Count Accuracy**: Shows detected/expected circle count (e.g., "3/3" means 3 circles detected out of 3 expected)
- **Correct Overlaps**: Shows correct overlaps found/required (e.g., "1/1" means 1 correct overlap out of 1 required)
- **Incorrect Overlaps**: Number of false positive overlaps (unintended overlaps)

### Debug Details (with --verbose)

- **found_pairs**: List of all detected overlapping circle pairs
- **missed_pairs**: Overlaps that were required but not found
- **hallucinated_pairs**: False positive overlaps (not requested but created)

## Architecture

### Core Components

**OverlapTask**: Defines a geometric SVG generation task with constraints
```python
task = OverlapTask(
    num_circles=3,
    overlaps_needed=[("Red", "Blue"), ("Green", "Yellow")]
)
```

**SVGEvaluator**: Parses SVG and detects circle overlaps using distance calculations
```python
evaluator = SVGEvaluator(svg_xml)
results = evaluator.check_overlaps(required_overlaps, color_list)
```

**LLMConfig**: Manages LLM provider configuration
```python
config = LLMConfig({"provider": "mistral", "model": "codestral-latest", ...})
```

**call_llm()**: Unified interface to call any LLM via liteLLM or mock
```python
response = call_llm(prompt, config, verbose=True)
```

## Testing

### Run All Tests
```bash
python -m unittest test_main -v
```

### Run Specific Tests
```bash
# Test argparse integration
python -m unittest test_main.TestArgparse -v

# Test SVG evaluation
python -m unittest test_main.TestSVGEvaluator -v

# Test single method
python -m unittest test_main.TestArgparse.test_argparse_verbose -v
```

### Test Coverage

The test suite includes:
- **OverlapTask Tests** (3): Configuration, validation, prompt generation
- **SVGEvaluator Tests** (5): Parsing, overlap detection, error handling
- **Mock LLM Tests** (1): Response generation
- **Argparse Tests** (4): CLI argument handling

Run tests and get coverage:
```bash
python -m coverage run -m unittest test_main
python -m coverage report
```

## Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'litellm'`

**Solution**: Install liteLLM (optional for mock mode):
```bash
pip install litellm
```

Or run with mock mode:
```bash
python main.py --use-mock --verbose
```

### Issue: LLM API connection fails

**Solution**: Falls back to mock LLM automatically. Check your API key and endpoint:
```bash
# Verify config
cat llm_config.json

# Run with verbose to see error details
python main.py --llm-config llm_config.json --verbose
```

### Issue: Invalid JSON in config file

**Solution**: Validate your JSON:
```bash
python -c "import json; json.load(open('llm_config.json'))"
```

## Development

### Project Structure
```
circle-draw-benchmark/
├── main.py                      # Core benchmark logic + argparse
├── test_main.py                 # Unit tests (13 tests)
├── llm_config.example.json      # Example LLM configuration
├── .gitignore                   # Git ignore patterns
├── README.md                    # This file
├── LICENSE                      # Project license
└── SVG_Overlap_Benchmark_Geometric_Approach.ipynb  # Jupyter notebook
```

### Adding New LLM Providers

The `call_llm()` function uses liteLLM, which supports 100+ LLM providers. Update `llm_config.json`:

```json
{
  "title": "Your Provider",
  "provider": "provider-name",
  "model": "model-name",
  "apiBase": "https://api.example.com/v1",
  "apiKey": "YOUR_KEY"
}
```

Supported providers:
- OpenAI (gpt-3.5, gpt-4, etc.)
- Mistral/Codestral
- Anthropic Claude
- Google Vertex AI
- AWS Bedrock
- Ollama (local)
- And 90+ more via liteLLM

## Performance Tips

1. **Use mock LLM for development**: No API costs
2. **Cache responses**: For repeated tests, save API responses
3. **Batch tests**: Run multiple benchmarks with different parameters
4. **Monitor costs**: Track API calls in your LLM provider dashboard

## Contributing

Contributions welcome! Areas for improvement:
- Additional SVG validation
- Performance optimizations
- New evaluation metrics
- Additional test cases
- Documentation improvements

## License

See LICENSE file for details.

## References

- [liteLLM Documentation](https://docs.litellm.ai/)
- [Mistral API Documentation](https://docs.mistral.ai/)
- [SVG Specification](https://www.w3.org/TR/SVG2/)
- [Circle Intersection Mathematics](https://en.wikipedia.org/wiki/Intersection_(geometry))

## Support

For issues or questions:
1. Check existing GitHub issues
2. Run tests with `--verbose` flag
3. Check configuration with example templates
4. Review error messages in terminal output

---

**Last Updated**: November 2025
**Status**: Active Development
**Python Version**: 3.8+
