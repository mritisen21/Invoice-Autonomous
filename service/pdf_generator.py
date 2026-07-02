import os
import re
from typing import Any

from fpdf import FPDF


def sanitize_filename_component(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return "invoice"

    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", text)
    cleaned = cleaned.strip("._-")
    return cleaned or "invoice"


def parse_numeric(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default
    text = str(value).strip()
    if not text:
        return default

    text = text.replace("₹", "").replace("$", "").replace("AUD", "").strip()
    if text.count(",") == 1 and "." not in text and len(text.split(",")[1]) == 2:
        text = text.replace(",", ".")
    else:
        text = text.replace(",", "")

    cleaned = re.sub(r"[^0-9.\-]", "", text)
    try:
        return float(cleaned)
    except ValueError:
        return default


class CorporateInvoiceEngine(FPDF):
    def __init__(self, config_data, invoice_record):
        super().__init__()
        self.cfg = config_data
        self.rec = invoice_record

    def header(self):
        company_name = self.rec.get("COMPANY_NAME") or self.cfg["metadata"]["company_name"]
        company_id = self.rec.get("COMPANY_ID") or self.cfg["metadata"]["company_id"]

        self.set_fill_color(*self.cfg["theme"]["primary_color"])
        self.rect(0, 0, 210, 8, "F")
        self.ln(10)
        self.set_font("Arial", "B", 18)
        self.set_text_color(*self.cfg["theme"]["secondary_color"])
        self.cell(120, 8, company_name, ln=False, align="L")
        self.set_font("Arial", "", 9)
        self.set_text_color(*self.cfg["theme"]["text_muted"])
        self.cell(0, 8, f" {self.rec['INVOICE_NUMBER']}", ln=True, align="R")
        self.set_font("Arial", "", 9)
        self.cell(0, 5, f"Company ID: {company_id}", ln=True, align="L")
        self.ln(10)

    def footer(self):
        self.set_y(-45)
        self.set_font("Arial", "B", 10)
        self.set_text_color(*self.cfg["theme"]["text_dark"])
        self.cell(0, 5, "Issued by, signature:", ln=True, align="R")
        self.set_font("Arial", "I", 14)
        self.set_text_color(41, 128, 185)
        self.cell(0, 10, "Authorized Signatory  ", ln=True, align="R")
        self.set_y(-15)
        self.set_font("Arial", "", 8)
        self.set_text_color(*self.cfg["theme"]["text_muted"])
        


def build_pdf(config_data, record, output_directory):
    invoice_number = record["INVOICE_NUMBER"]
    invoice_date = record.get("DATE", "")
    due_date = record.get("DUE_DATE", "")
    company_name = record.get("COMPANY_NAME") or config_data["metadata"]["company_name"]
    company_id = record.get("COMPANY_ID") or config_data["metadata"]["company_id"]
    address = record.get("ADDRESS") or config_data["metadata"]["address"]
    items = record.get("ITEMS") or [
        {
            "ITEM_DESCRIPTION": record.get("ITEM_DESCRIPTION", ""),
            "QTY": record.get("QTY", ""),
            "UNIT_PRICE": record.get("UNIT_PRICE", ""),
            "GST_PERCENT": record.get("GST_PERCENT", ""),
        }
    ]

    subtotal = 0.0
    gst_total = 0.0
    rendered_items: list[dict[str, Any]] = []

    for item in items:
        qty = int(parse_numeric(item.get("QTY", "0"), 0))
        unit_price = parse_numeric(item.get("UNIT_PRICE", "0"), 0.0)
        gst_p = parse_numeric(item.get("GST_PERCENT", "0"), 0.0)

        line_total = parse_numeric(item.get("LINE_TOTAL", None), qty * unit_price)
        if line_total == 0:
            line_total = qty * unit_price

        gst_amount = line_total * (gst_p / 100)
        amount = parse_numeric(item.get("AMOUNT", None), line_total + gst_amount)

        subtotal += line_total
        gst_total += gst_amount
        rendered_items.append(
            {
                "description": item["ITEM_DESCRIPTION"],
                "qty": qty,
                "unit_price": unit_price,
                "gst_p": gst_p,
                "line_total": line_total,
                "gst_amount": gst_amount,
                "amount": amount,
            }
        )

    final_amount = subtotal + gst_total

    pdf = CorporateInvoiceEngine(config_data, record)
    pdf.add_page()

    pdf.set_font("Arial", "B", 10)
    pdf.set_text_color(*config_data["theme"]["text_dark"])
    pdf.cell(120, 5, "BILL TO", ln=False)

    pdf.set_font("Arial", "B", 9)
    pdf.cell(35, 5, "Issue date:", ln=False, align="R")
    pdf.set_font("Arial", "", 9)
    pdf.cell(0, 5, f"  {invoice_date}", ln=True, align="L")

    pdf.set_font("Arial", "B", 9)
    pdf.set_text_color(*config_data["theme"]["text_dark"])
    pdf.cell(120, 5, company_name, ln=False)
    pdf.cell(35, 5, "Due date:", ln=False, align="R")
    pdf.set_font("Arial", "", 9)
    pdf.cell(0, 5, f"  {due_date}", ln=True, align="L")

    pdf.set_font("Arial", "", 9)
    pdf.set_text_color(*config_data["theme"]["text_muted"])
    address_parts = [part.strip() for part in address.split(",") if part.strip()]
    if address_parts:
        pdf.cell(120, 5, address_parts[0], ln=False)
        pdf.set_font("Arial", "B", 9)
        pdf.set_text_color(*config_data["theme"]["text_dark"])
        pdf.cell(35, 5, "", ln=False)
        pdf.cell(0, 5, "", ln=True)
        pdf.set_font("Arial", "", 9)
        pdf.set_text_color(*config_data["theme"]["text_muted"])
        for line in address_parts[1:]:
            pdf.cell(120, 5, line, ln=True)
    else:
        pdf.cell(0, 5, "", ln=True)

    pdf.ln(12)

    pdf.set_fill_color(*config_data["theme"]["primary_color"])
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 9)
    pdf.cell(42, 6, "  Invoice No.", ln=False, fill=True)
    pdf.cell(42, 6, "  Issue date", ln=False, fill=True)
    pdf.cell(42, 6, "  Due date", ln=False, fill=True)

    pdf.set_fill_color(*config_data["theme"]["secondary_color"])
    pdf.cell(0, 6, f"  Total due ({config_data['metadata']['currency']})", ln=True, fill=True)

    pdf.set_fill_color(*config_data["theme"]["background_highlight"])
    pdf.set_text_color(*config_data["theme"]["text_dark"])
    pdf.set_font("Arial", "", 10)
    pdf.cell(42, 10, f"  {invoice_number}", ln=False, fill=True)
    pdf.cell(42, 10, f"  {invoice_date}", ln=False, fill=True)
    pdf.cell(42, 10, f"  {due_date}", ln=False, fill=True)

    pdf.set_fill_color(*config_data["theme"]["secondary_color"])
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"  ${final_amount:,.2f}", ln=True, fill=True)

    pdf.ln(15)

    pdf.set_text_color(*config_data["theme"]["text_dark"])
    pdf.set_font("Arial", "B", 9)
    pdf.cell(95, 8, "Description", border="B", ln=False)
    pdf.cell(20, 8, "Quantity", border="B", ln=False, align="R")
    pdf.cell(25, 8, "Unit price ($)", border="B", ln=False, align="R")
    pdf.cell(20, 8, "GST %", border="B", ln=False, align="R")
    pdf.cell(0, 8, "Amount ($)", border="B", ln=True, align="R")

    pdf.set_font("Arial", "", 9)
    pdf.set_text_color(90, 90, 90)
    for item in rendered_items:
        pdf.cell(95, 12, f"{item['description']}", border="B", ln=False)
        pdf.cell(20, 12, f"{item['qty']}", border="B", ln=False, align="R")
        pdf.cell(25, 12, f"{item['unit_price']:,.2f}", border="B", ln=False, align="R")
        pdf.cell(20, 12, f"{item['gst_p']}%", border="B", ln=False, align="R")
        pdf.cell(0, 12, f"{item['amount']:,.2f}", border="B", ln=True, align="R")

    pdf.ln(6)

    pdf.set_font("Arial", "", 9)
    pdf.cell(140, 6, "", ln=False)
    pdf.cell(25, 6, "Subtotal:", ln=False, align="R")
    pdf.cell(0, 6, f"${subtotal:,.2f}", ln=True, align="R")

    pdf.cell(140, 6, "", ln=False)
    pdf.cell(25, 6, f"GST {gst_total:.2f}:", ln=False, align="R")
    pdf.cell(0, 6, f"${gst_total:,.2f}", ln=True, align="R")

    pdf.ln(2)
    pdf.set_font("Arial", "B", 11)
    pdf.set_text_color(*config_data["theme"]["secondary_color"])
    pdf.cell(140, 8, "", ln=False)
    pdf.cell(25, 8, "Total (AUD):", border="T", ln=False, align="R")
    pdf.cell(0, 8, f"${final_amount:,.2f}", border="T", ln=True, align="R")

    safe_invoice_number = sanitize_filename_component(invoice_number)
    output_filename = os.path.join(output_directory, f"invoice_{safe_invoice_number}.pdf")
    pdf.output(output_filename)