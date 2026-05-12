# Part B — Observations

## Models Compared
- IndicTrans2 (ai4bharat/indictrans2-en-indic-1B)
- MADLAD-3B (google/madlad400-3b-mt)
- NLLB-600M (facebook/nllb-200-distilled-600M)
- OpusMT-mul (Helsinki-NLP/opus-mt-en-mul)
- mT5-base (google/mt5-base)

## Sentences Evaluated
10 sentences from FLORES-200 devtest split (wikinews domain)

## Summary Results
| Model       | Avg Src Tokens | Avg Tgt Tokens | Avg Expansion | Fragmentation | UNK Rate |
|-------------|---------------|----------------|---------------|---------------|----------|
| IndicTrans2 | 32.2          | 171.7          | 5.256         | 0.000         | 0.058    |
| MADLAD-3B   | 34.1          | 55.4           | 1.641         | 0.095         | 0.000    |
| NLLB-600M   | 32.8          | 43.4           | 1.366         | 0.095         | 0.000    |
| OpusMT-mul  | 30.2          | 61.7           | 2.421         | 0.004         | 0.000    |
| mT5-base    | 35.9          | 6.3            | 0.200         | 0.000         | 0.000    |

## Key Finding 1 — Model with Lowest Expansion Ratio
mT5-base has the lowest expansion ratio (0.200), but this is misleading —
mT5-base is not fine-tuned for translation and produces garbage output
(e.g. '<extra_id_0> a few.') with very few tokens, giving an artificially
low expansion ratio. Excluding mT5-base, NLLB-600M has the genuinely
lowest expansion ratio (1.366) among models that produce valid Tamil output.

## Key Finding 2 — NLLB-600M is the Best Performing Model
NLLB-600M achieves the lowest expansion ratio (1.366) among valid translation
models, meaning it represents Tamil most efficiently. Its SentencePiece BPE
vocabulary was trained on large-scale multilingual data including Tamil,
giving it strong coverage of Tamil subword units and reducing fragmentation.

## Key Finding 3 — IndicTrans2 High Expansion
IndicTrans2 shows the highest expansion ratio (5.256) among valid models.
This is because its tokenizer uses an internal romanization preprocessing
step via IndicProcessor — when Tamil script is fed directly for tokenization,
the character-level encoding inflates the raw token count significantly.

## Key Finding 4 — Fragmentation
MADLAD-3B and NLLB-600M both show fragmentation of 0.095, meaning roughly
9.5% of Tamil tokens are subword fragments. IndicTrans2 and mT5-base show
zero fragmentation — IndicTrans2 because its romanized tokens are whole units,
mT5-base because its output is too short to fragment meaningfully.

## Key Finding 5 — Unknown Token Rate
Only IndicTrans2 shows a non-zero UNK rate (0.058), indicating its vocabulary
does not fully cover all Tamil Unicode characters present in the generated
translations. All other models show zero UNK rates, suggesting broader
Tamil Unicode coverage in their SentencePiece vocabularies.

## Why Tamil Expands Token Counts
Tamil is agglutinative — grammatical information (tense, case, person, number)
is encoded as suffixes on the root word. A single Tamil word like
'படிக்கவேண்டியிருந்தது' encodes what English expresses as
'had to have studied' — multiple English tokens become one Tamil word,
but subword tokenizers still split it into many pieces.

## Conclusion
NLLB-600M is the most token-efficient model for valid English→Tamil translation
with an expansion ratio of 1.366 and zero UNK rate. IndicTrans2's high expansion
is an artifact of its internal romanization preprocessing. mT5-base produces
invalid translations for this task as it is not fine-tuned for seq2seq translation.
