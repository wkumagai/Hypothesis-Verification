#!/usr/bin/env python3
"""
Tesla Stock Price Impact Analysis from Elon Musk's Bullish Tweets
Analyzes correlation between bullish Tesla tweets and subsequent stock price movements
"""

import os
import json
import csv
import time
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Tuple
from dotenv import load_dotenv
import anthropic

# Load environment variables
load_dotenv()

class TweetFetcher:
    """Fetches Elon Musk's tweets using Apify"""
    
    def __init__(self):
        self.api_token = os.getenv('APIFY_API_KEY')
        if not self.api_token:
            raise ValueError("APIFY_API_KEY not found in .env file")
        
        self.actor_id = "CJdippxWmn9uRfooo"
        self.base_url = "https://api.apify.com/v2"
    
    def fetch_tesla_tweets(self, months: int = 12) -> List[Dict[str, Any]]:
        """Fetch Elon Musk's tweets from the past N months"""
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months * 30)
        
        # Input configuration
        input_data = {
            "searchTerms": ["from:elonmusk Tesla OR TSLA OR @Tesla"],
            "twitterHandles": ["elonmusk"],
            "maxTweets": 2000,
            "includeReplies": True,
            "includeRetweets": False,
            "startDate": start_date.strftime("%Y-%m-%d"),
            "endDate": end_date.strftime("%Y-%m-%d"),
            "proxyConfiguration": {
                "useApifyProxy": True
            }
        }
        
        print(f"Fetching Tesla-related tweets from {start_date.date()} to {end_date.date()}")
        
        # Start the actor
        run_url = f"{self.base_url}/acts/{self.actor_id}/runs"
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(run_url, json=input_data, headers=headers)
        response.raise_for_status()
        
        run_info = response.json()
        run_id = run_info['data']['id']
        print(f"Actor run started with ID: {run_id}")
        
        # Wait for completion
        status_url = f"{self.base_url}/acts/{self.actor_id}/runs/{run_id}"
        
        while True:
            response = requests.get(status_url, headers=headers)
            response.raise_for_status()
            
            run_data = response.json()['data']
            status = run_data['status']
            
            if status == 'SUCCEEDED':
                print("Tweet fetching completed!")
                break
            elif status in ['FAILED', 'ABORTED']:
                raise Exception(f"Actor run {status}: {run_data.get('statusMessage', 'Unknown error')}")
            else:
                print(f"Status: {status}... waiting...")
                time.sleep(5)
        
        # Fetch dataset
        dataset_id = run_data['defaultDatasetId']
        dataset_url = f"{self.base_url}/datasets/{dataset_id}/items"
        
        all_tweets = []
        offset = 0
        limit = 100
        
        while True:
            params = {"offset": offset, "limit": limit}
            response = requests.get(dataset_url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            if isinstance(data, list):
                items = data
            else:
                items = data.get('items', [])
            
            if not items:
                break
            
            # Filter for Tesla-related content
            for tweet in items:
                text = tweet.get('text', '').lower()
                if any(keyword in text for keyword in ['tesla', 'tsla', '@tesla', '$tsla']):
                    all_tweets.append(tweet)
            
            offset += len(items)
            print(f"Processed {offset} tweets, found {len(all_tweets)} Tesla-related...")
        
        return all_tweets


class SentimentAnalyzer:
    """Analyzes tweet sentiment using available LLMs"""
    
    def __init__(self):
        # Try to use available LLM APIs
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        
        if self.openai_key:
            self.llm_type = 'openai'
            print("Using OpenAI for sentiment analysis")
        elif self.anthropic_key:
            self.client = anthropic.Anthropic(api_key=self.anthropic_key)
            self.llm_type = 'anthropic'
            print("Using Anthropic Claude for sentiment analysis")
        else:
            raise ValueError("No LLM API keys found in .env")
    
    def classify_sentiment(self, tweet_text: str) -> Tuple[str, float, str]:
        """Classify tweet sentiment as bullish, bearish, or neutral"""
        
        prompt = f"""Analyze the following tweet from Elon Musk about Tesla and classify it as:
1. BULLISH (positive about Tesla's future, products, or performance)
2. BEARISH (negative or cautious about Tesla)
3. NEUTRAL (factual, mixed, or unclear sentiment)

Also provide a confidence score (0-1) and a brief reason.

Tweet: "{tweet_text}"

Respond in JSON format:
{{"sentiment": "BULLISH/BEARISH/NEUTRAL", "confidence": 0.0-1.0, "reason": "brief explanation"}}"""
        
        try:
            if self.llm_type == 'openai':
                from openai import OpenAI
                client = OpenAI(api_key=self.openai_key)
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a financial sentiment analysis expert."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    max_tokens=150
                )
                result = json.loads(response.choices[0].message.content)
                
            elif self.llm_type == 'anthropic':
                response = self.client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=150,
                    temperature=0.1,
                    messages=[{"role": "user", "content": prompt}]
                )
                result = json.loads(response.content[0].text)
            
            return result['sentiment'], result['confidence'], result['reason']
            
        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            # Fallback to simple keyword-based analysis
            bullish_keywords = ['great', 'amazing', 'bullish', 'moon', 'rocket', 'breakthrough', 'record', 'best']
            bearish_keywords = ['problem', 'issue', 'difficult', 'challenge', 'delay', 'recall']
            
            text_lower = tweet_text.lower()
            bullish_score = sum(1 for word in bullish_keywords if word in text_lower)
            bearish_score = sum(1 for word in bearish_keywords if word in text_lower)
            
            if bullish_score > bearish_score:
                return "BULLISH", 0.5, "Keyword-based analysis"
            elif bearish_score > bullish_score:
                return "BEARISH", 0.5, "Keyword-based analysis"
            else:
                return "NEUTRAL", 0.5, "Keyword-based analysis"


class StockDataFetcher:
    """Fetches Tesla stock data using Alpaca API"""
    
    def __init__(self):
        self.api_key = os.getenv('APCA_API_KEY_ID')
        self.api_secret = os.getenv('APCA_API_SECRET_KEY')
        self.base_url = os.getenv('APCA_DATA_ENDPOINT', 'https://data.alpaca.markets')
        
        if not self.api_key or not self.api_secret:
            raise ValueError("Alpaca API credentials not found in .env")
        
        self.session = requests.Session()
        self.session.headers.update({
            'APCA-API-KEY-ID': self.api_key,
            'APCA-API-SECRET-KEY': self.api_secret
        })
    
    def fetch_price_data(self, timestamp: datetime, hours_after: List[int] = [1, 6, 12, 24]) -> Dict[str, Any]:
        """Fetch Tesla stock prices at tweet time and N hours after"""
        
        # Convert to market hours (skip weekends and after-hours)
        tweet_time = timestamp
        if tweet_time.tzinfo is None:
            tweet_time = tweet_time.replace(tzinfo=timezone.utc)
        
        # Get initial price (at tweet time or next market open)
        initial_time = self._get_market_time(tweet_time)
        end_time = initial_time + timedelta(hours=max(hours_after) + 1)
        
        # Fetch minute bars
        url = f"{self.base_url}/v2/stocks/bars"
        params = {
            'symbols': 'TSLA',
            'timeframe': '1Min',
            'start': initial_time.isoformat(),
            'end': end_time.isoformat(),
            'limit': 10000,
            'adjustment': 'raw',
            'feed': 'iex'
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'bars' not in data or 'TSLA' not in data['bars']:
                return None
            
            bars = data['bars']['TSLA']
            if not bars:
                return None
            
            # Get prices at specific intervals
            result = {
                'tweet_time': tweet_time.isoformat(),
                'initial_price': bars[0]['c'],
                'initial_time': bars[0]['t'],
                'prices_after': {}
            }
            
            for hours in hours_after:
                target_time = initial_time + timedelta(hours=hours)
                # Find closest bar
                closest_bar = min(bars, key=lambda x: abs(datetime.fromisoformat(x['t'].replace('Z', '+00:00')) - target_time))
                bar_time = datetime.fromisoformat(closest_bar['t'].replace('Z', '+00:00'))
                
                # Only use if within 30 minutes of target
                if abs((bar_time - target_time).total_seconds()) < 1800:
                    result['prices_after'][f'{hours}h'] = {
                        'price': closest_bar['c'],
                        'time': closest_bar['t'],
                        'change_pct': ((closest_bar['c'] - result['initial_price']) / result['initial_price']) * 100
                    }
            
            return result
            
        except Exception as e:
            print(f"Error fetching stock data: {e}")
            return None
    
    def _get_market_time(self, dt: datetime) -> datetime:
        """Get next market open time from given datetime"""
        # Simplified - assumes US Eastern Time market hours
        # In production, use Alpaca's calendar API
        
        # If weekend, move to Monday
        if dt.weekday() >= 5:  # Saturday = 5, Sunday = 6
            days_ahead = 7 - dt.weekday()
            dt = dt + timedelta(days=days_ahead)
            dt = dt.replace(hour=14, minute=30, second=0)  # 9:30 AM ET in UTC
        
        # If before market open, set to 9:30 AM
        elif dt.hour < 14 or (dt.hour == 14 and dt.minute < 30):
            dt = dt.replace(hour=14, minute=30, second=0)
        
        # If after market close, move to next day
        elif dt.hour >= 21:  # 4 PM ET in UTC
            dt = dt + timedelta(days=1)
            if dt.weekday() >= 5:
                days_ahead = 7 - dt.weekday()
                dt = dt + timedelta(days=days_ahead)
            dt = dt.replace(hour=14, minute=30, second=0)
        
        return dt


def analyze_tweet_impact(tweets: List[Dict], stock_fetcher: StockDataFetcher, sentiment_analyzer: SentimentAnalyzer) -> pd.DataFrame:
    """Analyze stock price impact of bullish tweets"""
    
    results = []
    
    for i, tweet in enumerate(tweets):
        print(f"\nAnalyzing tweet {i+1}/{len(tweets)}...")
        
        # Get tweet details
        tweet_text = tweet.get('text', '')
        tweet_time = tweet.get('createdAt', tweet.get('created_at', ''))
        
        if not tweet_time:
            continue
        
        # Parse timestamp
        try:
            # Handle different timestamp formats
            if 'T' in tweet_time:
                timestamp = datetime.fromisoformat(tweet_time.replace('Z', '+00:00'))
            else:
                # Twitter format: "Tue Jul 29 20:13:56 +0000 2025"
                timestamp = datetime.strptime(tweet_time, '%a %b %d %H:%M:%S +0000 %Y')
                timestamp = timestamp.replace(tzinfo=timezone.utc)
        except Exception as e:
            print(f"Error parsing timestamp: {e}")
            continue
        
        # Analyze sentiment
        sentiment, confidence, reason = sentiment_analyzer.classify_sentiment(tweet_text)
        
        # Only process bullish tweets with high confidence
        if sentiment != 'BULLISH' or confidence < 0.6:
            continue
        
        print(f"Bullish tweet found: {tweet_text[:100]}...")
        
        # Fetch stock data
        stock_data = stock_fetcher.fetch_price_data(timestamp)
        
        if stock_data and stock_data['prices_after']:
            result = {
                'tweet_id': tweet.get('id', ''),
                'tweet_time': timestamp,
                'tweet_text': tweet_text[:200],
                'sentiment': sentiment,
                'confidence': confidence,
                'reason': reason,
                'initial_price': stock_data['initial_price']
            }
            
            # Add price changes
            for interval, data in stock_data['prices_after'].items():
                result[f'price_{interval}'] = data['price']
                result[f'change_{interval}'] = data['change_pct']
            
            results.append(result)
    
    return pd.DataFrame(results)


def create_visualizations(df: pd.DataFrame, output_dir: str):
    """Create charts and visualizations"""
    
    if df.empty:
        print("No data to visualize")
        return
    
    # Set style
    plt.style.use('seaborn-v0_8-darkgrid')
    sns.set_palette("husl")
    
    # 1. Distribution of price changes
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    intervals = ['1h', '6h', '12h', '24h']
    
    for idx, interval in enumerate(intervals):
        ax = axes[idx // 2, idx % 2]
        col = f'change_{interval}'
        
        if col in df.columns:
            df[col].hist(bins=30, ax=ax, alpha=0.7, edgecolor='black')
            ax.axvline(x=0, color='red', linestyle='--', alpha=0.5)
            ax.set_title(f'Price Change Distribution - {interval} After Tweet')
            ax.set_xlabel('Price Change (%)')
            ax.set_ylabel('Frequency')
            
            # Add statistics
            mean_change = df[col].mean()
            median_change = df[col].median()
            ax.text(0.02, 0.98, f'Mean: {mean_change:.2f}%\nMedian: {median_change:.2f}%',
                   transform=ax.transAxes, verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/price_change_distributions.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. Box plots of price changes
    fig, ax = plt.subplots(figsize=(12, 8))
    
    change_cols = [col for col in df.columns if col.startswith('change_')]
    if change_cols:
        change_data = df[change_cols].values
        labels = [col.replace('change_', '') for col in change_cols]
        
        bp = ax.boxplot(change_data, labels=labels, patch_artist=True)
        
        # Color positive/negative differently
        for patch, data in zip(bp['boxes'], change_data.T):
            if np.median(data) > 0:
                patch.set_facecolor('lightgreen')
            else:
                patch.set_facecolor('lightcoral')
        
        ax.axhline(y=0, color='red', linestyle='--', alpha=0.5)
        ax.set_title('Stock Price Changes After Bullish Tweets', fontsize=16)
        ax.set_xlabel('Time After Tweet', fontsize=14)
        ax.set_ylabel('Price Change (%)', fontsize=14)
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/price_change_boxplots.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 3. Time series of tweet impacts
    if len(df) > 1:
        fig, ax = plt.subplots(figsize=(14, 8))
        
        df_sorted = df.sort_values('tweet_time')
        
        for interval in intervals:
            col = f'change_{interval}'
            if col in df_sorted.columns:
                ax.plot(df_sorted['tweet_time'], df_sorted[col], marker='o', label=interval, alpha=0.7)
        
        ax.axhline(y=0, color='red', linestyle='--', alpha=0.5)
        ax.set_title('Stock Price Impact Over Time', fontsize=16)
        ax.set_xlabel('Tweet Date', fontsize=14)
        ax.set_ylabel('Price Change (%)', fontsize=14)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Rotate x labels
        plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/impact_timeline.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 4. Summary statistics bar chart
    fig, ax = plt.subplots(figsize=(10, 8))
    
    stats = []
    for interval in intervals:
        col = f'change_{interval}'
        if col in df.columns:
            stats.append({
                'interval': interval,
                'mean': df[col].mean(),
                'median': df[col].median(),
                'positive_pct': (df[col] > 0).sum() / len(df) * 100
            })
    
    if stats:
        stats_df = pd.DataFrame(stats)
        
        x = np.arange(len(stats_df))
        width = 0.25
        
        ax.bar(x - width, stats_df['mean'], width, label='Mean Change (%)', alpha=0.8)
        ax.bar(x, stats_df['median'], width, label='Median Change (%)', alpha=0.8)
        ax.bar(x + width, stats_df['positive_pct'], width, label='% Positive', alpha=0.8)
        
        ax.set_xlabel('Time After Tweet', fontsize=14)
        ax.set_ylabel('Value', fontsize=14)
        ax.set_title('Summary Statistics of Price Changes', fontsize=16)
        ax.set_xticks(x)
        ax.set_xticklabels(stats_df['interval'])
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/summary_statistics.png', dpi=300, bbox_inches='tight')
    plt.close()


def generate_report(df: pd.DataFrame, output_dir: str):
    """Generate comprehensive analysis report"""
    
    report_path = f'{output_dir}/tesla_sentiment_analysis_report.md'
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# Tesla Stock Price Impact Analysis from Elon Musk's Bullish Tweets\n\n")
        f.write(f"**Analysis Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Period Analyzed**: Past 12 months\n\n")
        f.write(f"**Total Bullish Tweets Analyzed**: {len(df)}\n\n")
        
        f.write("## Executive Summary\n\n")
        
        if not df.empty:
            # Calculate key metrics
            intervals = ['1h', '6h', '12h', '24h']
            
            f.write("### Key Findings\n\n")
            
            for interval in intervals:
                col = f'change_{interval}'
                if col in df.columns:
                    mean_change = df[col].mean()
                    median_change = df[col].median()
                    std_change = df[col].std()
                    positive_pct = (df[col] > 0).sum() / len(df) * 100
                    
                    f.write(f"#### {interval} After Tweet\n")
                    f.write(f"- **Mean Price Change**: {mean_change:+.2f}%\n")
                    f.write(f"- **Median Price Change**: {median_change:+.2f}%\n")
                    f.write(f"- **Standard Deviation**: {std_change:.2f}%\n")
                    f.write(f"- **Positive Outcomes**: {positive_pct:.1f}%\n\n")
            
            # Best and worst outcomes
            f.write("### Notable Outcomes\n\n")
            
            for interval in intervals:
                col = f'change_{interval}'
                if col in df.columns:
                    best_idx = df[col].idxmax()
                    worst_idx = df[col].idxmin()
                    
                    f.write(f"#### {interval} Interval\n")
                    f.write(f"**Best Performance**: {df.loc[best_idx, col]:+.2f}%\n")
                    f.write(f"- Tweet: \"{df.loc[best_idx, 'tweet_text'][:100]}...\"\n")
                    f.write(f"- Date: {df.loc[best_idx, 'tweet_time'].strftime('%Y-%m-%d')}\n\n")
                    
                    f.write(f"**Worst Performance**: {df.loc[worst_idx, col]:+.2f}%\n")
                    f.write(f"- Tweet: \"{df.loc[worst_idx, 'tweet_text'][:100]}...\"\n")
                    f.write(f"- Date: {df.loc[worst_idx, 'tweet_time'].strftime('%Y-%m-%d')}\n\n")
            
            # Statistical significance
            f.write("## Statistical Analysis\n\n")
            
            f.write("### Correlation Matrix\n\n")
            f.write("| Interval | Mean | Median | Std Dev | % Positive | Max | Min |\n")
            f.write("|----------|------|--------|---------|------------|-----|-----|\n")
            
            for interval in intervals:
                col = f'change_{interval}'
                if col in df.columns:
                    f.write(f"| {interval} | {df[col].mean():+.2f}% | {df[col].median():+.2f}% | ")
                    f.write(f"{df[col].std():.2f}% | {(df[col] > 0).sum() / len(df) * 100:.1f}% | ")
                    f.write(f"{df[col].max():+.2f}% | {df[col].min():+.2f}% |\n")
            
            f.write("\n## Methodology\n\n")
            f.write("1. **Data Collection**: Tweets fetched using Apify Twitter Scraper API\n")
            f.write("2. **Sentiment Analysis**: LLM-based classification (bullish/bearish/neutral)\n")
            f.write("3. **Stock Data**: Minute-level data from Alpaca Markets API (IEX feed)\n")
            f.write("4. **Time Intervals**: Price changes measured at 1, 6, 12, and 24 hours post-tweet\n")
            f.write("5. **Market Hours**: Analysis limited to regular trading hours (9:30 AM - 4:00 PM ET)\n\n")
            
            f.write("## Visualizations\n\n")
            f.write("![Price Change Distributions](price_change_distributions.png)\n\n")
            f.write("![Price Change Box Plots](price_change_boxplots.png)\n\n")
            f.write("![Impact Timeline](impact_timeline.png)\n\n")
            f.write("![Summary Statistics](summary_statistics.png)\n\n")
            
            # Sample tweets
            f.write("## Sample Bullish Tweets Analyzed\n\n")
            
            sample_tweets = df.nlargest(5, 'confidence')[['tweet_time', 'tweet_text', 'confidence', 'change_24h']]
            for _, row in sample_tweets.iterrows():
                f.write(f"### {row['tweet_time'].strftime('%Y-%m-%d')}\n")
                f.write(f"**Tweet**: \"{row['tweet_text'][:200]}...\"\n")
                f.write(f"- **Confidence**: {row['confidence']:.2f}\n")
                f.write(f"- **24h Price Change**: {row['change_24h']:+.2f}%\n\n")
            
        else:
            f.write("No bullish tweets found in the analysis period.\n\n")
        
        f.write("## Disclaimer\n\n")
        f.write("This analysis is for educational purposes only and should not be considered ")
        f.write("as financial advice. Past performance does not guarantee future results. ")
        f.write("Multiple factors influence stock prices beyond social media posts.\n")


def main():
    """Main analysis pipeline"""
    
    # Create output directory in the repo
    output_dir = '/Users/kumacmini/Library/CloudStorage/Dropbox/Workspace/Hypothesis-Verification'
    
    print("Starting Tesla Sentiment Impact Analysis...")
    
    # Initialize components
    tweet_fetcher = TweetFetcher()
    sentiment_analyzer = SentimentAnalyzer()
    stock_fetcher = StockDataFetcher()
    
    # Fetch tweets
    print("\n1. Fetching Elon Musk's Tesla-related tweets...")
    tweets = tweet_fetcher.fetch_tesla_tweets(months=12)
    print(f"Found {len(tweets)} Tesla-related tweets")
    
    # Save raw tweets
    with open(f'{output_dir}/raw_tweets.json', 'w', encoding='utf-8') as f:
        json.dump(tweets, f, ensure_ascii=False, indent=2)
    
    # Analyze sentiment and stock impact
    print("\n2. Analyzing sentiment and stock price impact...")
    results_df = analyze_tweet_impact(tweets, stock_fetcher, sentiment_analyzer)
    
    if not results_df.empty:
        # Save results
        results_df.to_csv(f'{output_dir}/analysis_results.csv', index=False)
        print(f"\nAnalyzed {len(results_df)} bullish tweets")
        
        # Create visualizations
        print("\n3. Creating visualizations...")
        create_visualizations(results_df, output_dir)
        
        # Generate report
        print("\n4. Generating comprehensive report...")
        generate_report(results_df, output_dir)
        
        print(f"\nAnalysis complete! Results saved to {output_dir}")
    else:
        print("\nNo bullish tweets found or unable to fetch stock data.")


if __name__ == "__main__":
    main()