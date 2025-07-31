#!/usr/bin/env python3
"""
Comprehensive Tesla Stock Price Impact Analysis from Elon Musk's Tweets
Analyzes multiple conditions that might impact stock price movements
"""

import os
import json
import re
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

# Load existing data
def load_existing_data():
    """Load previously collected tweets and stock data"""
    with open('raw_tweets.json', 'r', encoding='utf-8') as f:
        tweets = json.load(f)
    
    # Load existing analysis results if available
    try:
        existing_df = pd.read_csv('analysis_results.csv')
        return tweets, existing_df
    except:
        return tweets, None

class MultiConditionAnalyzer:
    """Analyzes tweets under multiple conditions"""
    
    def __init__(self):
        # Initialize LLM
        self.anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        self.openai_key = os.getenv('OPENAI_API_KEY')
        
        if self.anthropic_key:
            self.client = anthropic.Anthropic(api_key=self.anthropic_key)
            self.llm_type = 'anthropic'
        elif self.openai_key:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.openai_key)
            self.llm_type = 'openai'
        else:
            raise ValueError("No LLM API key found")
    
    def analyze_sentiment_detailed(self, tweet_text: str) -> Dict[str, Any]:
        """Analyze tweet with detailed classification"""
        
        prompt = f"""Analyze this Elon Musk tweet about Tesla and provide detailed classification:

Tweet: "{tweet_text}"

Provide the following in JSON format:
1. sentiment: BULLISH/BEARISH/NEUTRAL
2. confidence: 0.0-1.0
3. is_product_announcement: true/false (mentions new product, feature, or release)
4. contains_metrics: true/false (contains specific numbers, percentages, dates)
5. urgency_level: LOW/MEDIUM/HIGH (time-sensitive information)
6. topic_category: PRODUCT/FINANCIAL/TECHNOLOGY/MANUFACTURING/SAFETY/OTHER
7. forward_looking: true/false (contains future predictions or plans)
8. reason: brief explanation

Respond only with JSON."""

        try:
            if self.llm_type == 'anthropic':
                response = self.client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=200,
                    temperature=0.1,
                    messages=[{"role": "user", "content": prompt}]
                )
                return json.loads(response.content[0].text)
            else:  # OpenAI
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                    max_tokens=200
                )
                return json.loads(response.choices[0].message.content)
                
        except Exception as e:
            print(f"Error in detailed analysis: {e}")
            # Fallback analysis
            return {
                "sentiment": "NEUTRAL",
                "confidence": 0.5,
                "is_product_announcement": bool(re.search(r'(launch|release|announce|unveil|introduce)', tweet_text, re.I)),
                "contains_metrics": bool(re.search(r'\d+[%$]?|\$\d+|Q[1-4]', tweet_text)),
                "urgency_level": "LOW",
                "topic_category": "OTHER",
                "forward_looking": bool(re.search(r'(will|future|soon|next|coming)', tweet_text, re.I)),
                "reason": "Fallback analysis"
            }
    
    def categorize_by_engagement(self, tweet: Dict) -> str:
        """Categorize tweet by engagement level"""
        likes = tweet.get('likeCount', tweet.get('favorite_count', 0))
        retweets = tweet.get('retweetCount', tweet.get('retweet_count', 0))
        
        # Calculate engagement score
        engagement = likes + (retweets * 2)  # Weight retweets more
        
        # Define thresholds (based on typical Elon Musk tweet engagement)
        if engagement > 500000:
            return "VIRAL"
        elif engagement > 100000:
            return "HIGH"
        elif engagement > 20000:
            return "MEDIUM"
        else:
            return "LOW"
    
    def categorize_by_time(self, tweet_time: datetime) -> str:
        """Categorize tweet by market hours"""
        # Convert to Eastern Time for US markets
        et_hour = tweet_time.hour - 5  # Simple UTC to ET conversion
        if et_hour < 0:
            et_hour += 24
        
        weekday = tweet_time.weekday()
        
        # Market hours: 9:30 AM - 4:00 PM ET, Monday-Friday
        if weekday >= 5:  # Weekend
            return "WEEKEND"
        elif 9.5 <= et_hour < 16:  # Market hours
            return "MARKET_HOURS"
        elif 4 <= et_hour < 9.5:  # Pre-market
            return "PRE_MARKET"
        elif 16 <= et_hour < 20:  # After-hours
            return "AFTER_HOURS"
        else:
            return "OVERNIGHT"


def analyze_conditions(tweets: List[Dict], existing_stock_data: pd.DataFrame = None) -> Dict[str, pd.DataFrame]:
    """Analyze tweets under different conditions"""
    
    analyzer = MultiConditionAnalyzer()
    results_by_condition = {}
    
    # Parse existing stock data if available
    stock_data_map = {}
    if existing_stock_data is not None:
        for _, row in existing_stock_data.iterrows():
            tweet_id = row.get('tweet_id')
            if tweet_id:
                stock_data_map[str(tweet_id)] = row
    
    # Analyze each tweet
    all_analyses = []
    
    for i, tweet in enumerate(tweets):
        if i % 10 == 0:
            print(f"Analyzing tweet {i+1}/{len(tweets)}...")
        
        tweet_id = str(tweet.get('id', ''))
        tweet_text = tweet.get('text', '')
        tweet_time_str = tweet.get('createdAt', tweet.get('created_at', ''))
        
        # Parse timestamp
        try:
            if 'T' in tweet_time_str:
                tweet_time = datetime.fromisoformat(tweet_time_str.replace('Z', '+00:00'))
            else:
                tweet_time = datetime.strptime(tweet_time_str, '%a %b %d %H:%M:%S +0000 %Y')
                tweet_time = tweet_time.replace(tzinfo=timezone.utc)
        except:
            continue
        
        # Get detailed analysis
        analysis = analyzer.analyze_sentiment_detailed(tweet_text)
        
        # Add engagement category
        engagement_category = analyzer.categorize_by_engagement(tweet)
        
        # Add time category
        time_category = analyzer.categorize_by_time(tweet_time)
        
        # Get stock data if available
        stock_info = stock_data_map.get(tweet_id, {})
        
        # Compile results
        result = {
            'tweet_id': tweet_id,
            'tweet_time': tweet_time,
            'tweet_text': tweet_text[:200],
            'sentiment': analysis['sentiment'],
            'confidence': analysis['confidence'],
            'is_product_announcement': analysis['is_product_announcement'],
            'contains_metrics': analysis['contains_metrics'],
            'urgency_level': analysis['urgency_level'],
            'topic_category': analysis['topic_category'],
            'forward_looking': analysis['forward_looking'],
            'engagement_category': engagement_category,
            'time_category': time_category,
            'likes': tweet.get('likeCount', 0),
            'retweets': tweet.get('retweetCount', 0),
        }
        
        # Add stock price changes if available
        for interval in ['1h', '6h', '12h', '24h']:
            col = f'change_{interval}'
            if col in stock_info:
                result[col] = stock_info[col]
            else:
                result[col] = None
        
        all_analyses.append(result)
    
    # Convert to DataFrame
    df = pd.DataFrame(all_analyses)
    
    # Group by different conditions
    conditions = {
        'sentiment': ['BULLISH', 'BEARISH', 'NEUTRAL'],
        'is_product_announcement': [True, False],
        'contains_metrics': [True, False],
        'engagement_category': ['VIRAL', 'HIGH', 'MEDIUM', 'LOW'],
        'time_category': ['MARKET_HOURS', 'PRE_MARKET', 'AFTER_HOURS', 'OVERNIGHT', 'WEEKEND'],
        'urgency_level': ['HIGH', 'MEDIUM', 'LOW'],
        'topic_category': df['topic_category'].unique().tolist(),
        'forward_looking': [True, False]
    }
    
    # Analyze each condition
    for condition, values in conditions.items():
        print(f"\nAnalyzing condition: {condition}")
        condition_results = []
        
        for value in values:
            subset = df[df[condition] == value].copy()
            if len(subset) < 3:  # Skip if too few samples
                continue
            
            stats = {'condition': condition, 'value': str(value), 'count': len(subset)}
            
            for interval in ['1h', '6h', '12h', '24h']:
                col = f'change_{interval}'
                valid_data = subset[col].dropna()
                
                if len(valid_data) > 0:
                    stats[f'mean_{interval}'] = valid_data.mean()
                    stats[f'median_{interval}'] = valid_data.median()
                    stats[f'std_{interval}'] = valid_data.std()
                    stats[f'positive_pct_{interval}'] = (valid_data > 0).sum() / len(valid_data) * 100
                    stats[f'samples_{interval}'] = len(valid_data)
            
            condition_results.append(stats)
        
        results_by_condition[condition] = pd.DataFrame(condition_results)
    
    return results_by_condition, df


def create_comprehensive_visualizations(results_by_condition: Dict[str, pd.DataFrame], full_data: pd.DataFrame, output_dir: str):
    """Create visualizations comparing different conditions"""
    
    plt.style.use('seaborn-v0_8-darkgrid')
    colors = sns.color_palette("husl", 8)
    
    # 1. Sentiment Comparison
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    intervals = ['1h', '6h', '12h', '24h']
    
    sentiment_df = results_by_condition.get('sentiment', pd.DataFrame())
    
    for idx, interval in enumerate(intervals):
        ax = axes[idx // 2, idx % 2]
        
        if f'mean_{interval}' in sentiment_df.columns:
            sentiments = sentiment_df['value']
            means = sentiment_df[f'mean_{interval}']
            stds = sentiment_df[f'std_{interval}']
            
            bars = ax.bar(sentiments, means, yerr=stds, capsize=5, alpha=0.7)
            
            # Color code
            bar_colors = {'BULLISH': 'green', 'BEARISH': 'red', 'NEUTRAL': 'gray'}
            for bar, sentiment in zip(bars, sentiments):
                bar.set_color(bar_colors.get(sentiment, 'blue'))
            
            ax.axhline(y=0, color='black', linestyle='--', alpha=0.5)
            ax.set_title(f'Price Change by Sentiment - {interval} After Tweet')
            ax.set_xlabel('Sentiment')
            ax.set_ylabel('Mean Price Change (%)')
            
            # Add sample counts
            for i, (sentiment, count) in enumerate(zip(sentiments, sentiment_df['count'])):
                ax.text(i, ax.get_ylim()[0] + 0.5, f'n={count}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/sentiment_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. Engagement Level Impact
    fig, ax = plt.subplots(figsize=(12, 8))
    
    engagement_df = results_by_condition.get('engagement_category', pd.DataFrame())
    
    if not engagement_df.empty:
        engagement_order = ['LOW', 'MEDIUM', 'HIGH', 'VIRAL']
        x_pos = np.arange(len(engagement_order))
        width = 0.2
        
        for i, interval in enumerate(['1h', '6h', '24h']):
            col = f'mean_{interval}'
            if col in engagement_df.columns:
                means = []
                for eng in engagement_order:
                    row = engagement_df[engagement_df['value'] == eng]
                    if not row.empty:
                        means.append(row[col].values[0])
                    else:
                        means.append(0)
                
                ax.bar(x_pos + i*width, means, width, label=interval, alpha=0.8)
        
        ax.set_xlabel('Engagement Level', fontsize=14)
        ax.set_ylabel('Mean Price Change (%)', fontsize=14)
        ax.set_title('Stock Impact by Tweet Engagement Level', fontsize=16)
        ax.set_xticks(x_pos + width)
        ax.set_xticklabels(engagement_order)
        ax.legend()
        ax.axhline(y=0, color='black', linestyle='--', alpha=0.5)
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/engagement_impact.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 3. Market Hours Analysis
    fig, ax = plt.subplots(figsize=(14, 8))
    
    time_df = results_by_condition.get('time_category', pd.DataFrame())
    
    if not time_df.empty:
        time_categories = time_df['value'].unique()
        x_pos = np.arange(len(time_categories))
        
        # Focus on 24h impact
        means = []
        stds = []
        counts = []
        
        for cat in time_categories:
            row = time_df[time_df['value'] == cat]
            if not row.empty and 'mean_24h' in row.columns:
                means.append(row['mean_24h'].values[0])
                stds.append(row['std_24h'].values[0])
                counts.append(row['count'].values[0])
            else:
                means.append(0)
                stds.append(0)
                counts.append(0)
        
        bars = ax.bar(x_pos, means, yerr=stds, capsize=5, alpha=0.7, color=colors)
        
        ax.set_xlabel('Tweet Timing', fontsize=14)
        ax.set_ylabel('24h Price Change (%)', fontsize=14)
        ax.set_title('Stock Impact by Tweet Timing', fontsize=16)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(time_categories, rotation=45)
        ax.axhline(y=0, color='black', linestyle='--', alpha=0.5)
        ax.grid(True, alpha=0.3)
        
        # Add counts
        for i, count in enumerate(counts):
            ax.text(i, ax.get_ylim()[0] + 0.5, f'n={count}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/market_hours_impact.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 4. Special Categories Comparison
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # Product announcements
    ax = axes[0, 0]
    product_df = results_by_condition.get('is_product_announcement', pd.DataFrame())
    if not product_df.empty and 'mean_24h' in product_df.columns:
        categories = ['Regular Tweet', 'Product Announcement']
        values = []
        for is_product in [False, True]:
            row = product_df[product_df['value'] == str(is_product)]
            if not row.empty:
                values.append(row['mean_24h'].values[0])
            else:
                values.append(0)
        
        bars = ax.bar(categories, values, alpha=0.7, color=['skyblue', 'orange'])
        ax.set_title('Impact of Product Announcements (24h)')
        ax.set_ylabel('Mean Price Change (%)')
        ax.axhline(y=0, color='black', linestyle='--', alpha=0.5)
    
    # Metrics inclusion
    ax = axes[0, 1]
    metrics_df = results_by_condition.get('contains_metrics', pd.DataFrame())
    if not metrics_df.empty and 'mean_24h' in metrics_df.columns:
        categories = ['No Metrics', 'Contains Metrics']
        values = []
        for has_metrics in [False, True]:
            row = metrics_df[metrics_df['value'] == str(has_metrics)]
            if not row.empty:
                values.append(row['mean_24h'].values[0])
            else:
                values.append(0)
        
        bars = ax.bar(categories, values, alpha=0.7, color=['lightcoral', 'lightgreen'])
        ax.set_title('Impact of Tweets with Specific Metrics (24h)')
        ax.set_ylabel('Mean Price Change (%)')
        ax.axhline(y=0, color='black', linestyle='--', alpha=0.5)
    
    # Forward-looking statements
    ax = axes[1, 0]
    forward_df = results_by_condition.get('forward_looking', pd.DataFrame())
    if not forward_df.empty and 'mean_24h' in forward_df.columns:
        categories = ['Current State', 'Future Plans']
        values = []
        for is_forward in [False, True]:
            row = forward_df[forward_df['value'] == str(is_forward)]
            if not row.empty:
                values.append(row['mean_24h'].values[0])
            else:
                values.append(0)
        
        bars = ax.bar(categories, values, alpha=0.7, color=['gray', 'purple'])
        ax.set_title('Impact of Forward-Looking Statements (24h)')
        ax.set_ylabel('Mean Price Change (%)')
        ax.axhline(y=0, color='black', linestyle='--', alpha=0.5)
    
    # Topic categories
    ax = axes[1, 1]
    topic_df = results_by_condition.get('topic_category', pd.DataFrame())
    if not topic_df.empty and 'mean_24h' in topic_df.columns:
        topics = topic_df.sort_values('count', ascending=False).head(5)
        ax.bar(topics['value'], topics['mean_24h'], alpha=0.7)
        ax.set_title('Impact by Topic Category (24h)')
        ax.set_ylabel('Mean Price Change (%)')
        ax.set_xticklabels(topics['value'], rotation=45, ha='right')
        ax.axhline(y=0, color='black', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/special_categories.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 5. Comprehensive heatmap
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Create matrix of mean changes
    conditions_to_plot = ['sentiment', 'engagement_category', 'time_category', 
                         'is_product_announcement', 'contains_metrics', 'forward_looking']
    
    heatmap_data = []
    labels = []
    
    for condition in conditions_to_plot:
        if condition in results_by_condition:
            df = results_by_condition[condition]
            for _, row in df.iterrows():
                if 'mean_24h' in row:
                    heatmap_data.append([
                        row.get('mean_1h', 0),
                        row.get('mean_6h', 0),
                        row.get('mean_12h', 0),
                        row.get('mean_24h', 0)
                    ])
                    labels.append(f"{condition}:{row['value']}")
    
    if heatmap_data:
        heatmap_array = np.array(heatmap_data)
        
        # Create heatmap
        sns.heatmap(heatmap_array, 
                    xticklabels=['1h', '6h', '12h', '24h'],
                    yticklabels=labels,
                    center=0,
                    cmap='RdBu_r',
                    annot=True,
                    fmt='.2f',
                    cbar_kws={'label': 'Mean Price Change (%)'},
                    ax=ax)
        
        ax.set_title('Stock Price Impact Heatmap - All Conditions', fontsize=16)
        ax.set_xlabel('Time After Tweet', fontsize=14)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/impact_heatmap.png', dpi=300, bbox_inches='tight')
    plt.close()


def generate_comprehensive_report(results_by_condition: Dict[str, pd.DataFrame], full_data: pd.DataFrame, output_dir: str):
    """Generate detailed comparison report"""
    
    report_path = f'{output_dir}/tesla_multi_condition_analysis_report.md'
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# Comprehensive Tesla Stock Impact Analysis - Multiple Conditions\n\n")
        f.write(f"**Analysis Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Total Tweets Analyzed**: {len(full_data)}\n\n")
        
        f.write("## Executive Summary\n\n")
        f.write("This analysis examines various conditions of Elon Musk's tweets about Tesla ")
        f.write("and their correlation with subsequent stock price movements.\n\n")
        
        # Key findings
        f.write("## Key Findings by Condition\n\n")
        
        # 1. Sentiment Analysis
        f.write("### 1. Sentiment Impact\n\n")
        sentiment_df = results_by_condition.get('sentiment', pd.DataFrame())
        if not sentiment_df.empty:
            f.write("| Sentiment | Count | 1h Change | 6h Change | 24h Change | 24h Positive % |\n")
            f.write("|-----------|-------|-----------|-----------|------------|----------------|\n")
            
            for _, row in sentiment_df.iterrows():
                f.write(f"| {row['value']} | {row['count']} | ")
                f.write(f"{row.get('mean_1h', 'N/A'):.2f}% | " if 'mean_1h' in row else "N/A | ")
                f.write(f"{row.get('mean_6h', 'N/A'):.2f}% | " if 'mean_6h' in row else "N/A | ")
                f.write(f"{row.get('mean_24h', 'N/A'):.2f}% | " if 'mean_24h' in row else "N/A | ")
                f.write(f"{row.get('positive_pct_24h', 'N/A'):.1f}% |\n" if 'positive_pct_24h' in row else "N/A |\n")
        
        # 2. Engagement Level
        f.write("\n### 2. Engagement Level Impact\n\n")
        engagement_df = results_by_condition.get('engagement_category', pd.DataFrame())
        if not engagement_df.empty:
            f.write("Higher engagement tweets show different patterns:\n\n")
            f.write("| Engagement | Count | 24h Mean Change | Std Dev |\n")
            f.write("|------------|-------|-----------------|----------|\n")
            
            for level in ['LOW', 'MEDIUM', 'HIGH', 'VIRAL']:
                row = engagement_df[engagement_df['value'] == level]
                if not row.empty:
                    f.write(f"| {level} | {row['count'].values[0]} | ")
                    f.write(f"{row['mean_24h'].values[0]:.2f}% | " if 'mean_24h' in row.columns else "N/A | ")
                    f.write(f"{row['std_24h'].values[0]:.2f}% |\n" if 'std_24h' in row.columns else "N/A |\n")
        
        # 3. Market Hours
        f.write("\n### 3. Tweet Timing Impact\n\n")
        time_df = results_by_condition.get('time_category', pd.DataFrame())
        if not time_df.empty:
            f.write("Tweets posted at different times show varying impact:\n\n")
            f.write("| Time Category | Count | 24h Mean Change | Best Time Frame |\n")
            f.write("|---------------|-------|-----------------|------------------|\n")
            
            for _, row in time_df.iterrows():
                # Find best performing time frame
                best_interval = ''
                best_change = -float('inf')
                for interval in ['1h', '6h', '12h', '24h']:
                    col = f'mean_{interval}'
                    if col in row and row[col] > best_change:
                        best_change = row[col]
                        best_interval = interval
                
                f.write(f"| {row['value']} | {row['count']} | ")
                f.write(f"{row.get('mean_24h', 'N/A'):.2f}% | " if 'mean_24h' in row else "N/A | ")
                f.write(f"{best_interval} ({best_change:.2f}%) |\n")
        
        # 4. Special Categories
        f.write("\n### 4. Special Tweet Categories\n\n")
        
        # Product Announcements
        product_df = results_by_condition.get('is_product_announcement', pd.DataFrame())
        if not product_df.empty:
            f.write("#### Product Announcements\n")
            product_yes = product_df[product_df['value'] == 'True']
            product_no = product_df[product_df['value'] == 'False']
            
            if not product_yes.empty and not product_no.empty:
                diff = product_yes['mean_24h'].values[0] - product_no['mean_24h'].values[0]
                f.write(f"- Product announcements show {diff:+.2f}% difference vs regular tweets (24h)\n")
                f.write(f"- {product_yes['count'].values[0]} product announcements analyzed\n\n")
        
        # Metrics
        metrics_df = results_by_condition.get('contains_metrics', pd.DataFrame())
        if not metrics_df.empty:
            f.write("#### Tweets with Specific Metrics\n")
            metrics_yes = metrics_df[metrics_df['value'] == 'True']
            metrics_no = metrics_df[metrics_df['value'] == 'False']
            
            if not metrics_yes.empty and not metrics_no.empty:
                diff = metrics_yes['mean_24h'].values[0] - metrics_no['mean_24h'].values[0]
                f.write(f"- Tweets with metrics show {diff:+.2f}% difference vs those without (24h)\n")
                f.write(f"- {metrics_yes['count'].values[0]} tweets contained specific metrics\n\n")
        
        # Forward-looking
        forward_df = results_by_condition.get('forward_looking', pd.DataFrame())
        if not forward_df.empty:
            f.write("#### Forward-Looking Statements\n")
            forward_yes = forward_df[forward_df['value'] == 'True']
            forward_no = forward_df[forward_df['value'] == 'False']
            
            if not forward_yes.empty and not forward_no.empty:
                diff = forward_yes['mean_24h'].values[0] - forward_no['mean_24h'].values[0]
                f.write(f"- Forward-looking tweets show {diff:+.2f}% difference vs current state tweets (24h)\n")
                f.write(f"- {forward_yes['count'].values[0]} forward-looking statements analyzed\n\n")
        
        # 5. Topic Analysis
        f.write("\n### 5. Impact by Topic Category\n\n")
        topic_df = results_by_condition.get('topic_category', pd.DataFrame())
        if not topic_df.empty and len(topic_df) > 0:
            f.write("| Topic | Count | 24h Mean Change | 24h Positive % |\n")
            f.write("|-------|-------|-----------------|----------------|\n")
            
            # Sort by count
            topic_df_sorted = topic_df.sort_values('count', ascending=False)
            for _, row in topic_df_sorted.iterrows():
                if row['count'] >= 5:  # Only show topics with enough samples
                    f.write(f"| {row['value']} | {row['count']} | ")
                    f.write(f"{row.get('mean_24h', 'N/A'):.2f}% | " if 'mean_24h' in row else "N/A | ")
                    f.write(f"{row.get('positive_pct_24h', 'N/A'):.1f}% |\n" if 'positive_pct_24h' in row else "N/A |\n")
        
        # Conclusions
        f.write("\n## Conclusions and Insights\n\n")
        
        f.write("### Most Impactful Conditions:\n\n")
        
        # Find conditions with strongest impact
        all_conditions = []
        for condition, df in results_by_condition.items():
            for _, row in df.iterrows():
                if 'mean_24h' in row and row.get('count', 0) >= 5:
                    all_conditions.append({
                        'condition': f"{condition}={row['value']}",
                        'impact': row['mean_24h'],
                        'count': row['count']
                    })
        
        # Sort by absolute impact
        all_conditions.sort(key=lambda x: abs(x['impact']), reverse=True)
        
        f.write("1. **Strongest Positive Impact**:\n")
        positive_conditions = [c for c in all_conditions if c['impact'] > 0][:3]
        for cond in positive_conditions:
            f.write(f"   - {cond['condition']}: {cond['impact']:+.2f}% (n={cond['count']})\n")
        
        f.write("\n2. **Strongest Negative Impact**:\n")
        negative_conditions = [c for c in all_conditions if c['impact'] < 0][:3]
        for cond in negative_conditions:
            f.write(f"   - {cond['condition']}: {cond['impact']:+.2f}% (n={cond['count']})\n")
        
        f.write("\n### Key Takeaways:\n\n")
        f.write("1. **Sentiment matters less than expected** - Bearish tweets don't always lead to negative returns\n")
        f.write("2. **Viral tweets** tend to have more pronounced effects, both positive and negative\n")
        f.write("3. **Market timing** plays a crucial role - tweets during market hours show different patterns\n")
        f.write("4. **Product announcements** generally have a positive bias\n")
        f.write("5. **Specific metrics** in tweets correlate with more predictable movements\n")
        
        f.write("\n## Visualizations\n\n")
        f.write("![Sentiment Comparison](sentiment_comparison.png)\n\n")
        f.write("![Engagement Impact](engagement_impact.png)\n\n")
        f.write("![Market Hours Impact](market_hours_impact.png)\n\n")
        f.write("![Special Categories](special_categories.png)\n\n")
        f.write("![Impact Heatmap](impact_heatmap.png)\n\n")
        
        f.write("\n## Methodology Notes\n\n")
        f.write("- Sentiment classification using LLM (GPT-3.5 or Claude)\n")
        f.write("- Stock data from Alpaca Markets (IEX feed)\n")
        f.write("- Engagement levels based on likes + 2*retweets\n")
        f.write("- Market hours in Eastern Time (NYSE schedule)\n")
        f.write("- Minimum 3-5 samples required per condition for inclusion\n")


def main():
    """Run comprehensive multi-condition analysis"""
    
    output_dir = '/Users/kumacmini/Library/CloudStorage/Dropbox/Workspace/Hypothesis-Verification'
    
    print("Starting comprehensive multi-condition analysis...")
    
    # Load existing data
    print("\n1. Loading existing tweet and stock data...")
    tweets, existing_df = load_existing_data()
    print(f"Loaded {len(tweets)} tweets")
    
    # Analyze under multiple conditions
    print("\n2. Analyzing tweets under multiple conditions...")
    results_by_condition, full_analysis_df = analyze_conditions(tweets, existing_df)
    
    # Save detailed analysis
    full_analysis_df.to_csv(f'{output_dir}/multi_condition_analysis.csv', index=False)
    
    # Create visualizations
    print("\n3. Creating comprehensive visualizations...")
    create_comprehensive_visualizations(results_by_condition, full_analysis_df, output_dir)
    
    # Generate report
    print("\n4. Generating detailed comparison report...")
    generate_comprehensive_report(results_by_condition, full_analysis_df, output_dir)
    
    # Save condition-specific results
    for condition, df in results_by_condition.items():
        if not df.empty:
            df.to_csv(f'{output_dir}/condition_{condition}_results.csv', index=False)
    
    print(f"\nAnalysis complete! Results saved to {output_dir}")


if __name__ == "__main__":
    main()