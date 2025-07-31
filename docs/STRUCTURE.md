# Repository Structure

This document describes the organization of the Hypothesis Verification repository.

## Directory Structure

```
Hypothesis-Verification/
├── src/                    # Source code
│   ├── core/              # Core functionality
│   │   ├── hypothesis_runner.py         # Main template runner
│   │   └── universal_sentiment_analyzer.py # Universal analyzer
│   ├── analyzers/         # Specific analysis implementations
│   │   ├── tesla_sentiment_analysis.py
│   │   ├── tesla_multi_condition_analysis.py
│   │   ├── trump_tech_sentiment_analysis.py
│   │   └── sentiment_classification_methodology.py
│   └── utils/             # Utility functions
│
├── data/                  # Data files
│   ├── raw/              # Raw data from APIs
│   │   ├── elon_raw_tweets.json
│   │   └── trump_raw_tweets.json
│   └── processed/        # Processed analysis data
│       ├── analysis_results.csv
│       ├── multi_condition_analysis.csv
│       └── sentiment_classification_details.json
│
├── results/              # Analysis results
│   ├── elon_tesla/      # Elon Musk Tesla analysis results
│   ├── trump_tech/      # Trump tech analysis results
│   └── reports/         # Generated reports
│       ├── tesla_sentiment_analysis_report.md
│       ├── trump_tech_sentiment_report.md
│       └── sentiment_classification_methodology_report.md
│
├── assets/              # Static assets
│   └── images/         # Generated visualizations
│       ├── sentiment_comparison.png
│       ├── impact_timeline.png
│       └── [other visualizations]
│
├── templates/           # YAML experiment templates
│   ├── hypothesis_template.yaml
│   └── examples/
│       ├── elon_tesla_example.yaml
│       └── trump_tesla_example.yaml
│
├── tests/              # Test files
│   └── test_hypothesis_system.py
│
├── scripts/            # Utility scripts
│   ├── organize_repo.py    # Repository organization script
│   └── cleanup.sh          # Cleanup script
│
├── docs/               # Documentation
│   ├── STRUCTURE.md        # This file
│   ├── API.md             # API documentation
│   └── CONTRIBUTING.md     # Contribution guidelines
│
├── config/             # Configuration files
│
├── .github/            # GitHub specific files
│   └── workflows/      # GitHub Actions
│       └── organize.yml    # Auto-organization workflow
│
├── README.md           # Main documentation
├── requirements.txt    # Python dependencies
├── .env.example       # Environment variables example
└── .gitignore         # Git ignore rules
```

## File Naming Conventions

### Source Code
- Use lowercase with underscores: `module_name.py`
- Analyzers should end with `_analysis.py`
- Test files should start with `test_`

### Data Files
- Raw data: `{source}_raw_{type}.{ext}`
- Processed data: `{analysis}_results.{ext}`
- Include timestamps when relevant: `{name}_{YYYYMMDD}.{ext}`

### Reports and Visualizations
- Reports: `{analysis}_report.md`
- Images: `{analysis}_{chart_type}.png`

## Organization Rules

1. **Source Code**: All Python modules go in `src/` with appropriate subdirectories
2. **Data Separation**: Keep raw and processed data separate
3. **Results**: Organize by experiment/analysis type
4. **Assets**: All images and static files in `assets/`
5. **Documentation**: All docs in `docs/` except README.md
6. **Tests**: All test files in `tests/`
7. **Templates**: Keep templates organized by type/purpose

## Adding New Analyses

When adding a new analysis:

1. Create analyzer in `src/analyzers/{name}_analysis.py`
2. Add template in `templates/examples/{name}_example.yaml`
3. Create results directory: `results/{name}/`
4. Update this documentation
5. Add tests in `tests/test_{name}.py`

## Maintenance

- Run `scripts/organize_repo.py` periodically to reorganize files
- Use GitHub Actions to enforce structure on PRs
- Review and clean up old results quarterly