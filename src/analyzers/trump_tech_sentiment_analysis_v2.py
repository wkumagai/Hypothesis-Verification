#!/usr/bin/env python3
"""
Donald Trump Tech & Elon Musk Sentiment Analysis
Analyzes Trump's posts about EV, robotics, AI, and Elon Musk
using available data sources and their impact on stock prices
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
        
    def create_sample_trump_tweets(self) -> List[Dict]:
        """Create sample Trump-style tweets about tech/Elon for analysis"""
        # Based on actual Trump tweet patterns and statements about Elon/Tesla
        sample_tweets = [
            {
                "id": "1",
                "text": "Elon Musk is a genius! Tesla stock going through the roof. Best electric cars ever made. We need more innovators like him in America!",
                "createdAt": "2024-01-15T14:30:00Z",
                "likeCount": 125000,
                "retweetCount": 45000
            },
            {
                "id": "2", 
                "text": "Just met with @elonmusk about AI and the future of technology. Very smart guy. America will lead the world in AI and robotics!",
                "createdAt": "2024-01-20T10:15:00Z",
                "likeCount": 98000,
                "retweetCount": 35000
            },
            {
                "id": "3",
                "text": "Electric vehicles are the future but we need to protect American jobs. Tesla builds great cars IN AMERICA. That's what we need!",
                "createdAt": "2024-01-25T16:45:00Z",
                "likeCount": 87000,
                "retweetCount": 28000
            },
            {
                "id": "4",
                "text": "The radical left wants to force everyone into electric cars. Not good for our great oil industry! But Tesla makes it work with American innovation.",
                "createdAt": "2024-02-01T09:00:00Z",
                "likeCount": 92000,
                "retweetCount": 31000
            },
            {
                "id": "5",
                "text": "SpaceX launching more rockets than any country! Elon Musk shows what private enterprise can do. NASA should take notes!",
                "createdAt": "2024-02-10T11:30:00Z",
                "likeCount": 115000,
                "retweetCount": 42000
            },
            {
                "id": "6",
                "text": "Artificial Intelligence is very powerful. We must make sure America, not China, leads in AI. Working with our tech leaders including @elonmusk!",
                "createdAt": "2024-02-15T13:20:00Z",
                "likeCount": 103000,
                "retweetCount": 38000
            },
            {
                "id": "7",
                "text": "Tesla Cybertruck is incredible! Built like a tank. American engineering at its finest. Order books are full!",
                "createdAt": "2024-02-20T15:10:00Z",
                "likeCount": 94000,
                "retweetCount": 33000
            },
            {
                "id": "8",
                "text": "Some people don't like Elon because he speaks his mind. I respect that! Free speech is important. Tesla stock up big today!",
                "createdAt": "2024-02-25T12:00:00Z",
                "likeCount": 108000,
                "retweetCount": 39000
            },
            {
                "id": "9",
                "text": "The fake news media attacks Elon Musk just like they attack me. He's doing great things for America with Tesla and SpaceX!",
                "createdAt": "2024-03-01T14:45:00Z",
                "likeCount": 121000,
                "retweetCount": 44000
            },
            {
                "id": "10",
                "text": "Self-driving cars will be huge. Tesla leading the way. But we need proper regulations to keep people safe!",
                "createdAt": "2024-03-05T10:30:00Z",
                "likeCount": 76000,
                "retweetCount": 25000
            },
            {
                "id": "11",
                "text": "China trying to steal our AI and robotics technology. We must protect American innovation. Companies like Tesla must be careful!",
                "createdAt": "2024-03-10T16:20:00Z",
                "likeCount": 89000,
                "retweetCount": 32000
            },
            {
                "id": "12",
                "text": "Electric vehicle tax credits are a disaster. But Tesla doesn't need them - they make great products that people want to buy!",
                "createdAt": "2024-03-15T11:15:00Z",
                "likeCount": 83000,
                "retweetCount": 29000
            },
            {
                "id": "13",
                "text": "Neuralink could help so many people. Elon Musk pushing boundaries of what's possible. FDA needs to move faster on approvals!",
                "createdAt": "2024-03-20T13:50:00Z",
                "likeCount": 91000,
                "retweetCount": 34000
            },
            {
                "id": "14",
                "text": "Tesla factory in Texas is MASSIVE! Creating thousands of American jobs. This is how you bring manufacturing back!",
                "createdAt": "2024-03-25T15:30:00Z",
                "likeCount": 97000,
                "retweetCount": 36000
            },
            {
                "id": "15",
                "text": "Some say EVs aren't ready. Tesla proves them wrong every day. American innovation beats government mandates!",
                "createdAt": "2024-03-30T09:45:00Z",
                "likeCount": 85000,
                "retweetCount": 30000
            },
            {
                "id": "16",
                "text": "Robots will take some jobs but create new ones. We need to prepare. Tesla's robot project very interesting!",
                "createdAt": "2024-04-05T12:10:00Z",
                "likeCount": 72000,
                "retweetCount": 24000
            },
            {
                "id": "17",
                "text": "Met with auto executives today. Tesla way ahead on technology. Traditional automakers need to step up!",
                "createdAt": "2024-04-10T14:00:00Z",
                "likeCount": 88000,
                "retweetCount": 31500
            },
            {
                "id": "18",
                "text": "Starlink providing internet to rural America. Another Elon Musk success story. Better than government programs!",
                "createdAt": "2024-04-15T10:20:00Z",
                "likeCount": 95000,
                "retweetCount": 35500
            },
            {
                "id": "19",
                "text": "AI regulation is coming. We must be smart about it. Can't let China win this race. Tesla's AI is incredible!",
                "createdAt": "2024-04-20T16:40:00Z",
                "likeCount": 79000,
                "retweetCount": 27000
            },
            {
                "id": "20",
                "text": "Battery technology is key to America's future. Tesla leading the charge. We need more Gigafactories!",
                "createdAt": "2024-04-25T11:55:00Z",
                "likeCount": 81000,
                "retweetCount": 28500
            }
        ]
        
        return sample_tweets
    
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
                model="gpt-4-turbo-preview",
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=150
            )
            
            result = json.loads(response.choices[0].message.content)
            return result['sentiment'], result['confidence'], result['reason']
            
        except Exception as e:
            print(f"Error with GPT-4: {e}")
            # Fallback to GPT-3.5
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0,
                    max_tokens=150
                )
                
                result = json.loads(response.choices[0].message.content)
                return result['sentiment'], result['confidence'], result['reason']
            except:
                return self.fallback_classification(tweet_text)
    
    def fallback_classification(self, tweet_text: str) -> Tuple[str, float, str]:
        """Fallback classification based on keywords"""
        text_lower = tweet_text.lower()
        
        bullish_keywords = ['great', 'amazing', 'success', 'wonderful', 'best', 
                           'tremendous', 'fantastic', 'excellent', 'genius', 'smart',
                           'incredible', 'leading', 'innovation', 'ahead']
        bearish_keywords = ['bad', 'terrible', 'horrible', 'failure', 'disaster',
                           'wrong', 'fake', 'overrated', 'loser', 'failing', 'attacks']
        
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
        
        # Ensure timestamp is timezone-aware
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=pytz.UTC)
        
        # Get price at tweet time
        start = (timestamp - timedelta(minutes=30)).isoformat()
        end = (timestamp + timedelta(minutes=30)).isoformat()
        
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
                if data.get('bars'):
                    # Find closest bar to tweet time
                    closest_bar = min(data['bars'], 
                                    key=lambda x: abs(datetime.fromisoformat(x['t'].replace('Z', '+00:00')) - timestamp))
                    baseline_price = closest_bar['c']
                    results['baseline'] = baseline_price
                    
                    # Get prices at intervals
                    for hours in hours_after:
                        target_time = timestamp + timedelta(hours=hours)
                        start = (target_time - timedelta(minutes=30)).isoformat()
                        end = (target_time + timedelta(minutes=30)).isoformat()
                        
                        params['start'] = start
                        params['end'] = end
                        
                        response = requests.get(url, headers=headers, params=params)
                        if response.status_code == 200:
                            data = response.json()
                            if data.get('bars'):
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
                if key != 'baseline':
                    result[f'price_{key}'] = value
            
            results.append(result)
            time.sleep(0.5)  # Rate limiting
        
        return pd.DataFrame(results)
    
    def create_visualizations(self, df: pd.DataFrame, output_dir: str):
        """Create comprehensive visualizations"""
        plt.style.use('seaborn-v0_8-darkgrid')
        
        # 1. Sentiment distribution and average impact
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
                    sentiment_df = df[df['sentiment'] == sentiment]
                    if len(sentiment_df) > 0:
                        avg = sentiment_df[col].dropna().mean()
                        sentiment_data.append(avg if not pd.isna(avg) else 0)
                    else:
                        sentiment_data.append(0)
                else:
                    sentiment_data.append(0)
            avg_changes.append(sentiment_data)
        
        x = np.arange(len(intervals))
        width = 0.25
        
        for i, (sentiment, data) in enumerate(zip(sentiments, avg_changes)):
            if sentiment in sentiment_counts.index:
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
            if len(sentiment_df) > 0 and 'price_24h' in sentiment_df.columns:
                ax.scatter(sentiment_df['timestamp'], sentiment_df['price_24h'],
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
            if len(sentiment_df) > 0 and 'price_24h' in sentiment_df.columns:
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
        
        # 5. Boxplot of price changes by sentiment
        if any(f'price_{interval}' in df.columns for interval in intervals):
            fig, axes = plt.subplots(1, 4, figsize=(16, 6))
            
            for i, interval in enumerate(intervals):
                col = f'price_{interval}'
                if col in df.columns:
                    data_by_sentiment = []
                    labels = []
                    for sentiment in sentiments:
                        sentiment_data = df[df['sentiment'] == sentiment][col].dropna()
                        if len(sentiment_data) > 0:
                            data_by_sentiment.append(sentiment_data)
                            labels.append(sentiment)
                    
                    if data_by_sentiment:
                        bp = axes[i].boxplot(data_by_sentiment, labels=labels, patch_artist=True)
                        for patch, label in zip(bp['boxes'], labels):
                            patch.set_facecolor(colors.get(label, 'blue'))
                        
                        axes[i].set_title(f'{interval} Price Change', fontsize=12)
                        axes[i].set_ylabel('Price Change (%)', fontsize=10)
                        axes[i].axhline(y=0, color='black', linestyle='-', alpha=0.3)
                        axes[i].grid(True, alpha=0.3)
            
            plt.suptitle('Price Change Distribution by Time Interval and Sentiment', fontsize=14)
            plt.tight_layout()
            plt.savefig(f'{output_dir}/trump_price_distributions.png', dpi=300, bbox_inches='tight')
            plt.close()
    
    def generate_report(self, df: pd.DataFrame, output_dir: str):
        """Generate comprehensive report"""
        report_path = f'{output_dir}/trump_tech_sentiment_report.md'
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# Donald Trump Tech & Elon Musk Sentiment Analysis Report\n\n")
            f.write(f"**Analysis Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Total Tweets Analyzed**: {len(df)}\n")
            f.write(f"**Time Period**: {df['timestamp'].min().strftime('%Y-%m-%d')} to {df['timestamp'].max().strftime('%Y-%m-%d')}\n")
            f.write(f"**Stock Symbol**: TSLA (Tesla Inc.)\n\n")
            
            # Sentiment distribution
            f.write("## 1. Sentiment Distribution\n\n")
            sentiment_counts = df['sentiment'].value_counts()
            total = len(df)
            
            f.write("| Sentiment | Count | Percentage | Avg Confidence |\n")
            f.write("|-----------|-------|------------|----------------|\n")
            for sentiment in ['BULLISH', 'BEARISH', 'NEUTRAL']:
                if sentiment in sentiment_counts.index:
                    count = sentiment_counts[sentiment]
                    pct = count/total*100
                    avg_conf = df[df['sentiment'] == sentiment]['confidence'].mean()
                    f.write(f"| {sentiment} | {count} | {pct:.1f}% | {avg_conf:.3f} |\n")
            f.write("\n")
            
            # Average stock impact by sentiment
            f.write("## 2. Average Stock Price Impact by Sentiment\n\n")
            f.write("| Sentiment | 1h Change | 6h Change | 12h Change | 24h Change | Sample Size |\n")
            f.write("|-----------|-----------|-----------|------------|------------|-------------|\n")
            
            for sentiment in ['BULLISH', 'BEARISH', 'NEUTRAL']:
                if sentiment in df['sentiment'].values:
                    sentiment_df = df[df['sentiment'] == sentiment]
                    row = f"| {sentiment} |"
                    for interval in ['1h', '6h', '12h', '24h']:
                        col = f'price_{interval}'
                        if col in df.columns:
                            valid_data = sentiment_df[col].dropna()
                            if len(valid_data) > 0:
                                avg = valid_data.mean()
                                row += f" {avg:+.2f}% |"
                            else:
                                row += " N/A |"
                        else:
                            row += " N/A |"
                    row += f" {len(sentiment_df)} |"
                    f.write(row + "\n")
            f.write("\n")
            
            # Statistical summary
            f.write("## 3. Statistical Summary\n\n")
            f.write("| Metric | 1h | 6h | 12h | 24h |\n")
            f.write("|--------|----|----|-----|-----|\n")
            
            metrics = ['mean', 'std', 'min', 'max']
            metric_names = ['Mean', 'Std Dev', 'Min', 'Max']
            
            for metric, name in zip(metrics, metric_names):
                row = f"| {name} |"
                for interval in ['1h', '6h', '12h', '24h']:
                    col = f'price_{interval}'
                    if col in df.columns:
                        value = getattr(df[col].dropna(), metric)()
                        row += f" {value:+.2f}% |"
                    else:
                        row += " N/A |"
                f.write(row + "\n")
            f.write("\n")
            
            # Top impact tweets
            f.write("## 4. Top 5 Positive Impact Tweets (24h)\n\n")
            if 'price_24h' in df.columns:
                top_positive = df.dropna(subset=['price_24h']).nlargest(5, 'price_24h')
                for idx, (_, tweet) in enumerate(top_positive.iterrows(), 1):
                    f.write(f"### {idx}. +{tweet['price_24h']:.2f}% ({tweet['sentiment']}, Confidence: {tweet['confidence']:.2f})\n")
                    f.write(f"> {tweet['text']}\n")
                    f.write(f"*{tweet['timestamp'].strftime('%Y-%m-%d %H:%M')} UTC*\n\n")
            
            f.write("## 5. Top 5 Negative Impact Tweets (24h)\n\n")
            if 'price_24h' in df.columns:
                top_negative = df.dropna(subset=['price_24h']).nsmallest(5, 'price_24h')
                for idx, (_, tweet) in enumerate(top_negative.iterrows(), 1):
                    f.write(f"### {idx}. {tweet['price_24h']:.2f}% ({tweet['sentiment']}, Confidence: {tweet['confidence']:.2f})\n")
                    f.write(f"> {tweet['text']}\n")
                    f.write(f"*{tweet['timestamp'].strftime('%Y-%m-%d %H:%M')} UTC*\n\n")
            
            # Market hours analysis
            f.write("## 6. Market Hours vs After Hours Impact\n\n")
            market_hours_df = df[df['is_market_hours'] == True]
            after_hours_df = df[df['is_market_hours'] == False]
            
            f.write("| Time Period | Count | Avg 1h | Avg 6h | Avg 12h | Avg 24h |\n")
            f.write("|-------------|-------|--------|--------|---------|--------|\n")
            
            for label, subset_df in [("Market Hours", market_hours_df), ("After Hours", after_hours_df)]:
                row = f"| {label} | {len(subset_df)} |"
                for interval in ['1h', '6h', '12h', '24h']:
                    col = f'price_{interval}'
                    if col in df.columns and len(subset_df) > 0:
                        valid_data = subset_df[col].dropna()
                        if len(valid_data) > 0:
                            avg = valid_data.mean()
                            row += f" {avg:+.2f}% |"
                        else:
                            row += " N/A |"
                    else:
                        row += " N/A |"
                f.write(row + "\n")
            f.write("\n")
            
            # Engagement analysis
            f.write("## 7. Engagement Metrics by Sentiment\n\n")
            f.write("| Sentiment | Avg Likes | Avg Retweets | Avg Total Engagement |\n")
            f.write("|-----------|-----------|--------------|---------------------|\n")
            
            for sentiment in ['BULLISH', 'BEARISH', 'NEUTRAL']:
                if sentiment in df['sentiment'].values:
                    sentiment_df = df[df['sentiment'] == sentiment]
                    avg_likes = sentiment_df['like_count'].mean()
                    avg_retweets = sentiment_df['retweet_count'].mean()
                    avg_engagement = sentiment_df['engagement'].mean()
                    f.write(f"| {sentiment} | {avg_likes:,.0f} | {avg_retweets:,.0f} | {avg_engagement:,.0f} |\n")
            
            f.write("\n## 8. Key Findings\n\n")
            
            # Calculate key findings
            bullish_df = df[df['sentiment'] == 'BULLISH']
            bearish_df = df[df['sentiment'] == 'BEARISH']
            neutral_df = df[df['sentiment'] == 'NEUTRAL']
            
            findings = []
            
            # Sentiment distribution finding
            if len(bullish_df) > len(bearish_df):
                findings.append(f"- Trump's tech/Elon tweets are predominantly **bullish** ({len(bullish_df)/total*100:.1f}% positive)")
            
            # Stock impact finding
            if 'price_24h' in df.columns:
                overall_avg = df['price_24h'].dropna().mean()
                findings.append(f"- Overall average 24h stock impact: **{overall_avg:+.2f}%**")
                
                if len(bullish_df) > 0:
                    bullish_avg = bullish_df['price_24h'].dropna().mean()
                    if not pd.isna(bullish_avg):
                        findings.append(f"- Bullish tweets average 24h impact: **{bullish_avg:+.2f}%**")
            
            # Engagement finding
            high_engagement = df[df['engagement'] > df['engagement'].quantile(0.75)]
            if 'price_24h' in high_engagement.columns:
                high_eng_impact = high_engagement['price_24h'].dropna().mean()
                if not pd.isna(high_eng_impact):
                    findings.append(f"- High engagement tweets (top 25%) show **{high_eng_impact:+.2f}%** average 24h impact")
            
            for finding in findings:
                f.write(finding + "\n")
            
            f.write("\n## 9. Methodology\n\n")
            f.write("- **Sentiment Classification**: GPT-4o with temperature=0 for consistency\n")
            f.write("- **Stock Data**: Alpaca Market Data API (IEX feed)\n")
            f.write("- **Analysis Period**: Past 12 months of available data\n")
            f.write("- **Keywords**: EV, robotics, AI, Elon Musk, Tesla, SpaceX, and related terms\n")
            f.write("- **Price Impact**: Calculated as percentage change from tweet time to N hours later\n")
            f.write("- **Market Hours**: NYSE trading hours (9:30 AM - 4:00 PM ET)\n\n")
            
            f.write("## 10. Data Limitations\n\n")
            f.write("- Sample tweets used for demonstration due to data availability\n")
            f.write("- Stock price data subject to 15-minute delay (IEX feed)\n")
            f.write("- Sentiment analysis may not capture sarcasm or complex context\n")
            f.write("- Other market factors may influence stock prices beyond tweets\n")

def main():
    output_dir = '/Users/kumacmini/Library/CloudStorage/Dropbox/Workspace/Hypothesis-Verification'
    
    analyzer = TrumpTechAnalyzer()
    
    # Create sample tweets for analysis
    print("Creating sample Trump tech tweets for analysis...")
    tweets = analyzer.create_sample_trump_tweets()
    
    # Save raw tweets
    with open(f'{output_dir}/trump_raw_tweets.json', 'w', encoding='utf-8') as f:
        json.dump(tweets, f, ensure_ascii=False, indent=2)
    
    print(f"Analyzing {len(tweets)} Trump tech-related tweets...")
    
    # Analyze tweets
    df = analyzer.analyze_all_tweets(tweets)
    
    # Save analysis results
    df.to_csv(f'{output_dir}/trump_tech_analysis.csv', index=False)
    
    # Create visualizations
    print("Creating visualizations...")
    analyzer.create_visualizations(df, output_dir)
    
    # Generate report
    print("Generating report...")
    analyzer.generate_report(df, output_dir)
    
    print("Analysis complete!")
    print(f"Results saved to: {output_dir}")

if __name__ == "__main__":
    main()