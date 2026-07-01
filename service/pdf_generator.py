import os
from fpdf import FPDF

class CorporateInvoiceEngine(FPDF):
    def __init__(self, config_data, invoice_record):
        super().__init__()
        self.cfg = config_data
        self.rec = invoice_record

    def header(self):
        self.set_fill_color(*self.cfg["theme"]["primary_color"])
        self.rect(0, 0, 210, 8, 'F')
        self.ln(10)
        self.set_font("Arial", "B", 18)
        self.set_text_color(*self.cfg["theme"]["secondary_color"])
        self.cell(120, 8, f"{self.cfg['metadata']['company_name']}", ln=False, align="L")
        self.set_font("Arial", "B", 16)
        self.set_text_color(*self.cfg["theme"]["text_muted"])
        self.cell(0, 8, f"Invoice {self.rec['INVOICE_NUMBER']}", ln=True, align="R")
        self.set_font("Arial", "", 9)
        self.cell(120, 5, f"Company ID: {self.cfg['metadata']['company_id']}", ln=False, align="L")
        self.cell(0, 5, "Tax Invoice", ln=True, align="R")
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
        self.cell(0, 5, "Pipeline Processed Architecture System Output.", ln=False, align="C")

def build_pdf(config_data, record, output_directory):
    qty = int(record["QTY"])
    unit_price = float(record["UNIT_PRICE"])
    gst_p = float(record["GST_PERCENT"])
    
    line_total = qty * unit_price
    gst_amount = line_total * (gst_p / 100)
    final_amount = line_total + gst_amount

    pdf = CorporateInvoiceEngine(config_data, record)
    pdf.add_page()
    
    pdf.set_font("Arial", "B", 10)
    pdf.set_text_color(*config_data["theme"]["text_dark"])
    pdf.cell(120, 5, "BILL TO", ln=False)
    
    pdf.set_font("Arial", "B", 9)
    pdf.cell(35, 5, "Issue date:", ln=False, align="R")
    pdf.set_font("Arial", "", 9)
    pdf.cell(0, 5, f"  {record['DATE']}", ln=True, align="L")
    
    pdf.set_font("Arial", "", 9)
    pdf.set_text_color(*config_data["theme"]["text_muted"])
    
    addr_parts = config_data["metadata"]["address"].split(",")
    pdf.cell(120, 5, addr_parts[0], ln=False)
    
    pdf.set_font("Arial", "B", 9)
    pdf.set_text_color(*config_data["theme"]["text_dark"])
    pdf.cell(35, 5, "Due date:", ln=False, align="R")
    pdf.set_font("Arial", "", 9)
    pdf.cell(0, 5, f"  {record['DUE_DATE']}", ln=True, align="L")
    
    for line in addr_parts[1:]:
        pdf.cell(120, 5, line.strip(), ln=True)
        
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
    pdf.cell(42, 10, f"  {record['INVOICE_NUMBER']}", ln=False, fill=True)
    pdf.cell(42, 10, f"  {record['DATE']}", ln=False, fill=True)
    pdf.cell(42, 10, f"  {record['DUE_DATE']}", ln=False, fill=True)
    
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
    pdf.cell(95, 12, f"{record['ITEM_DESCRIPTION']}", border="B", ln=False)
    pdf.cell(20, 12, f"{qty}", border="B", ln=False, align="R")
    pdf.cell(25, 12, f"{unit_price:,.2f}", border="B", ln=False, align="R")
    pdf.cell(20, 12, f"{gst_p}%", border="B", ln=False, align="R")
    pdf.cell(0, 12, f"{line_total:,.2f}", border="B", ln=True, align="R")
    
    pdf.ln(6)
    
    pdf.set_font("Arial", "", 9)
    pdf.cell(140, 6, "", ln=False)
    pdf.cell(25, 6, "Subtotal:", ln=False, align="R")
    pdf.cell(0, 6, f"${line_total:,.2f}", ln=True, align="R")
    
    pdf.cell(140, 6, "", ln=False)
    pdf.cell(25, 6, f"GST {gst_p}%:", ln=False, align="R")
    pdf.cell(0, 6, f"${gst_amount:,.2f}", ln=True, align="R")
    
    pdf.ln(2)
    pdf.set_font("Arial", "B", 11)
    pdf.set_text_color(*config_data["theme"]["secondary_color"])
    pdf.cell(140, 8, "", ln=False)
    pdf.cell(25, 8, "Total (AUD):", border="T", ln=False, align="R")
    pdf.cell(0, 8, f"${final_amount:,.2f}", border="T", ln=True, align="R")
    
    output_filename = os.path.join(output_directory, f"invoice_{record['INVOICE_NUMBER']}.pdf")
    pdf.output(output_filename)