# Part C — Indic Token Behavior Analysis

## Objective
Investigate how Tamil-specific tokens are handled across 5 translation models.

## Models Analysed
- IndicTrans2 (ai4bharat/indictrans2-en-indic-1B)
- NLLB-600M (facebook/nllb-200-distilled-600M)
- mT5-base (google/mt5-base)
- OpusMT-mul (Helsinki-NLP/opus-mt-en-mul)
- MADLAD-3B (google/madlad400-3b-mt)

## Summary Results
| Model       | Avg Tokens | Tamil Tokens | Tamil Ratio | Chars/Token | Unicode Frag | Memory (MB) |
|-------------|-----------|--------------|-------------|-------------|--------------|-------------|
| IndicTrans2 | 170.9     | 0.0          | 0.000       | 1.004       | 0.861        | 102.268     |
| MADLAD-3B   | 57.1      | 49.2         | 0.850       | 2.678       | 0.237        | 11.612      |
| NLLB-600M   | 50.4      | 45.6         | 0.891       | 3.035       | 0.241        | 9.093       |
| OpusMT-mul  | 164.6     | 140.9        | 0.848       | 0.929       | 0.850        | 96.134      |
| mT5-base    | 49.5      | 42.2         | 0.843       | 3.097       | 0.148        | 8.825       |

## Finding 1 — IndicTrans2 Tamil Token Count is Zero
IndicTrans2 shows 0 Tamil tokens despite producing Tamil output in Part A.
This is because IndicProcessor romanizes Tamil script internally before
tokenization — the tokenizer never sees native Tamil Unicode characters.
Instead it works with a latinized representation, which explains:
- avg_chars_per_token of 1.004 (single latin characters)
- unicode_fragmentation of 0.861 (86% single-character tokens)
- 0 Tamil Unicode tokens detected

This is by design — IndicTrans2 operates in a transliterated space internally
and converts back to Tamil script only at the output stage via postprocessing.

## Finding 2 — OpusMT-mul Severely Fragments Tamil
OpusMT-mul has the highest unicode fragmentation (0.850) among models that
actually process Tamil script. With avg_chars_per_token of only 0.929 —
less than 1 character per token — it is splitting Tamil words into individual
Unicode codepoints. This is classic English-centric BPE tokenizer behaviour:
lacking Tamil subword units in its vocabulary, it falls back to single
Unicode character tokens.

## Finding 3 — mT5-base is the Most Efficient Tamil Tokenizer
mT5-base achieves:
- Lowest unicode fragmentation (0.148) — least character-level splitting
- Highest avg chars per token (3.097) — each token carries more information
- Lowest memory footprint (8.825 MB)
This confirms mT5's SentencePiece vocabulary has the best Tamil subword
coverage among the 5 models, learned from large-scale multilingual pretraining.

Note: mT5-base ranks highest on tokenizer-level metrics but produces invalid
Tamil translations for seq2seq MT (as seen in Part B). Tokenizer efficiency
does not equal translation quality.

## Finding 4 — NLLB-600M is the Best Balance
NLLB-600M achieves:
- Highest Tamil token ratio (0.891) — 89.1% of tokens are Tamil
- Good avg chars per token (3.035)
- Low memory footprint (9.093 MB)
- Low unicode fragmentation (0.241)
Making it the best overall model for Tamil tokenization in real translation
scenarios where the model must also produce valid Tamil output.

## Finding 5 — Tamil's Agglutinative Structure
Tamil is agglutinative — suffixes for tense, case, person, and number are
attached directly to root words. A single Tamil word like
'படிக்கவேண்டியிருந்தது' (had to have studied) contains multiple morphemes.
Tokenizers with poor Tamil coverage split these into many single-character
tokens, causing token explosion and dramatically increasing Transformer
attention cost (scales as sequence_length²).

## Finding 6 — Memory Footprint Impact
The memory cost difference is dramatic (figures are illustrative estimates
based on a fixed hidden_size=768 — useful for relative comparison, not
absolute production benchmarks):
- IndicTrans2: 102.268 MB (due to 170.9 avg tokens)
- OpusMT-mul:  96.134 MB (due to 164.6 avg tokens)
- NLLB-600M:    9.093 MB (due to 50.4 avg tokens)
- mT5-base:     8.825 MB (due to 49.5 avg tokens)

IndicTrans2 and OpusMT require ~11x more Transformer memory than NLLB
and mT5 for the same sentences. In production, this translates directly
to higher GPU costs and lower throughput.

## Finding 7 — SentencePiece vs BPE
Models using SentencePiece (NLLB, MADLAD, mT5, IndicTrans2) learn subword
units directly from raw multilingual text without pre-tokenization rules.
This makes them naturally better at handling Tamil's Unicode-heavy,
agglutinative structure. OpusMT uses BPE which starts from characters and
merges frequent byte pairs — effective for European languages but produces
excessive fragmentation for Tamil due to its complex Unicode syllable blocks.

## Finding 8 — Vocabulary Coverage
Larger vocabulary = better Tamil coverage:
- NLLB-600M:  256,206 tokens (trained on 200 languages)
- MADLAD-3B:  256,000 tokens (trained on 400 languages)
- mT5-base:   250,100 tokens
- IndicTrans2: 64,000 tokens (Indic-specific but romanized)
- OpusMT-mul:  65,000 tokens (European-focused)

## Key Insight — Tokenizer Efficiency ≠ Translation Quality
A critical distinction emerges across Parts B and C: tokenizer efficiency
does not equal translation quality. mT5-base ranks highest on tokenizer
metrics (lowest fragmentation, highest chars per token, lowest memory footprint)
but produces invalid Tamil translations for seq2seq MT tasks. NLLB-600M
provides the best real-world balance — efficient tokenization AND valid Tamil
output. This tension between tokenizer-level metrics and end-to-end translation
quality is a key analytical finding of Task 1.

## Conclusion
mT5-base has the most efficient Tamil tokenization (lowest fragmentation,
highest chars per token, lowest memory). NLLB-600M is the best choice for
actual Tamil translation tasks combining efficiency with valid output quality.
IndicTrans2's unusual metrics (0 Tamil tokens, high fragmentation) are entirely
due to its internal romanization — not a weakness but a deliberate design choice
that enables its superior translation quality (BLEU 22.42 in Part A).
English-centric models like OpusMT-mul should be avoided for Tamil NLP tasks
due to severe Unicode fragmentation and extreme memory costs.
