from flask import Blueprint, render_template, current_app
import os
import fitz  # PyMuPDF
# from pdf2docx import Document


image_app = Blueprint('image_app', __name__)

@image_app.route('/pdf_to_image/<filename>/<extension>')
def pdf_to_image(filename, extension):
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    doc = fitz.open(file_path)

    image_paths = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap()
        image_filename = f'{filename}{page_num + 1}.{extension}'
        image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], image_filename)
        pix.save(image_path)
        image_paths.append(image_filename)

    return render_template('download.html', image_paths=image_paths)















# @image_app.route('/pdf_to_docx/<filename>')
# def pdf_to_docx(filename):
#     file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
#     docx_filename = filename.rsplit('.', 1)[0] + '.docx'
#     docx_path = os.path.join(current_app.config['UPLOAD_FOLDER'], docx_filename)

#     # Extract text from PDF and write to DOCX
#     try:
#         pdf_doc = fitz.open(file_path)
#         docx_doc = Document()

#         for page_num in range(len(pdf_doc)):
#             page = pdf_doc.load_page(page_num)
#             text = page.get_text()
#             docx_doc.add_paragraph(text)
        
#         docx_doc.save(docx_path)
#     except Exception as e:
#         return str(e)

#     return render_template('download.html', image_paths=docx_filename)




from flask import Flask, request, send_file
from PIL import Image
import os



@image_app.route('/image_to_pdf/<filename>', methods=['GET'])
def image_to_pdf(filename):
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(file_path):
        return "File not found", 404

    # Open the image and convert it to PDF
    image = Image.open(file_path)
    pdf_filename = f"{os.path.splitext(filename)[0]}.pdf"
    pdf_path = os.path.join(current_app.config['UPLOAD_FOLDER'], pdf_filename)
    image.save(pdf_path, "PDF", resolution=100.0)

    return send_file(pdf_path, as_attachment=True)


