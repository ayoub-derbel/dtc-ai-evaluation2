# OBD2-AI-Project

## Project Purpose
OBD2-AI-Project benchmarks different prompt engineering strategies for an automotive diagnostic AI assistant. It combines OBD-II DTC test cases with vehicle models, sends generated prompts to OpenRouter, and records model responses for comparison.

## Project Structure
```text
OBD2-AI-Project/
├── prompts/
│   └── prompts.json
├── dataset/
│   └── dtc_tests.json
├── scripts/
│   └── run_tests.py
├── results/
│   └── responses.json
├── README.md
├── requirements.txt
└── .gitignore
```

## Installation
1. Clone or copy this project.
2. Create and activate a Python virtual environment (recommended).
3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Configure API keys
Set both API keys directly in the script:

1. Open `scripts/run_tests.py`
2. Replace:

```python
OPENROUTER_API_KEY = "REPLACE_WITH_YOUR_OPENROUTER_API_KEY"
DEEPSEEK_API_KEY = "REPLACE_WITH_YOUR_DEEPSEEK_API_KEY"
```

with your real keys.

## Run Benchmark Tests
From inside the `OBD2-AI-Project` directory, run:

```bash
python scripts/run_tests.py
```

The script will:
- load prompt strategies from `prompts/prompts.json`
- load test cases from `dataset/dtc_tests.json`
- send each prompt-test combination to two providers: OpenRouter (`openai/gpt-4o`) and DeepSeek direct API (`deepseek-reasoner`)
- print detailed runtime logs
- write all outputs to `results/responses.json` (including prompt, provider, model label, and API model for each response)
- generate a readable PDF report at `results/responses_report.pdf` containing each prompt and associated response
- on API errors (e.g., 402 Payment Required), asks whether to continue or stop and save partial outputs

## GitHub Push Commands
After creating your GitHub repository, run:

```bash
git branch -M main
git remote add origin <GITHUB_REPO_URL>
git push -u origin main
```
