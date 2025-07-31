# Market Context Subagent

## Purpose
Provide comprehensive market context for the time period being analyzed to identify external factors affecting stock movements.

## Trigger Conditions
- Before analyzing stock price impacts
- When unusual price movements are detected
- For comprehensive report generation

## Responsibilities

### 1. Market Events Research
- Major market indices performance (S&P 500, NASDAQ, etc.)
- Sector-specific movements
- Trading volume anomalies
- Market volatility indicators (VIX)

### 2. Company-Specific Events
- Earnings announcements
- Product launches
- Executive changes
- Regulatory filings
- Competitor actions

### 3. Macro Economic Factors
- Federal Reserve announcements
- Economic indicators releases
- Geopolitical events
- Industry-specific news

### 4. Social Media Trends
- Viral events related to the company
- Trending hashtags
- Influencer mentions beyond target accounts
- General sentiment shifts

## Research Process

1. **Time Window Definition**
   - 48 hours before first post
   - Entire analysis period
   - 48 hours after last post

2. **Data Sources**
   - Financial news APIs
   - Market data providers
   - Social media trend analysis
   - Economic calendar

3. **Impact Assessment**
   - Rate each event's potential impact (High/Medium/Low)
   - Identify correlation with observed price movements
   - Flag confounding variables

## Output Format

```json
{
  "analysis_period": {
    "start": "2024-01-01",
    "end": "2024-01-31"
  },
  "market_context": {
    "general_trend": "bullish",
    "sp500_change": "+2.5%",
    "nasdaq_change": "+3.1%",
    "sector_performance": "Technology +4.2%"
  },
  "significant_events": [
    {
      "date": "2024-01-15",
      "type": "earnings",
      "description": "Tesla Q4 earnings beat expectations",
      "impact": "high",
      "price_movement": "+8.5%"
    },
    {
      "date": "2024-01-20",
      "type": "fed_announcement",
      "description": "Fed maintains interest rates",
      "impact": "medium",
      "market_reaction": "positive"
    }
  ],
  "confounding_factors": [
    "Earnings announcement coincided with Musk tweets",
    "Broad tech sector rally during analysis period"
  ],
  "context_summary": "Analysis period showed strong tech sector performance with multiple positive catalysts beyond social media influence."
}
```

## Implementation Guidelines

1. Cache market context data to avoid repeated API calls
2. Generate visual timeline of events
3. Highlight overlapping influences
4. Provide confidence levels for attribution
5. Include in final analysis reports