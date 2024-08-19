import tabula
import pandas as pd

# Specify the PDF file path
pdf_path = './Thembela.pdf'

# Extract tables from the PDF file
tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)

# Convert each table to an Excel sheet
with pd.ExcelWriter('output.xlsx', engine='openpyxl') as writer:
    for i, table in enumerate(tables):
        table.to_excel(writer, sheet_name=f'Sheet{i+1}', index=False)

print("PDF successfully converted to Excel")
