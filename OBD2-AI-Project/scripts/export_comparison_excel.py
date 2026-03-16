#!/usr/bin/env python3
"""Generate AI benchmark Excel file populated with real GPT and Groq results."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Side

OUTPUT_FILENAME = "AI_Test_Benchmark.xlsx"
SHEET_NAME = "AI_Test_Benchmark"

DTCS = [
    "P0100",
    "P0110",
    "P0128",
    "P0171",
    "P0172",
    "P0300",
    "P0301",
    "P0420",
    "P0442",
    "P0455",
]

PROMPTS = [
    "prompt_v1_basic",
    "Expert_Diagnostic",
    "prompt_v2_fewshot",
    "prompt_v3_json",
]

VEHICLES = [
    "Ford Focus 2018",
    "Toyota Corolla 2018",
    "Volkswagen Golf 2019",
]


ResultKey = tuple[str, str, str]


def load_results(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"Results file not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        payload = json.load(file)

    return payload.get("results", [])


def build_model_map(items: list[dict[str, Any]], accepted_models: set[str]) -> dict[ResultKey, str]:
    result: dict[ResultKey, str] = {}

    for item in items:
        model = str(item.get("api_model", ""))
        if model not in accepted_models:
            continue

        key = (
            str(item.get("prompt_id", "")),
            str(item.get("vehicle", "")),
            str(item.get("dtc", "")),
        )
        result[key] = str(item.get("response", "")).strip()

    return result


def merged_cell_text(
    prompt_id: str,
    dtc: str,
    model_map: dict[ResultKey, str],
) -> str:
    lines: list[str] = []
    for vehicle in VEHICLES:
        response = model_map.get((prompt_id, vehicle, dtc), "")
        if not response:
            response = "[Résultat indisponible]"
        lines.append(f"{vehicle}:\n{response}")

    return "\n\n".join(lines)


def apply_style(sheet) -> None:
    thin = Side(style="thin", color="000000")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    max_row = sheet.max_row
    max_col = sheet.max_column

    for row in range(1, max_row + 1):
        for col in range(1, max_col + 1):
            cell = sheet.cell(row=row, column=col)
            cell.border = border
            if col == 3:  # Vehicle
                cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
            else:
                cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]

    gpt_results = load_results(project_root / "results" / "responses_gpt.json")
    groq_results = load_results(project_root / "results" / "responses_groq.json")

    gpt_map = build_model_map(gpt_results, {"openai/gpt-4o", "openai/gpt-4o-mini"})
    groq_map = build_model_map(groq_results, {"llama-3.3-70b-versatile"})

    output_path = project_root / "results" / OUTPUT_FILENAME

    wb = Workbook()
    ws = wb.active
    ws.title = SHEET_NAME

    headers = ["DTC", "Prompt", "Vehicle", "GPT-4O", "Llama-3.3-70B-Versatile"]
    ws.append(headers)

    current_row = 2

    for dtc in DTCS:
        dtc_start = current_row

        for prompt in PROMPTS:
            prompt_start = current_row

            for vehicle in VEHICLES:
                ws.cell(row=current_row, column=1, value=dtc)
                ws.cell(row=current_row, column=2, value=prompt)
                ws.cell(row=current_row, column=3, value=vehicle)
                current_row += 1

            prompt_end = current_row - 1

            ws.cell(row=prompt_start, column=4, value=merged_cell_text(prompt, dtc, gpt_map))
            ws.cell(row=prompt_start, column=5, value=merged_cell_text(prompt, dtc, groq_map))

            ws.merge_cells(start_row=prompt_start, start_column=2, end_row=prompt_end, end_column=2)
            ws.merge_cells(start_row=prompt_start, start_column=4, end_row=prompt_end, end_column=4)
            ws.merge_cells(start_row=prompt_start, start_column=5, end_row=prompt_end, end_column=5)

        dtc_end = current_row - 1
        ws.merge_cells(start_row=dtc_start, start_column=1, end_row=dtc_end, end_column=1)

    ws.column_dimensions["A"].width = 12
    ws.column_dimensions["B"].width = 50
    ws.column_dimensions["C"].width = 20
    ws.column_dimensions["D"].width = 25
    ws.column_dimensions["E"].width = 25

    apply_style(ws)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output_path)
    print(f"Saved Excel file to {output_path}")


if __name__ == "__main__":
    main()
