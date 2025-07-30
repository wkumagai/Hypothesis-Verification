#!/usr/bin/env python3
"""
Sentiment Classification Methodology Documentation and Analysis
Provides detailed criteria and examples for Tesla tweet sentiment classification
"""

import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
from typing import Dict, List, Any

def load_analysis_data():
    """Load the multi-condition analysis data"""
    try:
        df = pd.read_csv('multi_condition_analysis.csv')
        with open('raw_tweets.json', 'r', encoding='utf-8') as f:
            tweets = json.load(f)
        return df, tweets
    except Exception as e:
        print(f"Error loading data: {e}")
        return None, None

def analyze_sentiment_distribution(df: pd.DataFrame):
    """Analyze the distribution of sentiments and their characteristics"""
    
    # Sentiment distribution
    sentiment_counts = df['sentiment'].value_counts()
    
    # Confidence scores by sentiment
    confidence_by_sentiment = df.groupby('sentiment')['confidence'].agg(['mean', 'std', 'min', 'max'])
    
    # Sample tweets for each sentiment
    samples = {}
    for sentiment in ['BULLISH', 'BEARISH', 'NEUTRAL']:
        sentiment_tweets = df[df['sentiment'] == sentiment].nlargest(5, 'confidence')
        samples[sentiment] = sentiment_tweets[['tweet_text', 'confidence']].to_dict('records')
    
    return sentiment_counts, confidence_by_sentiment, samples

def extract_classification_patterns(df: pd.DataFrame):
    """Extract common patterns in sentiment classification"""
    
    patterns = {
        'BULLISH': {
            'keywords': [],
            'phrases': [],
            'topics': Counter(),
            'characteristics': []
        },
        'BEARISH': {
            'keywords': [],
            'phrases': [],
            'topics': Counter(),
            'characteristics': []
        },
        'NEUTRAL': {
            'keywords': [],
            'phrases': [],
            'topics': Counter(),
            'characteristics': []
        }
    }
    
    # Common bullish indicators
    bullish_keywords = [
        'amazing', 'great', 'incredible', 'breakthrough', 'record', 'best',
        'revolutionary', 'game-changing', 'proud', 'excited', 'love', '🚀',
        'milestone', 'achievement', 'success', 'leading', 'dominating'
    ]
    
    # Common bearish indicators
    bearish_keywords = [
        'problem', 'issue', 'difficult', 'challenge', 'delay', 'recall',
        'investigation', 'concern', 'risk', 'unfortunately', 'struggle',
        'failure', 'disappointing', 'setback'
    ]
    
    # Common neutral indicators
    neutral_keywords = [
        'update', 'information', 'fact', 'data', 'report', 'status',
        'currently', 'working on', 'in progress', 'planned', 'scheduled'
    ]
    
    # Analyze each sentiment group
    for sentiment in ['BULLISH', 'BEARISH', 'NEUTRAL']:
        sentiment_df = df[df['sentiment'] == sentiment]
        
        # Count keyword occurrences
        for _, row in sentiment_df.iterrows():
            text = row['tweet_text'].lower()
            
            # Count topics
            patterns[sentiment]['topics'][row.get('topic_category', 'OTHER')] += 1
            
            # Find keywords
            if sentiment == 'BULLISH':
                for keyword in bullish_keywords:
                    if keyword.lower() in text:
                        patterns[sentiment]['keywords'].append(keyword)
            elif sentiment == 'BEARISH':
                for keyword in bearish_keywords:
                    if keyword.lower() in text:
                        patterns[sentiment]['keywords'].append(keyword)
            else:
                for keyword in neutral_keywords:
                    if keyword.lower() in text:
                        patterns[sentiment]['keywords'].append(keyword)
    
    return patterns

def create_methodology_visualizations(df: pd.DataFrame, output_dir: str):
    """Create visualizations explaining the classification methodology"""
    
    plt.style.use('seaborn-v0_8-darkgrid')
    
    # 1. Sentiment distribution pie chart
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))
    
    sentiment_counts = df['sentiment'].value_counts()
    colors = {'BULLISH': 'green', 'BEARISH': 'red', 'NEUTRAL': 'gray'}
    
    ax1.pie(sentiment_counts.values, labels=sentiment_counts.index, autopct='%1.1f%%',
            colors=[colors.get(s, 'blue') for s in sentiment_counts.index])
    ax1.set_title('Distribution of Sentiment Classifications', fontsize=14)
    
    # 2. Confidence score distribution by sentiment
    sentiments = ['BULLISH', 'BEARISH', 'NEUTRAL']
    confidence_data = [df[df['sentiment'] == s]['confidence'].values for s in sentiments]
    
    bp = ax2.boxplot(confidence_data, labels=sentiments, patch_artist=True)
    for patch, sentiment in zip(bp['boxes'], sentiments):
        patch.set_facecolor(colors.get(sentiment, 'blue'))
    
    ax2.set_title('LLM Confidence Scores by Sentiment', fontsize=14)
    ax2.set_ylabel('Confidence Score', fontsize=12)
    ax2.set_ylim(0, 1.1)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/sentiment_methodology_overview.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 3. Topic distribution by sentiment
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    for idx, sentiment in enumerate(sentiments):
        ax = axes[idx]
        sentiment_df = df[df['sentiment'] == sentiment]
        topic_counts = sentiment_df['topic_category'].value_counts()
        
        if not topic_counts.empty:
            ax.bar(range(len(topic_counts)), topic_counts.values, 
                   color=colors.get(sentiment, 'blue'), alpha=0.7)
            ax.set_xticks(range(len(topic_counts)))
            ax.set_xticklabels(topic_counts.index, rotation=45, ha='right')
            ax.set_title(f'{sentiment} Topics', fontsize=14)
            ax.set_ylabel('Count', fontsize=12)
            ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/sentiment_topic_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 4. Characteristics comparison
    fig, ax = plt.subplots(figsize=(12, 8))
    
    characteristics = ['is_product_announcement', 'contains_metrics', 'forward_looking']
    char_labels = ['Product\nAnnouncement', 'Contains\nMetrics', 'Forward\nLooking']
    
    x = np.arange(len(char_labels))
    width = 0.25
    
    for i, sentiment in enumerate(sentiments):
        sentiment_df = df[df['sentiment'] == sentiment]
        percentages = [
            (sentiment_df[char] == True).sum() / len(sentiment_df) * 100
            for char in characteristics
        ]
        
        ax.bar(x + i*width, percentages, width, label=sentiment, 
               color=colors.get(sentiment, 'blue'), alpha=0.8)
    
    ax.set_xlabel('Tweet Characteristics', fontsize=14)
    ax.set_ylabel('Percentage of Tweets (%)', fontsize=14)
    ax.set_title('Tweet Characteristics by Sentiment', fontsize=16)
    ax.set_xticks(x + width)
    ax.set_xticklabels(char_labels)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/sentiment_characteristics.png', dpi=300, bbox_inches='tight')
    plt.close()

def generate_methodology_report(df: pd.DataFrame, patterns: Dict, samples: Dict, output_dir: str):
    """Generate detailed methodology report"""
    
    report_path = f'{output_dir}/sentiment_classification_methodology_report.md'
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# Tesla Tweet Sentiment Classification Methodology\n\n")
        f.write("## 完全な再現可能性のための詳細文書\n\n")
        f.write(f"**作成日時**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # 1. Classification Process
        f.write("## 1. 分類プロセス\n\n")
        f.write("### 使用したLLMと設定\n")
        f.write("- **Primary LLM**: OpenAI GPT-3.5-turbo\n")
        f.write("- **Fallback LLM**: Anthropic Claude-3-haiku\n")
        f.write("- **Temperature**: 0.1 (一貫性のため低温設定)\n")
        f.write("- **Max Tokens**: 150\n\n")
        
        f.write("### LLMプロンプト（完全版）\n")
        f.write("```\n")
        f.write("Analyze the following tweet from Elon Musk about Tesla and classify it as:\n")
        f.write("1. BULLISH (positive about Tesla's future, products, or performance)\n")
        f.write("2. BEARISH (negative or cautious about Tesla)\n")
        f.write("3. NEUTRAL (factual, mixed, or unclear sentiment)\n")
        f.write("\n")
        f.write("Also provide a confidence score (0-1) and a brief reason.\n")
        f.write("\n")
        f.write('Tweet: "{tweet_text}"\n')
        f.write("\n")
        f.write("Respond in JSON format:\n")
        f.write('{"sentiment": "BULLISH/BEARISH/NEUTRAL", "confidence": 0.0-1.0, "reason": "brief explanation"}\n')
        f.write("```\n\n")
        
        # 2. Classification Criteria
        f.write("## 2. 詳細な分類基準\n\n")
        
        f.write("### BULLISH（強気）の判断基準\n")
        f.write("以下の要素を含むツイートは強気と分類される傾向:\n\n")
        f.write("**キーワード・フレーズ**:\n")
        f.write("- ポジティブな形容詞: amazing, great, incredible, breakthrough, revolutionary\n")
        f.write("- 成果を示す言葉: record, milestone, achievement, success, leading\n")
        f.write("- 将来への期待: excited, proud, game-changing\n")
        f.write("- 絵文字: 🚀, ❤️, 🔥\n\n")
        
        f.write("**文脈的要素**:\n")
        f.write("- 新製品や機能の成功を報告\n")
        f.write("- 生産記録や販売記録の達成\n")
        f.write("- 技術的ブレークスルーの発表\n")
        f.write("- チームや製品への賞賛\n\n")
        
        f.write("### BEARISH（弱気）の判断基準\n")
        f.write("以下の要素を含むツイートは弱気と分類される傾向:\n\n")
        f.write("**キーワード・フレーズ**:\n")
        f.write("- 問題を示す言葉: problem, issue, difficult, challenge, delay\n")
        f.write("- ネガティブな結果: recall, investigation, concern, risk\n")
        f.write("- 失敗や挫折: failure, disappointing, setback, unfortunately\n\n")
        
        f.write("**文脈的要素**:\n")
        f.write("- 生産や配送の遅延\n")
        f.write("- 技術的な問題や欠陥\n")
        f.write("- 規制上の懸念や調査\n")
        f.write("- 目標未達成の報告\n\n")
        
        f.write("### NEUTRAL（中立）の判断基準\n")
        f.write("以下の要素を含むツイートは中立と分類される傾向:\n\n")
        f.write("**キーワード・フレーズ**:\n")
        f.write("- 事実報告: update, information, fact, data, report\n")
        f.write("- 進行状況: currently, working on, in progress, planned\n")
        f.write("- 客観的記述: scheduled, status, details\n\n")
        
        f.write("**文脈的要素**:\n")
        f.write("- 感情的な判断を含まない事実の報告\n")
        f.write("- 技術仕様や数値データの共有\n")
        f.write("- プロセスや手順の説明\n")
        f.write("- ポジティブとネガティブが混在\n\n")
        
        # 3. Distribution Analysis
        f.write("## 3. 実際の分類結果の分布\n\n")
        
        sentiment_counts = df['sentiment'].value_counts()
        total = len(df)
        
        f.write("### 感情分類の内訳\n")
        f.write("| 感情 | 件数 | 割合 | 平均信頼度 |\n")
        f.write("|------|------|------|------------|\n")
        
        for sentiment in ['BULLISH', 'BEARISH', 'NEUTRAL']:
            count = sentiment_counts.get(sentiment, 0)
            pct = count / total * 100
            avg_conf = df[df['sentiment'] == sentiment]['confidence'].mean()
            f.write(f"| {sentiment} | {count} | {pct:.1f}% | {avg_conf:.3f} |\n")
        
        # 4. Specific Examples
        f.write("\n## 4. 具体的な分類例\n\n")
        
        for sentiment, examples in samples.items():
            f.write(f"### {sentiment} の例（信頼度の高い順）\n\n")
            for i, example in enumerate(examples[:3], 1):
                f.write(f"**例{i}** (信頼度: {example['confidence']:.3f})\n")
                f.write(f"```\n{example['tweet_text']}\n```\n\n")
        
        # 5. Edge Cases
        f.write("## 5. エッジケースと曖昧な例\n\n")
        
        # Low confidence examples
        low_conf = df[df['confidence'] < 0.6].nlargest(5, 'confidence')
        
        f.write("### 低信頼度の例（分類が困難だったケース）\n\n")
        for _, row in low_conf.iterrows():
            f.write(f"**{row['sentiment']}** (信頼度: {row['confidence']:.3f})\n")
            f.write(f"```\n{row['tweet_text'][:200]}...\n```\n\n")
        
        # 6. Fallback Classification
        f.write("## 6. フォールバック分類\n\n")
        f.write("LLMが利用できない場合のキーワードベース分類:\n\n")
        f.write("```python\n")
        f.write("bullish_keywords = ['great', 'amazing', 'bullish', 'moon', 'rocket', \n")
        f.write("                    'breakthrough', 'record', 'best']\n")
        f.write("bearish_keywords = ['problem', 'issue', 'difficult', 'challenge', \n")
        f.write("                    'delay', 'recall']\n")
        f.write("\n")
        f.write("text_lower = tweet_text.lower()\n")
        f.write("bullish_score = sum(1 for word in bullish_keywords if word in text_lower)\n")
        f.write("bearish_score = sum(1 for word in bearish_keywords if word in text_lower)\n")
        f.write("\n")
        f.write("if bullish_score > bearish_score:\n")
        f.write("    return 'BULLISH', 0.5, 'Keyword-based analysis'\n")
        f.write("elif bearish_score > bullish_score:\n")
        f.write("    return 'BEARISH', 0.5, 'Keyword-based analysis'\n")
        f.write("else:\n")
        f.write("    return 'NEUTRAL', 0.5, 'Keyword-based analysis'\n")
        f.write("```\n\n")
        
        # 7. Validation
        f.write("## 7. 分類の検証\n\n")
        
        # Cross-sentiment characteristics
        f.write("### 感情別の特徴分析\n\n")
        
        characteristics = ['is_product_announcement', 'contains_metrics', 'forward_looking']
        
        f.write("| 特徴 | BULLISH | BEARISH | NEUTRAL |\n")
        f.write("|------|---------|---------|----------|\n")
        
        for char in characteristics:
            row = f"| {char} |"
            for sentiment in ['BULLISH', 'BEARISH', 'NEUTRAL']:
                sentiment_df = df[df['sentiment'] == sentiment]
                if len(sentiment_df) > 0:
                    pct = (sentiment_df[char] == True).sum() / len(sentiment_df) * 100
                    row += f" {pct:.1f}% |"
                else:
                    row += " N/A |"
            f.write(row + "\n")
        
        # 8. Missing Categories
        f.write("\n## 8. 分類されないケース\n\n")
        f.write("以下のケースでは分類が困難または不適切:\n\n")
        f.write("1. **Tesla以外の話題**: SpaceXやNeuralink等の他社の話題\n")
        f.write("2. **リプライやリツイート**: 文脈が不完全な短い応答\n")
        f.write("3. **ジョークやミーム**: 真剣な意図が不明確\n")
        f.write("4. **極端に短いツイート**: 絵文字のみ、単語のみ\n\n")
        
        # 9. Reproducibility
        f.write("## 9. 再現性の確保\n\n")
        f.write("### 必要な環境\n")
        f.write("```bash\n")
        f.write("pip install openai==1.98.0 anthropic==0.60.0 pandas matplotlib seaborn\n")
        f.write("```\n\n")
        
        f.write("### 環境変数\n")
        f.write("```bash\n")
        f.write("export OPENAI_API_KEY='your-openai-key'\n")
        f.write("export ANTHROPIC_API_KEY='your-anthropic-key'\n")
        f.write("```\n\n")
        
        f.write("### 実行コマンド\n")
        f.write("```bash\n")
        f.write("python tesla_sentiment_analysis.py\n")
        f.write("python tesla_multi_condition_analysis.py\n")
        f.write("python sentiment_classification_methodology.py\n")
        f.write("```\n\n")
        
        f.write("## 10. 制限事項と改善点\n\n")
        f.write("1. **時間的文脈の欠如**: 過去のツイートやニュースとの関連が考慮されていない\n")
        f.write("2. **皮肉や暗示の理解**: LLMは皮肉や微妙な暗示を誤解する可能性\n")
        f.write("3. **市場の期待との乖離**: 強気でも市場の期待を下回れば株価は下落\n")
        f.write("4. **サンプルサイズ**: BEARISH tweets が少ない（6件のみ）\n\n")
        
        f.write("---\n\n")
        f.write("このレポートは完全な再現性を確保するため、すべての判断基準、")
        f.write("プロンプト、コード、および具体例を含んでいます。\n")


def main():
    """Run methodology analysis and generate report"""
    
    output_dir = '/Users/kumacmini/Library/CloudStorage/Dropbox/Workspace/Hypothesis-Verification'
    
    print("Analyzing sentiment classification methodology...")
    
    # Load data
    df, tweets = load_analysis_data()
    if df is None:
        print("Failed to load data")
        return
    
    # Analyze sentiment distribution
    sentiment_counts, confidence_stats, samples = analyze_sentiment_distribution(df)
    
    # Extract patterns
    patterns = extract_classification_patterns(df)
    
    # Create visualizations
    print("Creating methodology visualizations...")
    create_methodology_visualizations(df, output_dir)
    
    # Generate report
    print("Generating detailed methodology report...")
    generate_methodology_report(df, patterns, samples, output_dir)
    
    # Save detailed classification data
    classification_details = []
    for _, row in df.iterrows():
        detail = {
            'tweet_id': row['tweet_id'],
            'tweet_text': row['tweet_text'],
            'sentiment': row['sentiment'],
            'confidence': row['confidence'],
            'is_product_announcement': row['is_product_announcement'],
            'contains_metrics': row['contains_metrics'],
            'forward_looking': row['forward_looking'],
            'topic_category': row['topic_category'],
            'urgency_level': row['urgency_level']
        }
        classification_details.append(detail)
    
    # Save as JSON for complete transparency
    with open(f'{output_dir}/sentiment_classification_details.json', 'w', encoding='utf-8') as f:
        json.dump(classification_details, f, ensure_ascii=False, indent=2)
    
    print("Methodology documentation complete!")


if __name__ == "__main__":
    main()