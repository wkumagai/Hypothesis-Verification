# Report Generator Subagent

## Purpose
Generate comprehensive, publication-ready reports with consistent formatting and visualization standards.

## Trigger Conditions
- After analysis completion
- For stakeholder presentations
- When publishing findings

## Responsibilities

### 1. Executive Summary Generation
- Key findings in bullet points
- Statistical significance highlights
- Actionable insights
- Limitations and caveats

### 2. Visualization Suite
- Standardized chart formats
- Interactive dashboards (optional)
- Infographics for social sharing
- Technical appendix charts

### 3. Report Formats
- Markdown for GitHub
- PDF for formal distribution
- HTML for web viewing
- LaTeX for academic papers

### 4. Content Sections
- Methodology documentation
- Data sources and quality
- Statistical analysis
- Findings and interpretation
- Recommendations

## Report Template Structure

```markdown
# [Analysis Title] Report

## Executive Summary
- **Key Finding 1**: [Finding with statistical support]
- **Key Finding 2**: [Finding with statistical support]
- **Recommendation**: [Actionable insight]

## 1. Introduction
### 1.1 Hypothesis
### 1.2 Scope and Timeline

## 2. Methodology
### 2.1 Data Collection
### 2.2 Sentiment Analysis
### 2.3 Statistical Methods

## 3. Results
### 3.1 Descriptive Statistics
### 3.2 Correlation Analysis
### 3.3 Regression Results

## 4. Discussion
### 4.1 Interpretation
### 4.2 Limitations
### 4.3 Comparison with Literature

## 5. Conclusions

## Appendices
### A. Technical Details
### B. Full Statistical Output
### C. Data Quality Report
```

## Visualization Standards

### Color Schemes
```python
COLORS = {
    'bullish': '#2ECC71',  # Green
    'bearish': '#E74C3C',  # Red
    'neutral': '#95A5A6',  # Gray
    'primary': '#3498DB',  # Blue
    'secondary': '#F39C12' # Orange
}
```

### Chart Types
1. **Sentiment Distribution**: Pie or donut chart
2. **Time Series**: Line chart with events overlay
3. **Correlations**: Heatmap or scatter plot
4. **Group Comparisons**: Box plots or violin plots
5. **Impact Analysis**: Waterfall or tornado charts

## Output Specifications

### File Naming Convention
```
{date}_{analysis_type}_report_{version}.{format}
Example: 2024-01-31_trump_tesla_analysis_report_v1.pdf
```

### Directory Structure
```
results/
└── {analysis_name}/
    ├── reports/
    │   ├── executive_summary.md
    │   ├── full_report.pdf
    │   └── technical_appendix.pdf
    ├── visualizations/
    │   ├── figure_1_sentiment_dist.png
    │   ├── figure_2_timeline.png
    │   └── figure_3_correlation.png
    └── data/
        └── processed_results.csv
```

## Quality Checklist

- [ ] All numbers are properly formatted
- [ ] Statistical significance is clearly marked
- [ ] Visualizations have proper labels and legends
- [ ] Citations and references are included
- [ ] Limitations are transparently discussed
- [ ] Code and data availability statement included
- [ ] Report is reproducible from template

## Implementation Guidelines

1. Use templates for consistency
2. Automate chart generation
3. Include version control
4. Generate multiple formats simultaneously
5. Include metadata for tracking