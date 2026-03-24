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
Set API keys directly in scripts:

- In `scripts/run_tests_gpt.py`, replace:

```python
OPENROUTER_API_KEY = "REPLACE_WITH_YOUR_OPENROUTER_API_KEY"
```

- In `scripts/run_tests_deepseek.py`, replace:

```python
OPENROUTER_API_KEY = "REPLACE_WITH_YOUR_OPENROUTER_API_KEY"
```

- In `scripts/run_tests_groq.py`, replace:

```python
GROQ_API_KEY = "REPLACE_WITH_YOUR_GROQ_API_KEY"
```

- In `scripts/run_tests_groq_mixtral.py`, replace:

```python
GROQ_API_KEY = "REPLACE_WITH_YOUR_GROQ_API_KEY"
```

- In `scripts/run_tests_groq_deepseek_distill.py`, replace:

```python
GROQ_API_KEY = "REPLACE_WITH_YOUR_GROQ_API_KEY"
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

### DeepSeek R1 (via OpenRouter)
```bash
python scripts/run_tests_deepseek.py
```
Outputs:
- `results/responses_deepseek.json`
- `results/responses_deepseek_report.pdf`


### Groq (llama-3.3-70b-versatile)
```bash
python scripts/run_tests_groq.py
```
Outputs:
- `results/responses_groq.json`
- `results/responses_groq_report.pdf`


### Groq (Mixtral 8x7B)
```bash
python scripts/run_tests_groq_mixtral.py
```
Outputs:
- `results/responses_groq_mixtral.json`
- `results/responses_groq_mixtral_report.pdf`


### Groq (deepseek-r1-distill-llama-70b)
```bash
python scripts/run_tests_groq_deepseek_distill.py
```
Outputs:
- `results/responses_groq_deepseek_distill.json`
- `results/responses_groq_deepseek_distill_report.pdf`


### OpenRouter (anthropic/claude-sonnet-4.5)
```bash
python scripts/run_tests_claude_sonnet.py
```
Outputs:
- `results/responses_claude_sonnet.json`
- `results/responses_claude_sonnet_report.pdf`

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


## Export comparison to Excel
After running both scripts below:
- `python scripts/run_tests_gpt.py`
- `python scripts/run_tests_groq.py`
- `python scripts/run_tests_claude_sonnet.py`

Generate a comparison Excel file:

```bash
python scripts/export_comparison_excel.py
```

Output file:
- `results/AI_Test_Benchmark.xlsx`

Excel columns:
- `DTC`
- `Prompt`
- `Vehicle`
- `GPT-4O`
- `Llama-3.3-70B-Versatile`
- `anthropic/claude-sonnet-4.5`

The script generates merged blocks for `DTC` and `Prompt`, and writes real responses **per row combination** (`DTC + Prompt + Vehicle`) in `GPT-4O`, `Llama-3.3-70B-Versatile`, and `anthropic/claude-sonnet-4.5`. That means 12 distinct results per model for each DTC (4 prompts × 3 vehicles). If a result is missing, it writes `[Aucun résultat trouvé]`.

