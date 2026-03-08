#!/usr/bin/env python3
"""Run prompt benchmarking tests for OBD-II diagnostics via OpenRouter."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import requests

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL_NAME = "openai/gpt-4o-mini"
MAX_TOKENS = 1000
OPENROUTER_API_KEY = "REPLACE_WITH_YOUR_OPENROUTER_API_KEY"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def call_openrouter(api_key: str, prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "OBD2-AI-Test",
    }

    payload = {
        "model": MODEL_NAME,
        "max_tokens": MAX_TOKENS,
        "messages": [
            {"role": "user", "content": prompt},
        ],
    }

    response = requests.post(
        OPENROUTER_URL,
        headers=headers,
        json=payload,
        timeout=60,
    )
    response.raise_for_status()

    data = response.json()
    return data["choices"][0]["message"]["content"].strip()


def main() -> None:
    api_key = OPENROUTER_API_KEY

    if not api_key or api_key == "REPLACE_WITH_YOUR_OPENROUTER_API_KEY":
        raise RuntimeError("Set OPENROUTER_API_KEY directly in scripts/run_tests.py before running tests.")

    project_root = Path(__file__).resolve().parents[1]
    prompts_path = project_root / "prompts" / "prompts.json"
    tests_path = project_root / "dataset" / "dtc_tests.json"
    results_path = project_root / "results" / "responses.json"

    prompts_data = load_json(prompts_path)
    tests_data = load_json(tests_path)

    prompts = prompts_data.get("prompts", [])
    tests = tests_data.get("tests", [])

    all_results: list[dict[str, str]] = []

    for prompt_item in prompts:
        prompt_id = prompt_item["id"]
        prompt_template = prompt_item["content"]

        for test_case in tests:
            vehicle = test_case["vehicle"]
            dtc_code = test_case["dtc"]
            prompt_text = prompt_template.format(vehicle=vehicle, dtc_code=dtc_code)

            print("Running test")
            print(f"Prompt: {prompt_id}")
            print(f"Vehicle: {vehicle}")
            print(f"DTC: {dtc_code}")
            print(f"Model: {MODEL_NAME}\n")
            print("Prompt sent:")
            print(prompt_text)
            print()

            try:
                response_text = call_openrouter(api_key, prompt_text)
            except requests.RequestException as exc:
                response_text = f"ERROR: {exc}"

            print("Response received:")
            print(response_text)
            print("\n" + "-" * 80 + "\n")

            all_results.append(
                {
                    "prompt_id": prompt_id,
                    "vehicle": vehicle,
                    "dtc": dtc_code,
                    "model": MODEL_NAME,
                    "prompt": prompt_text,
                    "response": response_text,
                }
            )

    results_path.parent.mkdir(parents=True, exist_ok=True)
    with results_path.open("w", encoding="utf-8") as file:
        json.dump({"results": all_results}, file, indent=2)

    print(f"Saved {len(all_results)} results to {results_path}")


if __name__ == "__main__":
    main()
