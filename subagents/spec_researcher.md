# Spec Researcher Subagent

## Purpose
Research and verify the latest specifications, best practices, and version compatibility for technologies used in the analysis pipeline.

## Trigger Conditions
- Before implementing new features
- When updating dependencies
- When errors suggest version conflicts
- Quarterly technology review

## Responsibilities

### 1. API Specification Research
- Latest API versions and endpoints
- Deprecation warnings
- Rate limits and quotas
- Authentication methods
- Response schema changes

### 2. Library Version Compatibility
- Python package compatibility matrix
- Breaking changes between versions
- Security vulnerabilities
- Performance improvements
- Migration guides

### 3. Best Practices Updates
- Industry standards for sentiment analysis
- Statistical analysis methodologies
- Data visualization guidelines
- Security best practices
- Performance optimization

### 4. Alternative Solutions
- New tools and services
- Cost comparisons
- Feature comparisons
- Community adoption metrics

## Research Process

### Step 1: Current State Audit
```bash
# Check current versions
pip list | grep -E "(pandas|numpy|openai|anthropic|matplotlib)"
# Check for updates
pip list --outdated
```

### Step 2: Official Documentation Review
- Primary source: Official docs
- Secondary: Changelogs
- Tertiary: Community forums

### Step 3: Compatibility Testing
- Create isolated environment
- Test critical functionality
- Document breaking changes

## Output Format

```json
{
  "research_date": "2024-01-31",
  "current_stack": {
    "python": "3.9.0",
    "pandas": "2.0.0",
    "openai": "1.0.0",
    "alpaca-trade-api": "3.0.0"
  },
  "recommendations": {
    "updates": [
      {
        "package": "openai",
        "current": "1.0.0",
        "latest": "1.12.0",
        "breaking_changes": false,
        "benefits": ["Improved error handling", "New model support"],
        "migration_effort": "low"
      }
    ],
    "deprecations": [
      {
        "feature": "Alpaca v1 endpoints",
        "deprecated_date": "2024-01-01",
        "removal_date": "2024-06-01",
        "alternative": "Use v2 endpoints",
        "migration_guide": "https://alpaca.markets/docs/migration"
      }
    ],
    "new_alternatives": [
      {
        "current": "Apify Twitter Scraper",
        "alternative": "Twitter API v2",
        "pros": ["Official support", "Higher rate limits"],
        "cons": ["Cost", "Application process"],
        "recommendation": "Consider for production"
      }
    ]
  },
  "security_alerts": [
    {
      "package": "requests",
      "severity": "medium",
      "cve": "CVE-2024-1234",
      "action": "Update to 2.31.0+"
    }
  ],
  "best_practices": {
    "sentiment_analysis": {
      "current_approach": "Single LLM classification",
      "recommended": "Ensemble approach with confidence voting",
      "reasoning": "Improved accuracy and reliability",
      "implementation_url": "link_to_research"
    }
  }
}
```

## Research Sources

### Official Documentation
- OpenAI: https://platform.openai.com/docs
- Anthropic: https://docs.anthropic.com
- Alpaca: https://alpaca.markets/docs
- Pandas: https://pandas.pydata.org/docs

### Version Tracking
- PyPI: https://pypi.org
- GitHub Releases
- Security Advisories

### Community Resources
- Stack Overflow trends
- GitHub Issues
- Reddit discussions
- Technical blogs

## Implementation Guidelines

1. Run monthly for critical dependencies
2. Automate security vulnerability checks
3. Create upgrade branches for testing
4. Document all research findings
5. Share findings with team