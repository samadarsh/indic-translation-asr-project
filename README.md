# Indic Translation and ASR Project

This repository contains the deliverables for the Tamizh Round 2 Hands-On Projects.
It is structured as a monorepo containing two distinct tasks:
1. **Evaluation of Indic Translation Models** (`task1_translation_evaluation/`)
2. **ASR-Based Transcription and Transliteration System** (`task2_asr_transliteration/`)

## 🛠️ Installation & Setup

You can install all dependencies required for both tasks using the root `requirements.txt`:

```bash
# 1. Clone the repository
git clone https://github.com/samadarsh/indic-translation-asr-project.git
cd indic-translation-asr-project

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

## 📁 Repository Structure

* `data/`: Datasets, processed outputs, plots, and results.
* `docs/`: System architecture diagrams, summary reports, and demo recording links.
* `task1_translation_evaluation/`: Jupyter notebooks for batch translation and token analysis.
* `task2_asr_transliteration/`: Dockerized Gradio application for real-time transcription and transliteration.
* `presentation/`: Final presentation and demo links.

## 📊 Key Findings & Results

### Task 1: Indic Translation Evaluation
* **Batch Translation (Part A):** The `ai4bharat/indictrans2-en-indic-1B` model served as a strong baseline, achieving a **SacreBLEU Score of 22.42**, with a Brevity Penalty of **0.9638** and a Length Ratio of **0.9645** on the FLORES-200 Tamil evaluation set.
* **Token Analysis (Part B):** Cross-evaluated 5 models (`indictrans2`, `nllb`, `mt5-base`, `opus-mt-en-mul`, `madlad400-3b-mt`). The analysis revealed significant variance in token expansion ratios across English-to-Tamil translations depending on the model's vocabulary and subword tokenization strategies.
* **Indic Token Behavior (Part C):** Investigated Tamil-specific Unicode fragmentation and subword splitting, highlighting how agglutinative linguistic properties challenge non-specialized BPE tokenizers, whereas Indic-native models demonstrated far superior character-per-token efficiency.

### Task 2: ASR & Transliteration App
* **Robust Transcription:** Utilizing Hugging Face's `openai/whisper-medium`, the system accurately transcribes spoken Tamil.
* **Romanized Output:** A custom Tamil-aware grapheme romanizer converts Tamil script to clean ASCII Latin text (long vowels doubled, retroflex consonants capitalized), producing output that renders correctly in any plain-text environment.
* **Production-Ready Architecture:** Designed with a thread-safe `queue.Queue` buffer manager to process audio chunks efficiently without memory overflow, bundled into a responsive Gradio UI and fully containerized via Docker.

## 🚀 Running the Tasks

### Task 1: Indic Translation Evaluation
Navigate to `task1_translation_evaluation/` and start Jupyter Notebook:
```bash
jupyter notebook
```
Follow the instructions inside the notebooks for Part A, Part B, and Part C.

### Task 2: ASR & Transliteration App
Navigate to `task2_asr_transliteration/` to run the application using Docker:

```bash
cd task2_asr_transliteration
docker-compose up --build
```
The application will be accessible at `http://localhost:7860`.

## 📜 License
Released under the [MIT License](LICENSE).
