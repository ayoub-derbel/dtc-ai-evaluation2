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
Set the API keys directly in each script:

- In `scripts/run_tests_gpt.py`, replace:

```python
OPENROUTER_API_KEY = "REPLACE_WITH_YOUR_OPENROUTER_API_KEY"
```

- In `scripts/run_tests_deepseek.py`, replace:

```python
DEEPSEEK_API_KEY = "REPLACE_WITH_YOUR_DEEPSEEK_API_KEY"
```

## Run Benchmark Tests
From inside the `OBD2-AI-Project` directory, run one script per model:

### GPT-4o (OpenRouter)
```bash
python scripts/run_tests_gpt.py
```
Outputs:
- `results/responses_gpt.json`
- `results/responses_gpt_report.pdf`

### DeepSeek R1 (DeepSeek direct API)
```bash
python scripts/run_tests_deepseek.py
```
Outputs:
- `results/responses_deepseek.json`
- `results/responses_deepseek_report.pdf`

Both scripts:
- load prompt strategies from `prompts/prompts.json`
- load test cases from `dataset/dtc_tests.json`
- print detailed runtime logs
- ask whether to continue or stop on API errors (e.g., 402), then save partial outputs

## GitHub Push Commands
After creating your GitHub repository, run:

```bash
git branch -M main
git remote add origin <GITHUB_REPO_URL>
git push -u origin main
```
