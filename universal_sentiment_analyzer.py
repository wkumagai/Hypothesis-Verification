#!/usr/bin/env python3
"""
Universal Sentiment Analyzer
Works with any social media platform and stock data based on configuration
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

# Load environment variables
load_dotenv()

class UniversalSentimentAnalyzer:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.apify_key = os.getenv('APIFY_API_KEY')
        self.alpaca_key = os.getenv('ALPACA_API_KEY')
        self.alpaca_secret = os.getenv('ALPACA_SECRET_KEY')
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        
        # Initialize LLM clients
        if config['sentiment']['provider'] == 'openai':
            self.openai_client = OpenAI(api_key=self.openai_key)
        elif config['sentiment']['provider'] == 'anthropic':
            self.anthropic_client = Anthropic(api_key=self.anthropic_key)
    
    def run_analysis(self) -> Dict[str, Any]:
        """Run the complete analysis pipeline"""
        results = {
            'posts': [],
            'analysis': [],
            'sentiment_distribution': {},
            'price_impacts': {},
            'metadata': {
                'start_time': datetime.now(),
                'config': self.config
            }
        }
        
        # Fetch posts
        print("Fetching social media posts...")
        posts = self.fetch_posts()
        results['posts'] = posts
        
        if not posts:
            print("No posts found!")
            return results
        
        # Filter by keywords
        print(f"Filtering posts by keywords...")
        filtered_posts = self.filter_posts(posts)
        print(f"Found {len(filtered_posts)} relevant posts")
        
        # Analyze each post
        print("Analyzing posts...")
        analysis_results = []
        
        for i, post in enumerate(filtered_posts):
            print(f"Analyzing post {i+1}/{len(filtered_posts)}")
            
            # Classify sentiment
            sentiment, confidence, reason = self.classify_sentiment(post['text'])
            
            # Get stock data for each symbol
            stock_impacts = {}
            for symbol in self.config['market_data']['symbols']:
                impacts = self.get_stock_impact(symbol, post['timestamp'])
                stock_impacts[symbol] = impacts
            
            # Analyze conditions
            condition_results = self.analyze_conditions(post)
            
            result = {
                'post_id': post.get('id', ''),
                'timestamp': post['timestamp'],
                'text': post['text'],
                'sentiment': sentiment,
                'confidence': confidence,
                'reason': reason,
                'engagement': post.get('engagement', 0),
                'stock_impacts': stock_impacts,
                'conditions': condition_results
            }
            
            analysis_results.append(result)
            time.sleep(0.5)  # Rate limiting
        
        results['analysis'] = analysis_results
        
        # Calculate sentiment distribution
        sentiments = [r['sentiment'] for r in analysis_results]
        results['sentiment_distribution'] = pd.Series(sentiments).value_counts().to_dict()
        
        # Calculate average impacts by sentiment
        results['price_impacts'] = self.calculate_price_impacts(analysis_results)
        
        results['metadata']['end_time'] = datetime.now()
        
        return results
    
    def fetch_posts(self) -> List[Dict]:
        """Fetch posts from social media platform"""
        # For demonstration, return sample posts
        # In production, this would call Apify or other APIs
        
        # Check if we're dealing with Twitter/X
        if self.config['social_media']['platform'] == 'twitter':
            # Return sample posts for demonstration
            return self.create_sample_posts()
        
        # Add other platform handlers here
        return []
    
    def create_sample_posts(self) -> List[Dict]:
        """Create sample posts for testing"""
        posts = []
        accounts = self.config['social_media']['accounts']
        
        # Generate sample posts
        for i in range(20):
            post = {
                'id': f'sample_{i}',
                'text': self.generate_sample_text(i),
                'timestamp': datetime.now() - timedelta(days=i*10),
                'author': accounts[0] if accounts else 'unknown',
                'engagement': np.random.randint(10000, 500000),
                'likes': np.random.randint(5000, 250000),
                'retweets': np.random.randint(5000, 250000)
            }
            posts.append(post)
        
        return posts
    
    def generate_sample_text(self, index: int) -> str:
        """Generate sample text based on keywords"""
        keywords = self.config['social_media']['keywords']
        
        templates = [
            f"Amazing progress with {keywords[0]}! The future is bright.",
            f"Concerned about {keywords[1]} development. We need better regulations.",
            f"Just announced new {keywords[2]} features. Game changing!",
            f"The {keywords[0]} industry is transforming rapidly.",
            f"Meeting with {keywords[3] if len(keywords) > 3 else keywords[0]} team today.",
        ]
        
        return templates[index % len(templates)]
    
    def filter_posts(self, posts: List[Dict]) -> List[Dict]:
        """Filter posts by keywords"""
        keywords = [k.lower() for k in self.config['social_media']['keywords']]
        filtered = []
        
        for post in posts:
            text_lower = post['text'].lower()
            if any(keyword in text_lower for keyword in keywords):
                filtered.append(post)
        
        return filtered
    
    def classify_sentiment(self, text: str) -> Tuple[str, float, str]:
        """Classify sentiment using configured LLM"""
        categories = self.config['sentiment']['categories']
        
        # Build prompt
        if 'custom_prompt' in self.config['sentiment']:
            prompt = self.config['sentiment']['custom_prompt'].replace('{tweet_text}', text)
        else:
            prompt = self.build_default_prompt(text, categories)
        
        try:
            if self.config['sentiment']['provider'] == 'openai':
                response = self.openai_client.chat.completions.create(
                    model=self.config['sentiment']['model'],
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self.config['sentiment']['temperature'],
                    max_tokens=150
                )
                
                result = json.loads(response.choices[0].message.content)
                return result['sentiment'], result['confidence'], result['reason']
            
            elif self.config['sentiment']['provider'] == 'anthropic':
                response = self.anthropic_client.messages.create(
                    model=self.config['sentiment']['model'],
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self.config['sentiment']['temperature'],
                    max_tokens=150
                )
                
                result = json.loads(response.content[0].text)
                return result['sentiment'], result['confidence'], result['reason']
        
        except Exception as e:
            print(f"Error classifying sentiment: {e}")
            # Fallback classification
            return self.fallback_classification(text)
    
    def build_default_prompt(self, text: str, categories: List[Dict]) -> str:
        """Build default sentiment classification prompt"""
        prompt = "Classify the sentiment of the following text into one of these categories:\n\n"
        
        for i, cat in enumerate(categories):
            prompt += f"{i+1}. {cat['name']}: {cat['description']}\n"
        
        prompt += f"\nText: \"{text}\"\n\n"
        prompt += "Respond in JSON format:\n"
        prompt += '{"sentiment": "CATEGORY_NAME", "confidence": 0.0-1.0, "reason": "brief explanation"}'
        
        return prompt
    
    def fallback_classification(self, text: str) -> Tuple[str, float, str]:
        """Simple keyword-based classification"""
        text_lower = text.lower()
        
        positive_words = ['great', 'amazing', 'excellent', 'success', 'breakthrough']
        negative_words = ['bad', 'terrible', 'failure', 'problem', 'concern']
        
        pos_score = sum(1 for word in positive_words if word in text_lower)
        neg_score = sum(1 for word in negative_words if word in text_lower)
        
        categories = [cat['name'] for cat in self.config['sentiment']['categories']]
        
        if pos_score > neg_score and 'BULLISH' in categories:
            return 'BULLISH', 0.5, 'Keyword-based'
        elif neg_score > pos_score and 'BEARISH' in categories:
            return 'BEARISH', 0.5, 'Keyword-based'
        elif 'NEUTRAL' in categories:
            return 'NEUTRAL', 0.5, 'Keyword-based'
        else:
            return categories[0], 0.5, 'Default'
    
    def get_stock_impact(self, symbol: str, timestamp: datetime) -> Dict[str, float]:
        """Get stock price changes after post timestamp"""
        impacts = {}
        
        # For demonstration, return random values
        # In production, this would call Alpaca API
        for interval in self.config['analysis']['time_intervals']:
            impacts[f'{interval}h'] = np.random.uniform(-5, 5)
        
        return impacts
    
    def analyze_conditions(self, post: Dict) -> Dict[str, Any]:
        """Analyze additional conditions"""
        results = {}
        
        for condition in self.config['analysis']['conditions']:
            if not condition.get('enabled', True):
                continue
            
            if condition['name'] == 'market_hours':
                # Check if posted during market hours
                et_tz = pytz.timezone('America/New_York')
                et_time = post['timestamp'].astimezone(et_tz)
                market_open = et_time.replace(hour=9, minute=30, second=0)
                market_close = et_time.replace(hour=16, minute=0, second=0)
                is_market_hours = market_open <= et_time <= market_close and et_time.weekday() < 5
                results['market_hours'] = is_market_hours
            
            elif condition['name'] == 'engagement_level':
                # Categorize engagement
                engagement = post.get('engagement', 0)
                thresholds = condition.get('thresholds', {})
                
                if engagement >= thresholds.get('viral', 1000000):
                    results['engagement_level'] = 'viral'
                elif engagement >= thresholds.get('high', 500000):
                    results['engagement_level'] = 'high'
                elif engagement >= thresholds.get('medium', 100000):
                    results['engagement_level'] = 'medium'
                else:
                    results['engagement_level'] = 'low'
            
            # Add custom condition handlers here
        
        return results
    
    def calculate_price_impacts(self, analysis_results: List[Dict]) -> Dict[str, Dict]:
        """Calculate average price impacts by sentiment"""
        impacts = {}
        
        # Group by sentiment
        df = pd.DataFrame(analysis_results)
        
        for sentiment in df['sentiment'].unique():
            sentiment_df = df[df['sentiment'] == sentiment]
            impacts[sentiment] = {}
            
            # Calculate averages for each symbol and interval
            for symbol in self.config['market_data']['symbols']:
                symbol_impacts = {}
                
                for interval in self.config['analysis']['time_intervals']:
                    key = f'{interval}h'
                    values = []
                    
                    for _, row in sentiment_df.iterrows():
                        if symbol in row['stock_impacts']:
                            values.append(row['stock_impacts'][symbol].get(key, 0))
                    
                    if values:
                        symbol_impacts[key] = {
                            'mean': np.mean(values),
                            'std': np.std(values),
                            'count': len(values)
                        }
                
                impacts[sentiment][symbol] = symbol_impacts
        
        return impacts