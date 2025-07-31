# Contributing to Hypothesis Verification

Thank you for your interest in contributing to the Hypothesis Verification project! This document provides guidelines for contributing to the repository.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Repository Organization](#repository-organization)
- [Development Process](#development-process)
- [Submitting Changes](#submitting-changes)
- [Style Guidelines](#style-guidelines)
- [Adding New Analyses](#adding-new-analyses)

## Code of Conduct

- Be respectful and constructive in all interactions
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Hypothesis-Verification.git
   cd Hypothesis-Verification
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy environment template:
   ```bash
   cp .env.example .env
   # Add your API keys
   ```

## Repository Organization

### Directory Structure Rules

1. **Source Code** (`src/`)
   - Core functionality goes in `src/core/`
   - Analysis implementations go in `src/analyzers/`
   - Utility functions go in `src/utils/`

2. **Data Files** (`data/`)
   - Raw API data goes in `data/raw/`
   - Processed results go in `data/processed/`
   - Never commit large data files (>100MB)

3. **Results** (`results/`)
   - Organize by analysis type (e.g., `results/elon_tesla/`)
   - Reports go in `results/reports/`

4. **Templates** (`templates/`)
   - Examples go in `templates/examples/`
   - Keep templates well-documented

5. **Tests** (`tests/`)
   - Name test files as `test_*.py`
   - Mirror the `src/` structure

### File Naming Conventions

- Python modules: `lowercase_with_underscores.py`
- Analysis files: `{subject}_{type}_analysis.py`
- Data files: `{source}_raw_{date}.json`
- Reports: `{analysis}_report.md`
- Images: `{analysis}_{chart_type}.png`

## Development Process

### 1. Creating a New Feature

```bash
# Create a new branch
git checkout -b feature/your-feature-name

# Make your changes
# ...

# Run organization script
python scripts/organize_repo.py

# Run tests
python -m pytest tests/
```

### 2. Adding a New Analysis

To add a new analysis type:

1. **Create the analyzer**:
   ```python
   # src/analyzers/your_analysis.py
   class YourAnalyzer:
       def __init__(self, config):
           # Initialize
       
       def run_analysis(self):
           # Implementation
   ```

2. **Create a template**:
   ```yaml
   # templates/examples/your_example.yaml
   experiment:
     name: "Your Analysis"
     # ... configuration
   ```

3. **Add tests**:
   ```python
   # tests/test_your_analysis.py
   def test_your_analyzer():
       # Test implementation
   ```

4. **Create results directory**:
   ```bash
   mkdir -p results/your_analysis
   touch results/your_analysis/.gitkeep
   ```

5. **Update documentation**:
   - Add to `docs/STRUCTURE.md`
   - Update `README.md` if needed

### 3. Working with Templates

When creating new templates:

- Use the base template as a starting point
- Document all parameters clearly
- Provide realistic example values
- Test the template before committing

## Submitting Changes

### Pull Request Process

1. **Before submitting**:
   - Run the organization script: `python scripts/organize_repo.py`
   - Run tests: `python -m pytest`
   - Update documentation if needed

2. **Commit messages**:
   ```
   feat: Add new analysis for Reddit sentiment
   fix: Correct date parsing in Trump analyzer
   docs: Update template documentation
   refactor: Improve memory usage in analyzer
   ```

3. **Pull request description**:
   - Describe what changes you made
   - Explain why the changes are needed
   - List any breaking changes
   - Include example usage if applicable

### PR Checklist

- [ ] Code follows the project style guidelines
- [ ] Tests pass locally
- [ ] Documentation is updated
- [ ] Files are in correct directories
- [ ] No sensitive data (API keys, personal info) included
- [ ] Commit messages follow convention

## Style Guidelines

### Python Code Style

- Follow PEP 8
- Use meaningful variable names
- Add docstrings to all functions and classes
- Type hints are encouraged

```python
def analyze_sentiment(text: str, model: str = "gpt-3.5-turbo") -> Tuple[str, float]:
    """
    Analyze sentiment of given text.
    
    Args:
        text: Text to analyze
        model: LLM model to use
        
    Returns:
        Tuple of (sentiment, confidence)
    """
    # Implementation
```

### Documentation Style

- Use Markdown for all documentation
- Include code examples where helpful
- Keep language clear and concise
- Update docs when changing functionality

## Testing

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_hypothesis_system.py

# Run with coverage
python -m pytest --cov=src tests/
```

### Writing Tests

- Test both success and failure cases
- Use meaningful test names
- Mock external API calls
- Keep tests independent

## Questions?

If you have questions:

1. Check existing issues and discussions
2. Read the documentation
3. Open a new issue with your question

Thank you for contributing! 🚀