import csv
import json
import glob
from service.pdf_parser import extract_text_from_pdf
from service.llm_extractor import extract_fields_with_llm


def run_extraction(input_folder="output", report_path="report.csv"):
    pdf_files = glob.glob(f"{input_folder}/*.pdf")
    print(f"Found {len(pdf_files)} PDF files")

    all_rows = []
    for path in pdf_files:
        print(f"Processing {path}...")
        try:
            text = extract_text_from_pdf(path)
            data = extract_fields_with_llm(text)
            all_rows.append(data)
        except Exception as e:
            print(f"  FAILED: {e}")

    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["invoice_number", "invoice_date", "due_date", "total_amount", "items"])
        for data in all_rows:
            writer.writerow([
                data.get("invoice_number"),
                data.get("invoice_date"),
                data.get("due_date"),
                data.get("total_amount"),
                json.dumps(data.get("items"))
            ])

    print(f"Done! Wrote {len(all_rows)} rows to {report_path}")


if __name__ == "__main__":
    run_extraction()