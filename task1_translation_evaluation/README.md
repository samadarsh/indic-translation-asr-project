# Task 1 — Evaluation of Indic Translation Models

This directory contains three Jupyter notebooks evaluating English→Tamil
translation models across translation quality, token-based analysis, and
Indic token behavior.

---

## Project Structure

```
task1_translation_evaluation/
├── README.md
├── part_a_batch_translation/
│   ├── part_a_translation_evaluation.ipynb
│   ├── translation_outputs.csv
│   ├── sacrebleu_results.csv
│   └── observations.md
├── part_b_token_analysis/
│   ├── part_b_token_eda.ipynb
│   ├── token_counts.csv
│   ├── engineered_features.csv
│   ├── translation_outputs.csv
│   ├── plots/
│   │   ├── histogram_token_counts.png
│   │   ├── boxplot_expansion_ratios.png
│   │   ├── scatter_source_vs_target.png
│   │   └── bar_avg_expansion.png
│   └── observations.md
└── part_c_indic_token_behavior/
    ├── part_c_indic_token_analysis.ipynb
    ├── tokenization_comparison.csv
    ├── tamil_token_patterns.csv
    ├── plots/
    │   ├── avg_chars_per_token.png
    │   ├── unicode_fragmentation.png
    │   ├── memory_footprint.png
    │   ├── tamil_token_coverage.png
    │   ├── vocab_size.png
    │   └── rare_token_rate.png
    └── observations.md
```

---

## Installation

Run all commands from the **repository root** (where `requirements.txt` lives).

```bash
# 1. Create virtual environment
python -m venv .venv

# 2. Activate — Mac/Linux
source .venv/bin/activate

# Activate — Windows
.venv\Scripts\activate

# 3. Upgrade pip (recommended)
pip install --upgrade pip

# 4. Install all dependencies
pip install -r requirements.txt
```

---

## How to Run

Open any `.ipynb` notebook in **Jupyter Notebook**, **JupyterLab**,
**VS Code** (with the Jupyter extension), or **Google Colab**.

> **Important:** All notebooks use relative paths to load data from
> `../../data/raw/translation_dataset.csv`. Open and run each notebook
> from its own subdirectory to ensure paths resolve correctly. If you
> see a `FileNotFoundError`, check that your working directory matches
> the notebook's folder (e.g., `cd` into that part's directory).

**VS Code users:** Install the Jupyter extension, open the repo root
folder in VS Code, navigate to the notebook file and click
"Run All" or run cells individually with Shift+Enter.

**Google Colab users:** Upload the notebook and
`data/raw/translation_dataset.csv`, then recreate the `data/raw/`
folder structure or update the path in the dataset loading cell from
`../../data/raw/translation_dataset.csv` to the actual uploaded path.

Run notebooks in this order:
```
1. part_a_batch_translation/part_a_translation_evaluation.ipynb
2. part_b_token_analysis/part_b_token_eda.ipynb
3. part_c_indic_token_behavior/part_c_indic_token_analysis.ipynb
```

---

## Dataset

**FLORES-200** devtest split — sourced directly from the raw dataset
files. Placed at `data/raw/translation_dataset.csv`. The full CSV spans
multiple FLORES domains (wikinews, wikibooks, wikivoyage); Part A uses
the first 100 rows, while Parts B and C use the first 10 rows. This slice
draws predominantly from the wikinews domain due to row ordering.

- 1012 sentences available (100 used for Part A, 10 for Parts B and C)
- Columns: `id`, `english`, `tamil_reference`, `domain`, `topic`
- Human-verified Tamil reference translations — required for sacreBLEU

---

## Models Used

### Part A — Batch Translation & Evaluation
| Model | HuggingFace ID |
|---|---|
| IndicTrans2 | `ai4bharat/indictrans2-en-indic-1B` |

### Parts B & C — Token Analysis & Indic Token Behavior
| Model | HuggingFace ID | Note |
|---|---|---|
| IndicTrans2 | `ai4bharat/indictrans2-en-indic-1B` | |
| NLLB-600M | `facebook/nllb-200-distilled-600M` | |
| mT5-base | `google/mt5-base` | |
| OpusMT-mul | `Helsinki-NLP/opus-mt-en-mul` | See note below |
| MADLAD-3B | `google/madlad400-3b-mt` | See note below |

### Model Substitution Notes
- **`Helsinki-NLP/opus-mt-en-ta`** does not exist as a public model on
  Hugging Face. `Helsinki-NLP/opus-mt-en-mul` (English → multilingual)
  was used as a direct replacement — it supports Tamil as a target language
  and shares the same MarianMT tokenizer architecture, making it fully
  valid for tokenizer-level analysis in Parts B and C.
- **`google/madlad400-1b-mt`** does not exist publicly.
  `google/madlad400-3b-mt` was used — it is the smallest publicly
  available MADLAD variant.

---

## Results Summary

### Part A — SacreBLEU Evaluation
| Metric | Value |
|---|---|
| Model | ai4bharat/indictrans2-en-indic-1B |
| Sentences evaluated | 100 |
| SacreBLEU Score | **22.42** |
| Brevity Penalty | 0.9638 |
| Length Ratio | 0.9645 |

A score of 22.42 is considered good for English→Tamil translation.
Typical range: 5–15 (reasonable), 15–25 (good), 25+ (excellent).

### Part B — Token Analysis
| Model | Avg Expansion Ratio | Valid Tamil Output |
|---|---|---|
| IndicTrans2 | 5.256 | ✅ |
| NLLB-600M | 1.366 | ✅ |
| MADLAD-3B | 1.641 | ✅ |
| OpusMT-mul | 2.421 | ✅ |
| mT5-base | 0.200 | ❌ (not fine-tuned for MT) |

**NLLB-600M** has the lowest expansion ratio (1.366) among models
producing valid Tamil output.

### Part C — Indic Token Behavior
| Model | Avg Chars/Token | Unicode Frag | Memory (MB) |
|---|---|---|---|
| IndicTrans2 | 1.004 | 0.861 | 102.268 |
| NLLB-600M | 3.035 | 0.241 | 9.093 |
| mT5-base | 3.097 | 0.148 | 8.825 |
| OpusMT-mul | 0.929 | 0.850 | 96.134 |
| MADLAD-3B | 2.678 | 0.237 | 11.612 |

Memory figures are illustrative estimates based on fixed hidden_size=768,
useful for relative comparison — not absolute production benchmarks.

**Key insight:** Tokenizer efficiency ≠ translation quality. mT5-base
ranks best on tokenizer metrics but produces invalid Tamil translations.
NLLB-600M provides the best real-world balance — efficient tokenization
AND valid Tamil output. IndicTrans2 achieves the strongest BLEU score
(22.42) and is a strong baseline for English→Tamil translation despite
high token counts, due to its internal romanization preprocessing via
IndicProcessor.

---

## Key Findings

- IndicTrans2 achieves the strongest BLEU score (22.42) and is a strong
  baseline for English→Tamil translation
- NLLB-600M is the most token-efficient model for valid Tamil translation
  (expansion ratio 1.366, memory 9.093 MB)
- OpusMT-mul severely fragments Tamil Unicode (85% single-character tokens)
  and should be avoided for Tamil NLP tasks
- IndicTrans2's high token count in Parts B and C is an artifact of its
  internal romanization design — not a translation quality weakness
- Tamil's agglutinative structure causes token explosion in English-centric
  tokenizers, resulting in up to 11x higher Transformer memory costs
