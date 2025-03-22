import pandas as pd

EXCEL_FILE = "printer_supplies.xlsx"

# Load spreadsheet into DataFrame
def load_data():
    return pd.read_excel(EXCEL_FILE)

# Save DataFrame back to spreadsheet
def save_data(df):
    df.to_excel(EXCEL_FILE, index=False)

# Update supply quantity for a cabinet (row-wise)
def update_printer_supplies(cabinet, supply, change):
    df = load_data()
    df.loc[df["Building"] == cabinet, supply] += change
    save_data(df)

# Get quantity available of a supply at a given cabinet
def get_quantity_available(cabinet, supply):
    df = load_data()
    row = df[df["Building"] == cabinet]
    if not row.empty:
        return int(row.iloc[0][supply])
    return None