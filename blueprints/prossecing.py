from flask import Blueprint, current_app, render_template, send_from_directory
from pdf2image import convert_from_path
import os

image_app = Blueprint('image_app', __name__)

@image_app.route('/pdf_to_image/<filename>/<extension>')
def pdf_to_image(filename, extension):
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    
    # Ensure the file exists
    if not os.path.exists(file_path):
        return "File not found", 404

    try:
        # Convert PDF to images
        pages = convert_from_path(file_path, dpi=200)  # Adjust DPI if needed
        image_paths = []

        for page_num, page in enumerate(pages, start=1):
            image_filename = f"{os.path.splitext(filename)[0]}_page{page_num}.{extension}"
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], image_filename)
            page.save(image_path, extension.upper())
            image_paths.append(image_filename)

        return render_template('download.html', image_paths=image_paths)
    
    except Exception as e:
        return f"Error processing PDF: {str(e)}", 500












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


