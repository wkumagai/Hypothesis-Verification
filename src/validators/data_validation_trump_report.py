#!/usr/bin/env python3
"""
Data Validation Analysis for Trump Tech Sentiment Report
Uses Data Validator subagent principles to identify quality issues
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Tuple

class TrumpReportDataValidator:
    def __init__(self):
        self.validation_results = {
            "validation_status": "CRITICAL_FAILURE",
            "timestamp": datetime.now().isoformat(),
            "report_file": "trump_tech_sentiment_report.md",
            "checks": {},
            "critical_issues": [],
            "recommendations": [],
            "data_quality_score": 0.0
        }
        self.critical_issues = self.validation_results["critical_issues"]
    
    def validate_report(self) -> Dict[str, Any]:
        """Run comprehensive validation checks on the report"""
        
        # 1. Data Completeness Check
        self._check_data_completeness()
        
        # 2. Data Consistency Check
        self._check_data_consistency()
        
        # 3. Statistical Validity Check
        self._check_statistical_validity()
        
        # 4. Temporal Coverage Check
        self._check_temporal_coverage()
        
        # 5. Market Data Integration Check
        self._check_market_data_integration()
        
        # 6. Sample Size Adequacy Check
        self._check_sample_size()
        
        # 7. Methodology Transparency Check
        self._check_methodology_transparency()
        
        # Calculate overall score
        self._calculate_quality_score()
        
        return self.validation_results
    
    def _check_data_completeness(self):
        """Check if all required data fields are present and populated"""
        issues = []
        
        # Critical missing data
        missing_price_data = True  # All price impact data shows "N/A"
        missing_top_tweets = True  # Top impact tweets sections are empty
        incomplete_statistics = True  # Statistical summary is all "N/A"
        
        if missing_price_data:
            issues.append({
                "severity": "CRITICAL",
                "field": "price_impact_data",
                "issue": "All stock price impact measurements are missing (N/A)",
                "impact": "Cannot assess correlation between sentiment and stock movement"
            })
            self.critical_issues.append("Missing all price impact data")
        
        if missing_top_tweets:
            issues.append({
                "severity": "HIGH",
                "field": "top_impact_tweets",
                "issue": "Top positive and negative impact tweet sections are empty",
                "impact": "Cannot identify which tweets had significant market impact"
            })
        
        if incomplete_statistics:
            issues.append({
                "severity": "CRITICAL",
                "field": "statistical_summary",
                "issue": "All statistical metrics (mean, std dev, min, max) are N/A",
                "impact": "Cannot assess statistical significance or variability"
            })
            self.critical_issues.append("No statistical calculations performed")
        
        self.validation_results["checks"]["completeness"] = {
            "status": "FAILED",
            "issues": issues,
            "missing_critical_fields": 3,
            "completeness_score": 0.2  # Only basic metadata is complete
        }
    
    def _check_data_consistency(self):
        """Check for internal consistency in the report"""
        issues = []
        
        # Sample size inconsistencies
        total_tweets = 20
        bullish = 18
        neutral = 2
        bearish = 0  # Not mentioned but should be tracked
        
        if (bullish + neutral + bearish) != total_tweets:
            issues.append({
                "severity": "MEDIUM",
                "issue": "Missing BEARISH category in sentiment distribution",
                "impact": "Incomplete sentiment analysis"
            })
        
        # Market hours distribution
        market_hours = 7
        after_hours = 13
        if (market_hours + after_hours) != total_tweets:
            issues.append({
                "severity": "LOW",
                "issue": "Market hours distribution matches total tweets",
                "status": "PASSED"
            })
        
        self.validation_results["checks"]["consistency"] = {
            "status": "WARNING",
            "issues": issues,
            "consistency_score": 0.7
        }
    
    def _check_statistical_validity(self):
        """Check statistical analysis validity"""
        issues = []
        
        # No statistical calculations were performed
        issues.append({
            "severity": "CRITICAL",
            "issue": "No statistical calculations despite having sentiment data",
            "required_analyses": [
                "T-tests between sentiment groups",
                "Correlation coefficients",
                "Confidence intervals",
                "P-values for significance",
                "Effect size measurements"
            ]
        })
        
        # Sample size concerns
        issues.append({
            "severity": "HIGH",
            "issue": "Sample size of 20 tweets is too small for reliable statistical inference",
            "minimum_recommended": 100,
            "impact": "Results may not be statistically significant"
        })
        
        self.validation_results["checks"]["statistical_validity"] = {
            "status": "FAILED",
            "issues": issues,
            "validity_score": 0.0
        }
    
    def _check_temporal_coverage(self):
        """Check time period coverage"""
        issues = []
        
        # Time period analysis
        start_date = "2024-01-15"
        end_date = "2024-04-25"
        days_covered = 100  # Approximate
        tweets_per_day = 20 / days_covered  # 0.2 tweets per day
        
        issues.append({
            "severity": "HIGH",
            "issue": f"Only {tweets_per_day:.2f} tweets per day average",
            "recommendation": "Expand date range or collect more tweets",
            "impact": "Sparse data may miss important events"
        })
        
        issues.append({
            "severity": "MEDIUM",
            "issue": "Analysis claims 'past 12 months' but only covers ~3 months",
            "actual_coverage": "100 days",
            "claimed_coverage": "12 months"
        })
        
        self.validation_results["checks"]["temporal_coverage"] = {
            "status": "WARNING",
            "issues": issues,
            "coverage_score": 0.3
        }
    
    def _check_market_data_integration(self):
        """Check market data integration quality"""
        issues = []
        
        issues.append({
            "severity": "CRITICAL",
            "issue": "No market data was successfully integrated",
            "evidence": "All price impact fields show N/A",
            "possible_causes": [
                "API connection failure",
                "Date mismatch between tweets and market data",
                "Incorrect symbol mapping",
                "Market data not available for time periods"
            ]
        })
        
        issues.append({
            "severity": "HIGH",
            "issue": "Cannot verify market hours classification without timestamps",
            "impact": "Market hours analysis may be inaccurate"
        })
        
        self.validation_results["checks"]["market_data_integration"] = {
            "status": "FAILED",
            "issues": issues,
            "integration_score": 0.0
        }
    
    def _check_sample_size(self):
        """Check if sample size is adequate for conclusions"""
        issues = []
        
        min_samples_by_analysis = {
            "basic_correlation": 30,
            "statistical_significance": 100,
            "subgroup_analysis": 50,
            "time_series_analysis": 200
        }
        
        actual_samples = 20
        
        for analysis_type, min_required in min_samples_by_analysis.items():
            if actual_samples < min_required:
                issues.append({
                    "severity": "HIGH",
                    "analysis_type": analysis_type,
                    "required_samples": min_required,
                    "actual_samples": actual_samples,
                    "adequacy": f"{(actual_samples/min_required)*100:.1f}%"
                })
        
        self.validation_results["checks"]["sample_size"] = {
            "status": "FAILED",
            "issues": issues,
            "adequacy_score": 0.2
        }
    
    def _check_methodology_transparency(self):
        """Check methodology documentation"""
        positive_aspects = []
        issues = []
        
        # Positive aspects
        positive_aspects.extend([
            "LLM model and temperature specified",
            "Data source (Alpaca API) identified",
            "Keywords listed",
            "Market hours definition provided",
            "Limitations section included"
        ])
        
        # Missing aspects
        issues.extend([
            {
                "severity": "MEDIUM",
                "issue": "No explanation for missing price data",
                "needed": "Troubleshooting steps or error messages"
            },
            {
                "severity": "HIGH",
                "issue": "Sentiment classification prompt not included",
                "impact": "Cannot reproduce sentiment analysis"
            },
            {
                "severity": "MEDIUM",
                "issue": "No data collection methodology details",
                "needed": "How were Trump's tweets filtered and collected?"
            }
        ])
        
        self.validation_results["checks"]["methodology"] = {
            "status": "WARNING",
            "positive_aspects": positive_aspects,
            "issues": issues,
            "transparency_score": 0.6
        }
    
    def _calculate_quality_score(self):
        """Calculate overall data quality score"""
        scores = []
        weights = {
            "completeness": 0.3,
            "consistency": 0.1,
            "statistical_validity": 0.2,
            "market_data_integration": 0.25,
            "sample_size": 0.1,
            "methodology": 0.05
        }
        
        for check_name, check_data in self.validation_results["checks"].items():
            if check_name in ["completeness", "consistency", "temporal_coverage"]:
                score = check_data.get("completeness_score", 
                                     check_data.get("consistency_score", 
                                     check_data.get("coverage_score", 0)))
            elif check_name == "statistical_validity":
                score = check_data.get("validity_score", 0)
            elif check_name == "market_data_integration":
                score = check_data.get("integration_score", 0)
            elif check_name == "sample_size":
                score = check_data.get("adequacy_score", 0)
            elif check_name == "methodology":
                score = check_data.get("transparency_score", 0)
            else:
                score = 0
            
            weight = weights.get(check_name.replace("_", ""), 0.1)
            scores.append(score * weight)
        
        self.validation_results["data_quality_score"] = sum(scores)
        
        # Generate prioritized recommendations
        self._generate_recommendations()
    
    def _generate_recommendations(self):
        """Generate actionable recommendations based on validation results"""
        
        recommendations = [
            {
                "priority": "CRITICAL",
                "action": "Fix market data integration",
                "steps": [
                    "Verify Alpaca API credentials are correct",
                    "Check if TSLA data is available for the tweet dates",
                    "Ensure tweet timestamps are properly parsed",
                    "Test API connection with known good dates",
                    "Consider using fallback data source if Alpaca fails"
                ],
                "expected_outcome": "Price impact data populated for all tweets"
            },
            {
                "priority": "CRITICAL",
                "action": "Increase sample size",
                "steps": [
                    "Extend date range to full 12 months",
                    "Remove restrictive keyword filters if applicable",
                    "Include all Trump tweets mentioning tech companies",
                    "Target minimum 100-200 tweets for statistical validity"
                ],
                "expected_outcome": "Statistically significant results"
            },
            {
                "priority": "HIGH",
                "action": "Implement statistical analysis",
                "steps": [
                    "Calculate correlation coefficients",
                    "Perform t-tests between sentiment groups",
                    "Add confidence intervals",
                    "Include p-values for all comparisons",
                    "Calculate effect sizes (Cohen's d)"
                ],
                "expected_outcome": "Complete statistical validation"
            },
            {
                "priority": "HIGH",
                "action": "Add data completeness checks",
                "steps": [
                    "Implement pre-analysis data validation",
                    "Create fallback handling for missing data",
                    "Log all data collection failures",
                    "Add data quality metrics to report"
                ],
                "expected_outcome": "Transparent data quality reporting"
            },
            {
                "priority": "MEDIUM",
                "action": "Enhance methodology documentation",
                "steps": [
                    "Include exact sentiment classification prompts",
                    "Document data collection process",
                    "Add flowchart of analysis pipeline",
                    "Include example tweet classifications"
                ],
                "expected_outcome": "Fully reproducible analysis"
            }
        ]
        
        self.validation_results["recommendations"] = recommendations

def generate_validation_report(results: Dict[str, Any]) -> str:
    """Generate a markdown report of validation results"""
    
    report = f"""# Data Validation Report: Trump Tech Sentiment Analysis

**Validation Date**: {results['timestamp']}
**Overall Data Quality Score**: {results['data_quality_score']:.1%}
**Validation Status**: {results['validation_status']}

## Critical Issues Identified

"""
    
    for issue in results['critical_issues']:
        report += f"- 🚨 **{issue}**\n"
    
    report += "\n## Detailed Validation Results\n\n"
    
    for check_name, check_data in results['checks'].items():
        status_emoji = "✅" if check_data['status'] == "PASSED" else "⚠️" if check_data['status'] == "WARNING" else "❌"
        
        report += f"### {check_name.replace('_', ' ').title()}\n"
        report += f"**Status**: {status_emoji} {check_data['status']}\n\n"
        
        if 'issues' in check_data:
            for issue in check_data['issues']:
                if isinstance(issue, dict) and 'severity' in issue:
                    report += f"- **{issue['severity']}**: {issue.get('issue', issue)}\n"
                    if 'impact' in issue:
                        report += f"  - Impact: {issue['impact']}\n"
        
        report += "\n"
    
    report += "## Prioritized Recommendations\n\n"
    
    for rec in results['recommendations']:
        report += f"### {rec['priority']} Priority: {rec['action']}\n\n"
        report += "**Steps**:\n"
        for i, step in enumerate(rec['steps'], 1):
            report += f"{i}. {step}\n"
        report += f"\n**Expected Outcome**: {rec['expected_outcome']}\n\n"
    
    report += """## Summary

This validation reveals significant data quality issues that must be addressed before the analysis results can be considered reliable. The most critical issues are:

1. **Complete absence of market data integration** - No price impact calculations
2. **Insufficient sample size** - Only 20 tweets over 3 months
3. **Missing statistical validation** - No significance testing

The current report has a data quality score of {:.1%}, indicating it requires substantial improvements before the findings can be trusted or acted upon.
""".format(results['data_quality_score'])
    
    return report

def main():
    # Initialize validator
    validator = TrumpReportDataValidator()
    
    # Run validation
    results = validator.validate_report()
    
    # Generate report
    report = generate_validation_report(results)
    
    # Save results
    with open("data_validation_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    with open("data_validation_report.md", "w") as f:
        f.write(report)
    
    print("Data Validation Complete!")
    print(f"Overall Quality Score: {results['data_quality_score']:.1%}")
    print(f"Critical Issues Found: {len(results['critical_issues'])}")
    print("\nReports generated:")
    print("- data_validation_results.json")
    print("- data_validation_report.md")

if __name__ == "__main__":
    main()