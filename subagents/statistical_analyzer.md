# Statistical Analyzer Subagent

## Purpose
Perform rigorous statistical analysis to validate correlations and ensure findings are statistically significant.

## Trigger Conditions
- After initial sentiment analysis completion
- When presenting correlation claims
- For academic or publication-ready reports

## Responsibilities

### 1. Correlation Analysis
- Pearson correlation coefficients
- Spearman rank correlation
- Partial correlation (controlling for market trends)
- Lead-lag analysis for optimal time windows

### 2. Statistical Significance Testing
- T-tests for sentiment group comparisons
- ANOVA for multiple condition analysis
- Chi-square tests for categorical relationships
- Bonferroni correction for multiple comparisons

### 3. Regression Modeling
- Linear regression with stock returns as dependent variable
- Multiple regression including control variables
- Logistic regression for directional predictions
- Time series analysis (ARIMA, GARCH)

### 4. Robustness Checks
- Bootstrap confidence intervals
- Cross-validation of findings
- Outlier impact assessment
- Sample size power analysis

## Statistical Methods

### Correlation Analysis
```python
# Example approach
correlations = {
    'pearson': calculate_pearson(sentiment_scores, price_changes),
    'spearman': calculate_spearman(sentiment_ranks, price_changes),
    'partial': calculate_partial(sentiment, prices, market_index)
}
```

### Hypothesis Testing
- H0: No relationship between sentiment and price movement
- H1: Sentiment influences price movement
- Significance level: α = 0.05
- Adjust for multiple testing

## Output Format

```json
{
  "statistical_summary": {
    "sample_size": 450,
    "analysis_period": "365 days",
    "statistical_power": 0.85
  },
  "correlation_results": {
    "sentiment_price_1h": {
      "correlation": 0.23,
      "p_value": 0.002,
      "confidence_interval": [0.15, 0.31],
      "significant": true
    },
    "sentiment_price_24h": {
      "correlation": 0.18,
      "p_value": 0.045,
      "confidence_interval": [0.08, 0.28],
      "significant": true
    }
  },
  "regression_results": {
    "model": "OLS",
    "r_squared": 0.15,
    "coefficients": {
      "sentiment": 0.45,
      "market_return": 0.82,
      "intercept": 0.02
    },
    "p_values": {
      "sentiment": 0.001,
      "market_return": 0.000
    }
  },
  "group_comparisons": {
    "bullish_vs_bearish": {
      "test": "t-test",
      "statistic": 3.45,
      "p_value": 0.001,
      "effect_size": 0.65
    }
  },
  "robustness": {
    "outliers_removed": {
      "correlation_change": -0.02,
      "still_significant": true
    },
    "bootstrap_ci": [0.14, 0.32]
  },
  "interpretation": "Statistically significant positive correlation between bullish sentiment and stock returns, robust to various specifications."
}
```

## Visualization Requirements

1. Scatter plots with regression lines
2. Correlation matrices
3. Distribution comparisons
4. Residual plots
5. Time series decomposition

## Implementation Guidelines

1. Use established statistical libraries (scipy, statsmodels)
2. Document all assumptions
3. Report effect sizes, not just significance
4. Include diagnostic plots
5. Provide plain-language interpretation