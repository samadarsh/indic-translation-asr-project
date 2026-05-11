# Indic Translation and ASR Project

This repository contains the deliverables for the Tamizh Round 2 Hands-On Projects.
It is structured as a monorepo containing two distinct tasks:
1. **Evaluation of Indic Translation Models** (`task1_translation_evaluation/`)
2. **ASR-Based Transcription and Transliteration System** (`task2_asr_transliteration/`)

## 🛠️ Installation & Setup

You can install all dependencies required for both tasks using the root `requirements.txt`:

```bash
# 1. Clone the repository
git clone <your-repo-link>
cd indic-translation-asr-project

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

## 📁 Repository Structure

* `data/`: Contains all datasets, processed files, and results.
* `docs/`: System architectures and reports.
* `task1_translation_evaluation/`: Jupyter notebooks for batch translation and token analysis.
* `task2_asr_transliteration/`: Dockerized Gradio application for real-time transcription and transliteration.
* `presentation/`: Final presentation and demo links.

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
[MIT License]
