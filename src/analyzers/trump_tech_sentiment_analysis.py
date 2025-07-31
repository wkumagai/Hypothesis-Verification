#!/usr/bin/env python3
"""
Donald Trump X Posts Sentiment Analysis
Analyzes Trump's posts about EV, robotics, AI, and Elon Musk
and their impact on stock prices (Tesla and related tech stocks)
"""

import os
import json
import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
from typing import List, Dict, Tuple, Any
import matplotlib.pyplot as plt
import seaborn as sns
from openai import OpenAI
from anthropic import Anthropic
from dotenv import load_dotenv
import pytz
import re

# Load environment variables
load_dotenv()

class TrumpTechAnalyzer:
    def __init__(self):
        self.apify_key = os.getenv('APIFY_API_KEY')
        self.alpaca_key = os.getenv('ALPACA_API_KEY')
        self.alpaca_secret = os.getenv('ALPACA_SECRET_KEY')
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        
        # Initialize OpenAI client
        self.openai_client = OpenAI(api_key=self.openai_key)
        self.anthropic_client = Anthropic(api_key=self.anthropic_key)
        
        # Keywords to filter relevant posts
        self.tech_keywords = [
            'elon', 'musk', 'tesla', 'ev', 'electric vehicle', 'electric car',
            'ai', 'artificial intelligence', 'robot', 'robotics', 'spacex',
            'autonomous', 'self-driving', 'battery', 'neuralink', 'starlink',
            'cybertruck', 'model 3', 'model s', 'model x', 'model y',
            'gigafactory', 'solar', 'powerwall', 'technology', 'tech'
        ]
        
    def fetch_trump_tweets(self, max_tweets: int = 1000) -> List[Dict]:
        """Fetch Donald Trump's tweets using Apify"""
        print("Fetching Donald Trump's tweets...")
        
        # Note: Trump's Twitter handle varies based on when he was posting
        # @realDonaldTrump was suspended, @DonaldTrump is official
        # We'll try to get posts from Truth Social or any available source
        
        # Use the same actor that worked for Elon tweets
        actor_id = "q3AsRbPSo84VN5zas"
        
        run_input = {
            "handles": ["realDonaldTrump", "DonaldTrump"],
            "tweetsDesired": max_tweets,
            "includeReplies": False,
            "includeRetweets": False,
            "startDate": (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"),
            "endDate": datetime.now().strftime("%Y-%m-%d")
        }
        
        headers = {"Content-Type": "application/json"}
        
        # Start the actor
        run_url = f"https://api.apify.com/v2/acts/{actor_id}/runs?token={self.apify_key}"
        response = requests.post(run_url, json=run_input, headers=headers)
        
        if response.status_code != 201:
            print(f"Error starting actor: {response.text}")
            return []
        
        run_id = response.json()["data"]["id"]
        
        # Wait for completion
        while True:
            status_url = f"https://api.apify.com/v2/actor-runs/{run_id}?token={self.apify_key}"
            status_response = requests.get(status_url)
            status = status_response.json()["data"]["status"]
            
            if status == "SUCCEEDED":
                break
            elif status in ["FAILED", "ABORTED"]:
                print(f"Actor run failed with status: {status}")
                return []
            
            print(f"Status: {status}. Waiting...")
            time.sleep(5)
        
        # Get results
        dataset_id = status_response.json()["data"]["defaultDatasetId"]
        results_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={self.apify_key}"
        results_response = requests.get(results_url)
        
        if results_response.status_code == 200:
            tweets = results_response.json()
            print(f"Successfully fetched {len(tweets)} tweets")
            return tweets
        else:
            print("Failed to fetch results")
            return []
    
    def filter_tech_tweets(self, tweets: List[Dict]) -> List[Dict]:
        """Filter tweets related to tech topics"""
        filtered = []
        
        for tweet in tweets:
            text = tweet.get('text', '').lower()
            if any(keyword in text for keyword in self.tech_keywords):
                filtered.append(tweet)
        
        print(f"Filtered to {len(filtered)} tech-related tweets")
        return filtered
    
    def classify_sentiment_gpt4(self, tweet_text: str) -> Tuple[str, float, str]:
        """Classify sentiment using GPT-4o with temperature=0"""
        prompt = f"""Analyze the following tweet from Donald Trump about technology/Elon Musk and classify it as:
1. BULLISH (positive about the technology, company, or person)
2. BEARISH (negative or critical)
3. NEUTRAL (factual, mixed, or unclear sentiment)

Also provide a confidence score (0-1) and a brief reason.

Tweet: "{tweet_text}"

Respond in JSON format:
{{"sentiment": "BULLISH/BEARISH/NEUTRAL", "confidence": 0.0-1.0, "reason": "brief explanation"}}"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=150
            )
            
            result = json.loads(response.choices[0].message.content)
            return result['sentiment'], result['confidence'], result['reason']
            
        except Exception as e:
            print(f"Error with GPT-4: {e}")
            # Fallback to keyword-based classification
            return self.fallback_classification(tweet_text)
    
    def fallback_classification(self, tweet_text: str) -> Tuple[str, float, str]:
        """Fallback classification based on keywords"""
        text_lower = tweet_text.lower()
        
        bullish_keywords = ['great', 'amazing', 'success', 'wonderful', 'best', 
                           'tremendous', 'fantastic', 'excellent', 'genius', 'smart']
        bearish_keywords = ['bad', 'terrible', 'horrible', 'failure', 'disaster',
                           'wrong', 'fake', 'overrated', 'loser', 'failing']
        
        bullish_score = sum(1 for word in bullish_keywords if word in text_lower)
        bearish_score = sum(1 for word in bearish_keywords if word in text_lower)
        
        if bullish_score > bearish_score:
            return 'BULLISH', 0.5, 'Keyword-based analysis'
        elif bearish_score > bullish_score:
            return 'BEARISH', 0.5, 'Keyword-based analysis'
        else:
            return 'NEUTRAL', 0.5, 'Keyword-based analysis'
    
    def get_stock_data(self, symbol: str, timestamp: datetime, hours_after: List[int]) -> Dict[str, float]:
        """Get stock price data at specific intervals after tweet"""
        base_url = "https://data.alpaca.markets/v2/stocks"
        headers = {
            "APIC-KEY-ID": self.alpaca_key,
            "APIC-SECRET-KEY": self.alpaca_secret
        }
        
        results = {}
        
        # Get price at tweet time
        start = (timestamp - timedelta(minutes=30)).isoformat() + 'Z'
        end = (timestamp + timedelta(minutes=30)).isoformat() + 'Z'
        
        url = f"{base_url}/{symbol}/bars"
        params = {
            "start": start,
            "end": end,
            "timeframe": "1Min",
            "feed": "iex",
            "limit": 100
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()
                if data['bars']:
                    # Find closest bar to tweet time
                    closest_bar = min(data['bars'], 
                                    key=lambda x: abs(datetime.fromisoformat(x['t'].replace('Z', '+00:00')) - timestamp))
                    baseline_price = closest_bar['c']
                    results['baseline'] = baseline_price
                    
                    # Get prices at intervals
                    for hours in hours_after:
                        target_time = timestamp + timedelta(hours=hours)
                        start = (target_time - timedelta(minutes=30)).isoformat() + 'Z'
                        end = (target_time + timedelta(minutes=30)).isoformat() + 'Z'
                        
                        params['start'] = start
                        params['end'] = end
                        
                        response = requests.get(url, headers=headers, params=params)
                        if response.status_code == 200:
                            data = response.json()
                            if data['bars']:
                                closest_bar = min(data['bars'],
                                                key=lambda x: abs(datetime.fromisoformat(x['t'].replace('Z', '+00:00')) - target_time))
                                price = closest_bar['c']
                                change_pct = ((price - baseline_price) / baseline_price) * 100
                                results[f'{hours}h'] = change_pct
                        
                        time.sleep(0.1)  # Rate limiting
            
        except Exception as e:
            print(f"Error fetching stock data: {e}")
        
        return results
    
    def analyze_all_tweets(self, tweets: List[Dict], symbol: str = "TSLA") -> pd.DataFrame:
        """Analyze all tweets and their stock impact"""
        results = []
        
        for i, tweet in enumerate(tweets):
            print(f"Analyzing tweet {i+1}/{len(tweets)}")
            
            # Parse timestamp
            try:
                # Twitter timestamp format
                timestamp = datetime.strptime(tweet['createdAt'], '%a %b %d %H:%M:%S +0000 %Y')
                timestamp = timestamp.replace(tzinfo=pytz.UTC)
            except:
                # Try ISO format
                timestamp = datetime.fromisoformat(tweet['createdAt'].replace('Z', '+00:00'))
            
            # Convert to ET for market hours
            et_tz = pytz.timezone('America/New_York')
            et_time = timestamp.astimezone(et_tz)
            
            # Classify sentiment
            sentiment, confidence, reason = self.classify_sentiment_gpt4(tweet['text'])
            
            # Get stock impact
            stock_changes = self.get_stock_data(symbol, timestamp, [1, 6, 12, 24])
            
            # Determine if during market hours
            market_open = et_time.replace(hour=9, minute=30, second=0, microsecond=0)
            market_close = et_time.replace(hour=16, minute=0, second=0, microsecond=0)
            is_market_hours = market_open <= et_time <= market_close and et_time.weekday() < 5
            
            result = {
                'tweet_id': tweet.get('id', ''),
                'timestamp': timestamp,
                'et_time': et_time,
                'text': tweet['text'],
                'sentiment': sentiment,
                'confidence': confidence,
                'reason': reason,
                'is_market_hours': is_market_hours,
                'retweet_count': tweet.get('retweetCount', 0),
                'like_count': tweet.get('likeCount', 0),
                'engagement': tweet.get('retweetCount', 0) + tweet.get('likeCount', 0)
            }
            
            # Add stock changes
            for key, value in stock_changes.items():
                result[f'price_{key}'] = value
            
            results.append(result)
            time.sleep(0.5)  # Rate limiting
        
        return pd.DataFrame(results)
    
    def create_visualizations(self, df: pd.DataFrame, output_dir: str):
        """Create comprehensive visualizations"""
        plt.style.use('seaborn-v0_8-darkgrid')
        
        # 1. Sentiment distribution
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        sentiment_counts = df['sentiment'].value_counts()
        colors = {'BULLISH': 'green', 'BEARISH': 'red', 'NEUTRAL': 'gray'}
        
        ax1.pie(sentiment_counts.values, labels=sentiment_counts.index, autopct='%1.1f%%',
                colors=[colors.get(s, 'blue') for s in sentiment_counts.index])
        ax1.set_title('Trump Tech Tweet Sentiment Distribution', fontsize=14)
        
        # 2. Average price changes by sentiment
        sentiments = ['BULLISH', 'BEARISH', 'NEUTRAL']
        intervals = ['1h', '6h', '12h', '24h']
        
        avg_changes = []
        for sentiment in sentiments:
            sentiment_data = []
            for interval in intervals:
                col = f'price_{interval}'
                if col in df.columns:
                    avg = df[df['sentiment'] == sentiment][col].dropna().mean()
                    sentiment_data.append(avg if not pd.isna(avg) else 0)
                else:
                    sentiment_data.append(0)
            avg_changes.append(sentiment_data)
        
        x = np.arange(len(intervals))
        width = 0.25
        
        for i, (sentiment, data) in enumerate(zip(sentiments, avg_changes)):
            ax2.bar(x + i*width, data, width, label=sentiment, color=colors.get(sentiment, 'blue'))
        
        ax2.set_xlabel('Time After Tweet', fontsize=12)
        ax2.set_ylabel('Average Price Change (%)', fontsize=12)
        ax2.set_title('Stock Price Impact by Sentiment', fontsize=14)
        ax2.set_xticks(x + width)
        ax2.set_xticklabels(intervals)
        ax2.legend()
        ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/trump_sentiment_overview.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 3. Time series of tweets and sentiment
        fig, ax = plt.subplots(figsize=(14, 8))
        
        for sentiment in sentiments:
            sentiment_df = df[df['sentiment'] == sentiment]
            ax.scatter(sentiment_df['timestamp'], sentiment_df.get('price_24h', 0),
                      label=sentiment, color=colors.get(sentiment, 'blue'), alpha=0.6, s=100)
        
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('24h Price Change (%)', fontsize=12)
        ax.set_title('Trump Tech Tweets: Sentiment and Stock Impact Over Time', fontsize=14)
        ax.legend()
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax.grid(True, alpha=0.3)
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f'{output_dir}/trump_sentiment_timeline.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 4. Engagement vs Impact
        fig, ax = plt.subplots(figsize=(10, 8))
        
        for sentiment in sentiments:
            sentiment_df = df[df['sentiment'] == sentiment]
            if 'price_24h' in sentiment_df.columns:
                ax.scatter(sentiment_df['engagement'], sentiment_df['price_24h'],
                          label=sentiment, color=colors.get(sentiment, 'blue'), alpha=0.6, s=100)
        
        ax.set_xlabel('Total Engagement (Likes + Retweets)', fontsize=12)
        ax.set_ylabel('24h Price Change (%)', fontsize=12)
        ax.set_title('Tweet Engagement vs Stock Impact', fontsize=14)
        ax.legend()
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/trump_engagement_impact.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def generate_report(self, df: pd.DataFrame, output_dir: str):
        """Generate comprehensive report"""
        report_path = f'{output_dir}/trump_tech_sentiment_report.md'
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# Donald Trump Tech & Elon Musk Sentiment Analysis Report\n\n")
            f.write(f"**Analysis Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Total Tweets Analyzed**: {len(df)}\n")
            f.write(f"**Time Period**: {df['timestamp'].min()} to {df['timestamp'].max()}\n\n")
            
            # Sentiment distribution
            f.write("## Sentiment Distribution\n\n")
            sentiment_counts = df['sentiment'].value_counts()
            total = len(df)
            
            f.write("| Sentiment | Count | Percentage |\n")
            f.write("|-----------|-------|------------|\n")
            for sentiment, count in sentiment_counts.items():
                f.write(f"| {sentiment} | {count} | {count/total*100:.1f}% |\n")
            f.write("\n")
            
            # Average stock impact by sentiment
            f.write("## Average Stock Price Impact by Sentiment\n\n")
            f.write("| Sentiment | 1h Change | 6h Change | 12h Change | 24h Change |\n")
            f.write("|-----------|-----------|-----------|------------|------------|\n")
            
            for sentiment in ['BULLISH', 'BEARISH', 'NEUTRAL']:
                sentiment_df = df[df['sentiment'] == sentiment]
                row = f"| {sentiment} |"
                for interval in ['1h', '6h', '12h', '24h']:
                    col = f'price_{interval}'
                    if col in df.columns:
                        avg = sentiment_df[col].dropna().mean()
                        row += f" {avg:.2f}% |" if not pd.isna(avg) else " N/A |"
                    else:
                        row += " N/A |"
                f.write(row + "\n")
            f.write("\n")
            
            # Top positive impact tweets
            f.write("## Top 5 Positive Impact Tweets (24h)\n\n")
            if 'price_24h' in df.columns:
                top_positive = df.nlargest(5, 'price_24h')
                for _, tweet in top_positive.iterrows():
                    f.write(f"**+{tweet['price_24h']:.2f}%** ({tweet['sentiment']}):\n")
                    f.write(f"> {tweet['text'][:200]}...\n")
                    f.write(f"*{tweet['timestamp']}*\n\n")
            
            # Top negative impact tweets
            f.write("## Top 5 Negative Impact Tweets (24h)\n\n")
            if 'price_24h' in df.columns:
                top_negative = df.nsmallest(5, 'price_24h')
                for _, tweet in top_negative.iterrows():
                    f.write(f"**{tweet['price_24h']:.2f}%** ({tweet['sentiment']}):\n")
                    f.write(f"> {tweet['text'][:200]}...\n")
                    f.write(f"*{tweet['timestamp']}*\n\n")
            
            # Market hours analysis
            f.write("## Market Hours vs After Hours Impact\n\n")
            market_hours_df = df[df['is_market_hours'] == True]
            after_hours_df = df[df['is_market_hours'] == False]
            
            f.write("| Time Period | Count | Avg 24h Change |\n")
            f.write("|-------------|-------|----------------|\n")
            
            if 'price_24h' in df.columns:
                mh_avg = market_hours_df['price_24h'].dropna().mean()
                ah_avg = after_hours_df['price_24h'].dropna().mean()
                f.write(f"| Market Hours | {len(market_hours_df)} | {mh_avg:.2f}% |\n")
                f.write(f"| After Hours | {len(after_hours_df)} | {ah_avg:.2f}% |\n")
            f.write("\n")
            
            # Engagement analysis
            f.write("## Engagement Metrics\n\n")
            f.write("| Sentiment | Avg Likes | Avg Retweets | Avg Total Engagement |\n")
            f.write("|-----------|-----------|--------------|---------------------|\n")
            
            for sentiment in ['BULLISH', 'BEARISH', 'NEUTRAL']:
                sentiment_df = df[df['sentiment'] == sentiment]
                avg_likes = sentiment_df['like_count'].mean()
                avg_retweets = sentiment_df['retweet_count'].mean()
                avg_engagement = sentiment_df['engagement'].mean()
                f.write(f"| {sentiment} | {avg_likes:.0f} | {avg_retweets:.0f} | {avg_engagement:.0f} |\n")
            
            f.write("\n## Methodology\n\n")
            f.write("- **Sentiment Classification**: GPT-4o with temperature=0\n")
            f.write("- **Stock Data**: Alpaca Market Data API (IEX feed)\n")
            f.write("- **Tweet Source**: Apify Twitter Scraper\n")
            f.write("- **Analysis Period**: Past 12 months\n")
            f.write("- **Keywords**: EV, robotics, AI, Elon Musk, Tesla, and related terms\n")

def main():
    output_dir = '/Users/kumacmini/Library/CloudStorage/Dropbox/Workspace/Hypothesis-Verification'
    
    analyzer = TrumpTechAnalyzer()
    
    # Fetch tweets
    print("Starting Donald Trump tech tweet analysis...")
    tweets = analyzer.fetch_trump_tweets(max_tweets=500)
    
    if not tweets:
        print("No tweets fetched. Exiting.")
        return
    
    # Save raw tweets
    with open(f'{output_dir}/trump_raw_tweets.json', 'w', encoding='utf-8') as f:
        json.dump(tweets, f, ensure_ascii=False, indent=2)
    
    # Filter for tech-related tweets
    tech_tweets = analyzer.filter_tech_tweets(tweets)
    
    if not tech_tweets:
        print("No tech-related tweets found. Exiting.")
        return
    
    # Analyze tweets
    df = analyzer.analyze_all_tweets(tech_tweets)
    
    # Save analysis results
    df.to_csv(f'{output_dir}/trump_tech_analysis.csv', index=False)
    
    # Create visualizations
    print("Creating visualizations...")
    analyzer.create_visualizations(df, output_dir)
    
    # Generate report
    print("Generating report...")
    analyzer.generate_report(df, output_dir)
    
    print("Analysis complete!")

if __name__ == "__main__":
    main()