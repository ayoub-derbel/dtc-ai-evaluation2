#!/usr/bin/env python3
"""Run prompt benchmarking tests for OBD-II diagnostics via OpenRouter."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import requests
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL_NAME = "openai/gpt-4o"
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
        "messages": [{"role": "user", "content": prompt}],
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


def render_prompt(prompt_template: str, vehicle: str, dtc_code: str) -> str:
    """Render known placeholders without using str.format() to avoid JSON brace collisions."""
    return (
        prompt_template.replace("{vehicle}", vehicle)
        .replace("{model}", vehicle)
        .replace("{dtc}", dtc_code)
        .replace("{dtc_code}", dtc_code)
    )


def ask_continue_or_stop() -> bool:
    """Return True to continue tests, False to stop and save current outputs."""
    print("An API error occurred.")
    print("Choose an option:")
    print("1) Continue testing")
    print("2) Stop now and generate responses.json + PDF with current results")

    while True:
        choice = input("Enter 1 or 2: ").strip()
        if choice == "1":
            return True
        if choice == "2":
            return False
        print("Invalid choice. Please enter 1 (continue) or 2 (stop).")


def wrap_text(text: str, max_chars: int = 110) -> list[str]:
    lines: list[str] = []
    for raw_line in text.splitlines() or [""]:
        words = raw_line.split()
        if not words:
            lines.append("")
            continue

        current = words[0]
        for word in words[1:]:
            trial = f"{current} {word}"
            if len(trial) <= max_chars:
                current = trial
            else:
                lines.append(current)
                current = word
        lines.append(current)
    return lines


def export_pdf(results: list[dict[str, str]], pdf_path: Path) -> None:
    pdf = canvas.Canvas(str(pdf_path), pagesize=A4)
    _, height = A4
    x_margin = 40
    y = height - 40

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(x_margin, y, "OBD2 AI Benchmark Report")
    y -= 24

    for index, item in enumerate(results, start=1):
        sections = [
            f"Test #{index}",
            f"Prompt ID: {item['prompt_id']}",
            f"Vehicle: {item['vehicle']}",
            f"DTC: {item['dtc']}",
            f"Model: {item['model']}",
            "Prompt sent:",
            item["prompt"],
            "Response received:",
            item["response"],
            "-" * 90,
        ]

        for section in sections:
            for line in wrap_text(section):
                if y <= 40:
                    pdf.showPage()
                    y = height - 40
                pdf.setFont("Helvetica", 10)
                pdf.drawString(x_margin, y, line)
                y -= 14
        y -= 8

    pdf.save()


def save_outputs(results: list[dict[str, str]], results_path: Path, pdf_path: Path) -> None:
    results_path.parent.mkdir(parents=True, exist_ok=True)
    with results_path.open("w", encoding="utf-8") as file:
        json.dump({"results": results}, file, indent=2)

    export_pdf(results, pdf_path)


def main() -> None:
    api_key = OPENROUTER_API_KEY

    if not api_key or api_key == "REPLACE_WITH_YOUR_OPENROUTER_API_KEY":
        raise RuntimeError("Set OPENROUTER_API_KEY directly in scripts/run_tests.py before running tests.")

    project_root = Path(__file__).resolve().parents[1]
    prompts_path = project_root / "prompts" / "prompts.json"
    tests_path = project_root / "dataset" / "dtc_tests.json"
    results_path = project_root / "results" / "responses.json"
    pdf_path = project_root / "results" / "responses_report.pdf"

    prompts_data = load_json(prompts_path)
    tests_data = load_json(tests_path)

    prompts = prompts_data.get("prompts", [])
    tests = tests_data.get("tests", [])

    all_results: list[dict[str, str]] = []
    stop_requested = False

    for prompt_item in prompts:
        if stop_requested:
            break

        prompt_id = prompt_item["id"]
        prompt_template = prompt_item["content"]

        for test_case in tests:
            vehicle = test_case["vehicle"]
            dtc_code = test_case["dtc"]
            prompt_text = render_prompt(prompt_template, vehicle, dtc_code)

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
                        "prompt_template": prompt_template,
                        "vehicle": vehicle,
                        "dtc": dtc_code,
                        "model": MODEL_NAME,
                        "prompt": prompt_text,
                        "response": response_text,
                    }
                )

                if ask_continue_or_stop():
                    continue

                stop_requested = True
                break

            print("Response received:")
            print(response_text)
            print("\n" + "-" * 80 + "\n")

            all_results.append(
                {
                    "prompt_id": prompt_id,
                    "prompt_template": prompt_template,
                    "vehicle": vehicle,
                    "dtc": dtc_code,
                    "model": MODEL_NAME,
                    "prompt": prompt_text,
                    "response": response_text,
                }
            )

    save_outputs(all_results, results_path, pdf_path)

    print(f"Saved {len(all_results)} results to {results_path}")
    print(f"Saved PDF report to {pdf_path}")


if __name__ == "__main__":
    main()
