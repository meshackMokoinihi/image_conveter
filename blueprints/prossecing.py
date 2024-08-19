from pdf2image import convert_from_bytes
from flask import Blueprint, render_template
import tabula
import pandas as pd
from PIL import Image
from fpdf import FPDF

import uuid

# Generate a random UUID

image_app = Blueprint('auth', __name__)


@image_app.route('pdf_to_image/<filename>')
def pdf_to_image(filename):
    images = convert_from_bytes(open(filename, 'rb').read(
    ), poppler_path=r"poppler-0.68.0_x86\poppler-0.68.0\bin")
    for i in range(len(images)):
        # Save pages as images in the pdf
        images[i].save(f'image_{i+1}.png', 'PNG')
    return render_template('')


@image_app.route()
def pdf_to_excel():
    pdf_path = './Thembela.pdf'

    # Extract tables from the PDF file
    tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)

    # Convert each table to an Excel sheet
    with pd.ExcelWriter('output.xlsx', engine='openpyxl') as writer:
        for i, table in enumerate(tables):
            table.to_excel(writer, sheet_name=f'Sheet{i+1}', index=False)



@image_app.route()
def image_to_pdf():
    # Specify the image file path
    image_path = 'your_image.jpg'

    # Load the image using Pillow
    image = Image.open(image_path)

    # Convert the image to RGB (if it's not already in RGB mode)
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")

    # Save the image as a PDF
    pdf_path = 'output.pdf'
    image.save(pdf_path)

    print("Image successfully converted to PDF")
