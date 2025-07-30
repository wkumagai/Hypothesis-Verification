# Tesla Tweet Sentiment Classification Methodology

## 完全な再現可能性のための詳細文書

**作成日時**: 2025-07-31 00:02:11

## 1. 分類プロセス

### 使用したLLMと設定
- **Primary LLM**: OpenAI GPT-3.5-turbo
- **Fallback LLM**: Anthropic Claude-3-haiku
- **Temperature**: 0.1 (一貫性のため低温設定)
- **Max Tokens**: 150

### LLMプロンプト（完全版）
```
Analyze the following tweet from Elon Musk about Tesla and classify it as:
1. BULLISH (positive about Tesla's future, products, or performance)
2. BEARISH (negative or cautious about Tesla)
3. NEUTRAL (factual, mixed, or unclear sentiment)

Also provide a confidence score (0-1) and a brief reason.

Tweet: "{tweet_text}"

Respond in JSON format:
{"sentiment": "BULLISH/BEARISH/NEUTRAL", "confidence": 0.0-1.0, "reason": "brief explanation"}
```

## 2. 詳細な分類基準

### BULLISH（強気）の判断基準
以下の要素を含むツイートは強気と分類される傾向:

**キーワード・フレーズ**:
- ポジティブな形容詞: amazing, great, incredible, breakthrough, revolutionary
- 成果を示す言葉: record, milestone, achievement, success, leading
- 将来への期待: excited, proud, game-changing
- 絵文字: 🚀, ❤️, 🔥

**文脈的要素**:
- 新製品や機能の成功を報告
- 生産記録や販売記録の達成
- 技術的ブレークスルーの発表
- チームや製品への賞賛

### BEARISH（弱気）の判断基準
以下の要素を含むツイートは弱気と分類される傾向:

**キーワード・フレーズ**:
- 問題を示す言葉: problem, issue, difficult, challenge, delay
- ネガティブな結果: recall, investigation, concern, risk
- 失敗や挫折: failure, disappointing, setback, unfortunately

**文脈的要素**:
- 生産や配送の遅延
- 技術的な問題や欠陥
- 規制上の懸念や調査
- 目標未達成の報告

### NEUTRAL（中立）の判断基準
以下の要素を含むツイートは中立と分類される傾向:

**キーワード・フレーズ**:
- 事実報告: update, information, fact, data, report
- 進行状況: currently, working on, in progress, planned
- 客観的記述: scheduled, status, details

**文脈的要素**:
- 感情的な判断を含まない事実の報告
- 技術仕様や数値データの共有
- プロセスや手順の説明
- ポジティブとネガティブが混在

## 3. 実際の分類結果の分布

### 感情分類の内訳
| 感情 | 件数 | 割合 | 平均信頼度 |
|------|------|------|------------|
| BULLISH | 95 | 76.6% | 0.805 |
| BEARISH | 6 | 4.8% | 0.817 |
| NEUTRAL | 23 | 18.5% | 0.674 |

## 4. 具体的な分類例

### BULLISH の例（信頼度の高い順）

**例1** (信頼度: 0.900)
```
Just left the @Tesla design studio.

Most epic demo ever by end of year. 

Ever.
```

**例2** (信頼度: 0.900)
```
The first fully autonomous delivery of a Tesla Model Y from factory to a customer home across town, including highways, was just completed a day ahead of schedule!!

Congratulations to the @Tesla_AI t
```

**例3** (信頼度: 0.900)
```
Super congratulations to the @Tesla_AI software &amp; chip design teams on a successful @Robotaxi launch!!

Culmination of a decade of hard work.

Both the AI chip and software teams were built from s
```

### BEARISH の例（信頼度の高い順）

**例1** (信頼度: 0.900)
```
Turns out that we can get radical leftists to burn down any government department if we just put a Tesla logo on it! 

This will be so easy. They’ll never figure it out.
```

**例2** (信頼度: 0.800)
```
Many of those doing these “takedowns” have also sold Tesla stock short, so they benefit financially from a drop in the stock
```

**例3** (信頼度: 0.800)
```
The worst bad guys are the ones who are financing the Tesla terror campaign 
https://t.co/nHyn73wuuz
```

### NEUTRAL の例（信頼度の高い順）

**例1** (信頼度: 1.000)
```
Tesla
```

**例2** (信頼度: 0.800)
```
@LauraLoomer @stclairashley @Tesla I don’t know if the child is mine or not, but am not against finding out. No court order is needed. 

Despite not knowing for sure, I have given Ashley $2.5M and am 
```

**例3** (信頼度: 0.800)
```
@DefiyantlyFree @DarrigoMelanie Yeah. Tesla losses were high for many years, so carry forward. 

Super majority of profit is from production and sales overseas, not US. 

But the point I am making IS 
```

## 5. エッジケースと曖昧な例

### 低信頼度の例（分類が困難だったケース）

**NEUTRAL** (信頼度: 0.500)
```
.@Tesla_AI...
```

**NEUTRAL** (信頼度: 0.500)
```
@SawyerMerritt @Tesla Wow...
```

**NEUTRAL** (信頼度: 0.500)
```
@Gfilche @Tesla A crazy amount of execution is needed to get there, but I do see a path to world’s biggest company...
```

**NEUTRAL** (信頼度: 0.500)
```
@amuse Wow, they’re totally insane. 

Death threats, shooting up Tesla stores and burning down Superchargers are definitely not “legitimate forms of protest”!...
```

**NEUTRAL** (信頼度: 0.500)
```
@Eric_Schmitt @realDonaldTrump @Tesla @X ❤️...
```

## 6. フォールバック分類

LLMが利用できない場合のキーワードベース分類:

```python
bullish_keywords = ['great', 'amazing', 'bullish', 'moon', 'rocket', 
                    'breakthrough', 'record', 'best']
bearish_keywords = ['problem', 'issue', 'difficult', 'challenge', 
                    'delay', 'recall']

text_lower = tweet_text.lower()
bullish_score = sum(1 for word in bullish_keywords if word in text_lower)
bearish_score = sum(1 for word in bearish_keywords if word in text_lower)

if bullish_score > bearish_score:
    return 'BULLISH', 0.5, 'Keyword-based analysis'
elif bearish_score > bullish_score:
    return 'BEARISH', 0.5, 'Keyword-based analysis'
else:
    return 'NEUTRAL', 0.5, 'Keyword-based analysis'
```

## 7. 分類の検証

### 感情別の特徴分析

| 特徴 | BULLISH | BEARISH | NEUTRAL |
|------|---------|---------|----------|
| is_product_announcement | 49.5% | 0.0% | 8.7% |
| contains_metrics | 14.7% | 16.7% | 8.7% |
| forward_looking | 64.2% | 33.3% | 26.1% |

## 8. 分類されないケース

以下のケースでは分類が困難または不適切:

1. **Tesla以外の話題**: SpaceXやNeuralink等の他社の話題
2. **リプライやリツイート**: 文脈が不完全な短い応答
3. **ジョークやミーム**: 真剣な意図が不明確
4. **極端に短いツイート**: 絵文字のみ、単語のみ

## 9. 再現性の確保

### 必要な環境
```bash
pip install openai==1.98.0 anthropic==0.60.0 pandas matplotlib seaborn
```

### 環境変数
```bash
export OPENAI_API_KEY='your-openai-key'
export ANTHROPIC_API_KEY='your-anthropic-key'
```

### 実行コマンド
```bash
python tesla_sentiment_analysis.py
python tesla_multi_condition_analysis.py
python sentiment_classification_methodology.py
```

## 10. 制限事項と改善点

1. **時間的文脈の欠如**: 過去のツイートやニュースとの関連が考慮されていない
2. **皮肉や暗示の理解**: LLMは皮肉や微妙な暗示を誤解する可能性
3. **市場の期待との乖離**: 強気でも市場の期待を下回れば株価は下落
4. **サンプルサイズ**: BEARISH tweets が少ない（6件のみ）

---

このレポートは完全な再現性を確保するため、すべての判断基準、プロンプト、コード、および具体例を含んでいます。
