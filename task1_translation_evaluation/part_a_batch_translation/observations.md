# Part A — Observations

## Model
ai4bharat/indictrans2-en-indic-1B

## Dataset
FLORES-200 devtest split — 100 sentences (wikinews domain)

## Results
| Metric | Value |
|---|---|
| SacreBLEU Score | 22.42 |
| Brevity Penalty | 0.9638 |
| Length Ratio | 0.9645 |

## Interpretation
- A SacreBLEU score of 22.42 is considered good for English to Tamil translation
- Typical range for Indic language pairs: 5-15 (reasonable), 15-25 (good), 25+ (excellent)
- BP of 0.9638 indicates output length is very close to reference length
- Model is neither over-translating nor under-translating

## Why IndicTrans2 performs well
- Trained specifically on Indic language pairs including Tamil
- Uses Indic-aware SentencePiece tokenization that handles Tamil morphology
- Handles Tamil agglutinative structure better than general multilingual models
- IndicProcessor handles script normalization pre and post translation

## Limitations
- Evaluated on only 100 sentences (wikinews domain)
- Greedy decoding used for speed — beam search would improve score
- BLEU has known limitations for morphologically rich languages like Tamil
