# Data Validator Subagent

## Purpose
Validate and verify data quality before running hypothesis verification experiments.

## Trigger Conditions
- Before any analysis when new data is loaded
- When data sources change
- When anomalies are detected in results

## Responsibilities

### 1. Data Completeness Check
- Verify all required fields are present
- Check for missing values and their patterns
- Validate date ranges match expectations
- Ensure minimum sample size requirements

### 2. Data Quality Validation
- Check for duplicate entries
- Validate timestamp formats and timezone consistency
- Verify numeric values are within reasonable ranges
- Detect outliers using statistical methods

### 3. API Data Verification
- Confirm API responses match expected schema
- Validate rate limiting compliance
- Check for API deprecation warnings
- Verify data freshness (not stale cache)

### 4. Cross-Reference Validation
- Match social media posts with available market data
- Verify stock symbols are valid and active
- Check market hours alignment
- Validate sentiment classification completeness

## Output Format

```json
{
  "validation_status": "passed|failed|warning",
  "timestamp": "2024-01-31T10:00:00Z",
  "checks": {
    "completeness": {
      "status": "passed",
      "missing_records": 0,
      "coverage": "100%"
    },
    "quality": {
      "status": "warning",
      "issues": ["5 duplicate tweets detected"],
      "outliers": 2
    },
    "api_data": {
      "status": "passed",
      "freshness": "real-time",
      "schema_valid": true
    },
    "cross_reference": {
      "status": "passed",
      "matched_records": 450,
      "unmatched": 3
    }
  },
  "recommendations": [
    "Remove duplicate tweets before analysis",
    "Investigate 2 outlier price movements"
  ]
}
```

## Implementation Guidelines

1. Run automatically before each analysis
2. Log all validation results for audit trail
3. Halt analysis on critical failures
4. Provide actionable recommendations
5. Generate validation report in results directory