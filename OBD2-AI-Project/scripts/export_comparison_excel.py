#!/usr/bin/env python3
"""Export benchmark responses from GPT and Groq into a comparison Excel file."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from openpyxl import Workbook


def load_results(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"Results file not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    return data.get("results", [])


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    gpt_results_path = project_root / "results" / "responses_gpt.json"
    groq_results_path = project_root / "results" / "responses_groq.json"
    output_path = project_root / "results" / "benchmark_comparison.xlsx"

    gpt_results = load_results(gpt_results_path)
    groq_results = load_results(groq_results_path)

    table: dict[tuple[str, str, str], dict[str, str]] = {}

    for item in gpt_results:
        key = (item.get("prompt_id", ""), item.get("vehicle", ""), item.get("dtc", ""))
        row = table.setdefault(key, {"gpt": "", "llama": ""})

        api_model = item.get("api_model", "")
        if api_model in {"openai/gpt-4o-mini", "openai/gpt-4o"}:
            row["gpt"] = item.get("response", "")

    for item in groq_results:
        key = (item.get("prompt_id", ""), item.get("vehicle", ""), item.get("dtc", ""))
        row = table.setdefault(key, {"gpt": "", "llama": ""})

        api_model = item.get("api_model", "")
        model_label = item.get("model_label", "")
        if api_model == "llama-3.3-70b-versatile" or model_label == "llama-3.3-70b-versatile":
            row["llama"] = item.get("response", "")

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "benchmark_comparison"

    sheet.append(
        [
            "Prompt ID",
            "Vehicle",
            "DTC",
            "GPT-4o-mini",
            "llama-3.3-70b-versatile",
        ]
    )

    for (prompt_id, vehicle, dtc) in sorted(table.keys()):
        row_data = table[(prompt_id, vehicle, dtc)]
        sheet.append([prompt_id, vehicle, dtc, row_data["gpt"], row_data["llama"]])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(output_path)

    print(f"Saved Excel comparison file to {output_path}")


if __name__ == "__main__":
    main()
