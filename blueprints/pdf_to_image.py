from pdf2image import convert_from_bytes
from flask import Blueprint, render_template

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