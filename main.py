from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any

from configuration import load_config
from service import build_pdf

REQUIRED_FIELDS = (
    "INVOICE_NUMBER",
    "DATE",
    "DUE_DATE",
    "ITEM_DESCRIPTION",
    "QTY",
    "UNIT_PRICE",
    "GST_PERCENT",
)


def parse_args() -> argparse.Namespace:
    base_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(
        description="Generate invoice PDFs from CSV or interactive input."
    )
    parser.add_argument(
        "--source",
        choices=("csv", "cli"),
        default="csv",
        help="Input source for invoices.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=base_dir / "configuration" / "config.json",
        help="Path to the configuration JSON file.",
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=base_dir / "input" / "invoice_data.csv",
        help="Path to the input CSV file.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=base_dir / "output",
        help="Directory where generated PDFs are written.",
    )
    return parser.parse_args()


def prompt_input(prompt: str, optional: bool = False) -> str:
    while True:
        value = input(prompt).strip()
        if value or optional:
            return value
        print("  Input cannot be blank. Please try again.")


def prompt_number(prompt: str, value_type: type[float] | type[int]) -> str:
    while True:
        value = prompt_input(prompt)
        try:
            parsed = value_type(value)
        except ValueError:
            print("  Please enter a valid number.")
            continue

        if parsed < 0:
            print("  Please enter a non-negative value.")
            continue

        return str(parsed)


def prompt_for_invoice_record() -> dict[str, str]:
    print("\nEnter invoice details:")
    return {
        "INVOICE_NUMBER": prompt_input("  Invoice number: "),
        "DATE": prompt_input("  Issue date (dd/mm/yyyy): "),
        "DUE_DATE": prompt_input("  Due date (dd/mm/yyyy): "),
        "ITEM_DESCRIPTION": prompt_input("  Item description: "),
        "QTY": prompt_number("  Quantity: ", int),
        "UNIT_PRICE": prompt_number("  Unit price: ", float),
        "GST_PERCENT": prompt_number("  GST percent: ", float),
    }


def read_invoice_records_from_csv(file_path: Path) -> list[dict[str, str]]:
    if not file_path.exists():
        raise FileNotFoundError(f"CSV input file not found: {file_path}")

    with file_path.open("r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        fieldnames = reader.fieldnames or []
        missing_columns = [field for field in REQUIRED_FIELDS if field not in fieldnames]
        if missing_columns:
            raise ValueError(
                f"CSV file is missing required columns: {', '.join(missing_columns)}"
            )

        records = [row for row in reader if any(row.values())]

    if not records:
        raise ValueError("No invoice records found in CSV input.")

    return records


def validate_record(record: dict[str, str]) -> None:
    missing_values = [field for field in REQUIRED_FIELDS if not record.get(field)]
    if missing_values:
        raise ValueError(
            "Invoice record is missing required values: " + ", ".join(missing_values)
        )


def process_invoice_records(
    config_data: dict[str, Any], records: list[dict[str, str]], output_dir: Path
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    for index, record in enumerate(records, start=1):
        validate_record(record)
        print(f" -> Mapping record #{index}: Invoice {record['INVOICE_NUMBER']}")
        build_pdf(config_data, record, output_dir)


def execute_autonomous_pipeline() -> None:
    args = parse_args()
    config_data = load_config(args.config)

    if args.source == "cli":
        records: list[dict[str, str]] = []
        while True:
            records.append(prompt_for_invoice_record())
            more = prompt_input("Add another invoice? [y/N]: ", optional=True).lower()
            if more not in ("y", "yes"):
                break
    else:
        records = read_invoice_records_from_csv(args.input)
        print(f"[SUCCESS] Parsed {len(records)} invoice record(s) from CSV.")

    process_invoice_records(config_data, records, args.output)
    print(
        f"\n[PIPELINE EXITED SUCCESSFULLY] Documents routed out directly to: {args.output.resolve()}"
    )


if __name__ == "__main__":
    execute_autonomous_pipeline()
