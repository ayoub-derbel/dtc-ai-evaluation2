#!/usr/bin/env python3
"""Generate AI benchmark Excel populated with real GPT and Groq results per combination."""

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


def load_results(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    return data.get("results", [])


def build_index(results: list[dict[str, Any]]) -> dict[tuple[str, str, str], str]:
    index: dict[tuple[str, str, str], str] = {}
    for item in results:
        key = (item.get("prompt_id", ""), item.get("vehicle", ""), item.get("dtc", ""))
        index[key] = item.get("response", "")
    return index


def apply_style(sheet) -> None:
    thin = Side(style="thin", color="000000")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    max_row = sheet.max_row
    max_col = sheet.max_column

    for row in range(1, max_row + 1):
        for col in range(1, max_col + 1):
            cell = sheet.cell(row=row, column=col)
            cell.border = border
            if col == 3:  # Vehicle column
                cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
            else:
                cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    output_path = project_root / "results" / OUTPUT_FILENAME
    gpt_results_path = project_root / "results" / "responses_gpt.json"
    groq_results_path = project_root / "results" / "responses_groq.json"

    gpt_index = build_index(load_results(gpt_results_path))
    groq_index = build_index(load_results(groq_results_path))

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
                gpt_response = gpt_index.get((prompt, vehicle, dtc), "[Aucun résultat trouvé]")
                groq_response = groq_index.get((prompt, vehicle, dtc), "[Aucun résultat trouvé]")

                ws.cell(row=current_row, column=1, value=dtc)
                ws.cell(row=current_row, column=2, value=prompt)
                ws.cell(row=current_row, column=3, value=vehicle)
                ws.cell(row=current_row, column=4, value=gpt_response)
                ws.cell(row=current_row, column=5, value=groq_response)
                current_row += 1

            prompt_end = current_row - 1
            ws.merge_cells(start_row=prompt_start, start_column=2, end_row=prompt_end, end_column=2)

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
