# Hypothesis Verification System

A comprehensive system for analyzing correlations between social media sentiment and stock price movements. This repository provides both specific implementations and a flexible template system for running various hypothesis verification experiments.

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/wkumagai/Hypothesis-Verification.git
cd Hypothesis-Verification

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Run an example experiment
python src/core/hypothesis_runner.py templates/examples/trump_tesla_example.yaml
```

## 📋 Project Structure

```
Hypothesis-Verification/
├── src/                           # Source code
│   ├── core/                      # Core functionality
│   │   ├── hypothesis_runner.py  # Template-based experiment runner
│   │   ├── hypothesis_runner_enhanced.py  # Enhanced runner with subagents
│   │   ├── universal_sentiment_analyzer.py
│   │   └── subagent_framework.py  # Subagent orchestration system
│   ├── analyzers/                 # Analysis implementations
│   │   ├── tesla_sentiment_analysis.py
│   │   ├── trump_tech_sentiment_analysis.py
│   │   └── sentiment_classification_methodology.py
│   └── utils/                     # Utility functions
├── data/                          # Data storage
│   ├── raw/                       # Raw API data
│   └── processed/                 # Processed results
├── results/                       # Analysis outputs
│   ├── elon_tesla/               # Elon Musk analysis results
│   ├── trump_tech/               # Trump analysis results
│   └── reports/                  # Generated reports
├── assets/                        # Static assets
│   └── images/                   # Charts and visualizations
├── templates/                     # Experiment templates
│   ├── hypothesis_template.yaml  # Base template
│   ├── hypothesis_template_with_subagents.yaml  # Enhanced template
│   └── examples/                 # Example configurations
├── subagents/                     # Subagent specifications
│   ├── data_validator.md         # Data quality validation
│   ├── market_context.md         # Market research
│   ├── statistical_analyzer.md   # Statistical validation
│   ├── report_generator.md       # Report generation
│   └── spec_researcher.md        # Spec updates
├── tests/                        # Test suite
├── scripts/                      # Utility scripts
│   ├── organize_repo.py         # Auto-organization script
│   └── cleanup.sh               # Cleanup script
├── docs/                         # Documentation
│   ├── STRUCTURE.md             # Repository organization guide
│   └── CONTRIBUTING.md          # Contribution guidelines
└── .github/                      # GitHub configurations
    └── workflows/                # GitHub Actions
        └── organize.yml          # Auto-organization workflow
```

For detailed structure documentation, see [docs/STRUCTURE.md](docs/STRUCTURE.md).

## 🧪 Template System

The template system allows you to define hypothesis verification experiments in YAML format. Templates can be filled manually or by AI systems.

### 🤖 NEW: Subagent System

The enhanced hypothesis runner now includes specialized AI subagents that automatically improve your analysis:

- **Data Validator**: Ensures data quality before analysis
- **Market Context**: Researches confounding market events  
- **Statistical Analyzer**: Performs rigorous statistical validation
- **Report Generator**: Creates professional, standardized reports
- **Spec Researcher**: Keeps dependencies and APIs up-to-date

#### Using Subagents

```bash
# Run with full subagent support (default)
python src/core/hypothesis_runner_enhanced.py templates/example_with_subagents.yaml

# Run without subagents for comparison
python src/core/hypothesis_runner_enhanced.py templates/example.yaml --no-subagents
```

### Basic Template Structure

```yaml
experiment:
  name: "Your Experiment Name"
  hypothesis: "Your hypothesis statement"
  
  data_sources:
    social_media:
      platform: "twitter"
      accounts: ["account1", "account2"]
      keywords: ["keyword1", "keyword2"]
      date_range:
        start: "365_days_ago"  # or YYYY-MM-DD
        end: "now"
    
    market_data:
      symbols:
        - symbol: "TSLA"
          name: "Tesla Inc."
  
  sentiment_analysis:
    llm_provider: "openai"  # or "anthropic"
    model: "gpt-4-turbo-preview"
    temperature: 0.0
    
  analysis:
    time_intervals: [1, 6, 12, 24]  # hours
```

### Creating a New Experiment

1. Copy the template:
   ```bash
   cp templates/hypothesis_template.yaml templates/my_experiment.yaml
   ```

2. Fill in the template with your parameters

3. Run the experiment:
   ```bash
   python src/core/hypothesis_runner.py templates/my_experiment.yaml
   ```

## 📊 Analysis Types

### 1. Social Media Sentiment Analysis
- Fetches posts from specified accounts
- Filters by keywords
- Classifies sentiment using LLMs (GPT-4, Claude, etc.)
- Supports custom sentiment categories

### 2. Stock Price Impact Analysis
- Measures price changes at multiple time intervals
- Correlates with post timestamps
- Handles market hours vs after-hours analysis

### 3. Multi-Condition Analysis
- Engagement levels (viral, high, medium, low)
- Market timing
- Product announcements
- Custom conditions

## 🔧 Configuration

### Required API Keys

Create a `.env` file with:

```bash
# Social Media Scraping
APIFY_API_KEY=your_apify_key

# Stock Market Data
ALPACA_API_KEY=your_alpaca_key
ALPACA_SECRET_KEY=your_alpaca_secret

# LLM Providers
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key  # Optional
```

### Supported Platforms

- **Social Media**: Twitter/X (via Apify)
- **Market Data**: Alpaca Markets (IEX feed)
- **LLMs**: OpenAI GPT models, Anthropic Claude

## 📈 Example Results

### Trump Tech Sentiment Analysis
- 90% of Trump's tech/Elon tweets were classified as BULLISH
- Average 24-hour stock impact varied by sentiment
- High engagement posts showed stronger correlations

### Elon Musk Tesla Analysis
- 76.6% bullish sentiment in Tesla-related tweets
- Surprising finding: Neutral tweets had highest positive impact (+8.47% at 24h)
- Market hours tweets performed worse than after-hours

## 🛠️ Advanced Usage

### Custom Conditions

Add custom analysis conditions in your template:

```yaml
conditions:
  - name: "contains_numbers"
    description: "Tweet contains specific metrics"
    enabled: true
    implementation: "check_metrics_in_text"
```

### Batch Processing

Process multiple experiments:

```bash
for template in templates/experiments/*.yaml; do
    python src/core/hypothesis_runner.py "$template"
done
```

### 🤖 Subagent Configuration

Configure which subagents to use in your template:

```yaml
experiment:
  # Enable specific subagents
  subagents:
    - data_validator      # Quality assurance
    - market_context      # External factors
    - statistical_analyzer # Rigorous validation
    - report_generator    # Professional outputs
  
  # Configure subagent behavior
  analysis:
    statistical_rigor: "academic"  # basic, standard, academic

# Subagent-specific settings
subagent_config:
  data_validator:
    strict_mode: true
    check_duplicates: true
  
  statistical_analyzer:
    confidence_level: 0.95
    bootstrap_iterations: 10000
```

### Programmatic Usage

```python
import sys
sys.path.append('src')
from core.hypothesis_runner import HypothesisRunner

runner = HypothesisRunner("path/to/template.yaml")
results = runner.run_experiment()
```

## 📚 Methodology

### Sentiment Classification
- Uses LLMs with temperature=0 for consistency
- Fallback to keyword-based classification
- Confidence scores for each classification

### Price Impact Calculation
- Baseline price at tweet time
- Percentage change at specified intervals
- Handles missing data gracefully

### Statistical Analysis
- Mean, median, standard deviation
- Distribution analysis
- Correlation metrics

## 🧪 Testing

Run the test suite:

```bash
python test_hypothesis_system.py
```

Tests include:
- Template validation
- Date processing
- Configuration generation
- Multi-template support

## 📝 Creating Reports

Generated reports include:
- Sentiment distribution charts
- Price impact visualizations
- Time series analysis
- Engagement vs impact correlations
- Statistical summaries
- Methodology documentation

## 🗂️ Repository Maintenance

### Automated Organization

The repository includes automated organization features:

1. **Organization Script**: Run manually to reorganize files
   ```bash
   python scripts/organize_repo.py
   ```

2. **Cleanup Script**: Remove temporary files and organize
   ```bash
   ./scripts/cleanup.sh
   ```

3. **GitHub Actions**: Automatically runs weekly and on PRs to maintain structure

### Contributing

See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines on:
- File naming conventions
- Directory structure rules
- Adding new analyses
- Submitting pull requests

## 🚀 Future Enhancements

- [x] Specialized subagents for quality control
- [ ] Support for Reddit, Truth Social
- [ ] Real-time monitoring mode
- [ ] Machine learning predictions
- [ ] Multi-symbol portfolio analysis
- [x] Automated report generation
- [ ] Web dashboard interface
- [ ] Cross-agent memory sharing
- [ ] Automated experiment optimization

## 📄 License

This project is for research and educational purposes. Ensure compliance with:
- API terms of service
- Market data usage restrictions
- Social media platform policies

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📞 Support

For issues or questions:
- Open an issue on GitHub
- Check existing documentation
- Review example templates

---

**Note**: This system uses delayed market data (15-minute delay on IEX feed). For real-time analysis, upgrade to premium data feeds.