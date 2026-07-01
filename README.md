# Invoice-Autonomous

## How to run

1. Open PowerShell in the project folder:
   - `cd "c:\Users\Mirithika Saraswathy\Invoice-Autonomous"`
2. Create a virtual environment:
   - `python -m venv venv`
3. Activate it:
   - `venv\Scripts\Activate.ps1`
4. Install dependencies:
   - `pip install -r requirements.txt`
5. Run the app:
   - `run.bat`
   - or `.
un.ps1`

## How users can enter invoice details

### Option 1: Use the CSV file

Edit `input/invoice_data.csv` with one or more rows using these columns:

- `INVOICE_NUMBER`
- `DATE`
- `DUE_DATE`
- `ITEM_DESCRIPTION`
- `QTY`
- `UNIT_PRICE`
- `GST_PERCENT`

Then run `python main.py` and choose `csv`.

### Option 2: Enter details interactively

Run `python main.py` and choose `cli` when prompted.
The app will ask for invoice number, dates, item description, quantity, unit price, and GST percent.

## Output

Generated PDF invoices are saved to the `output/` folder.
