import tempfile
import unittest
from pathlib import Path

from openpyxl import Workbook

from main import group_invoice_rows, read_invoice_records_from_input
from service.pdf_generator import build_pdf


class InvoicePipelineTests(unittest.TestCase):
    def test_groups_rows_with_the_same_invoice_number(self):
        rows = [
            {
                "INVOICE_NUMBER": "INV-100",
                "DATE": "01/01/2026",
                "DUE_DATE": "15/01/2026",
                "ITEM_DESCRIPTION": "Setup",
                "QTY": "1",
                "UNIT_PRICE": "100",
                "GST_PERCENT": "10",
            },
            {
                "INVOICE_NUMBER": "INV-100",
                "DATE": "01/01/2026",
                "DUE_DATE": "15/01/2026",
                "ITEM_DESCRIPTION": "Support",
                "QTY": "2",
                "UNIT_PRICE": "50",
                "GST_PERCENT": "10",
            },
        ]

        grouped = group_invoice_rows(rows)

        self.assertEqual(len(grouped), 1)
        self.assertEqual(grouped[0]["INVOICE_NUMBER"], "INV-100")
        self.assertEqual(len(grouped[0]["ITEMS"]), 2)

    def test_reads_excel_file_and_groups_rows(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "invoices.xlsx"
            workbook = Workbook()
            sheet = workbook.active
            sheet.append([
                "INVOICE_NUMBER",
                "DATE",
                "DUE_DATE",
                "ITEM_DESCRIPTION",
                "QTY",
                "UNIT_PRICE",
                "GST_PERCENT",
            ])
            sheet.append(["INV-200", "02/01/2026", "16/01/2026", "Consulting", "1", "200", "10"])
            sheet.append(["INV-200", "02/01/2026", "16/01/2026", "Hosting", "1", "100", "10"])
            workbook.save(path)

            grouped = read_invoice_records_from_input(path)

            self.assertEqual(len(grouped), 1)
            self.assertEqual(grouped[0]["INVOICE_NUMBER"], "INV-200")
            self.assertEqual(len(grouped[0]["ITEMS"]), 2)

    def test_build_pdf_sanitizes_invoice_number_for_output_path(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_dir = Path(tmp_dir)
            config_data = {
                "metadata": {
                    "company_name": "Example Corp",
                    "company_id": "C-100",
                    "address": "1 Test Street, Melbourne",
                    "currency": "AUD",
                },
                "theme": {
                    "primary_color": (41, 128, 185),
                    "secondary_color": (44, 62, 80),
                    "text_muted": (127, 140, 141),
                    "text_dark": (44, 62, 80),
                    "background_highlight": (236, 240, 241),
                },
            }
            record = {
                "INVOICE_NUMBER": '"INV/2026-001"',
                "DATE": "01/01/2026",
                "DUE_DATE": "15/01/2026",
                "COMPANY_NAME": "Example Corp",
                "COMPANY_ID": "C-100",
                "ADDRESS": "1 Test Street, Melbourne",
                "ITEMS": [
                    {
                        "ITEM_DESCRIPTION": "Consulting",
                        "QTY": "1",
                        "UNIT_PRICE": "100",
                        "GST_PERCENT": "10",
                    }
                ],
            }

            build_pdf(config_data, record, output_dir)

            created_files = list(output_dir.glob("*.pdf"))
            self.assertEqual(len(created_files), 1)
            self.assertEqual(created_files[0].name, "invoice_INV-2026-001.pdf")


if __name__ == "__main__":
    unittest.main()
