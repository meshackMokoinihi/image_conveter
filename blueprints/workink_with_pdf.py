from flask import Flask, Blueprint, request, render_template_string, render_template, send_from_directory
import os
wPdf = Blueprint('workingPdf', __name__ )



from pypdf import PdfReader, PdfWriter
ENCRYPTED_DIR = "encrypted_files"
os.makedirs(ENCRYPTED_DIR, exist_ok=True)

@wPdf.route('/extract_images', methods=['POST', 'GET'])
def extract_images():
    reader = PdfReader("test_stamp.pdf")

    page = reader.pages[0]

    for count, image_file_object in enumerate(page.images):
        with open(str(count) + image_file_object.name, "wb") as fp:
            fp.write(image_file_object.data)
            
            
@wPdf.route('/extract_text', methods=['POST'])
def extract_text():
    uploaded_file = request.files['file']  # Get the uploaded file
    reader = PdfReader(uploaded_file)
    page = reader.pages[0]
    text = page.extract_text()

    # Pass the extracted text to a styled template
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/css/bootstrap.min.css" rel="stylesheet">
        <title>Extracted Text</title>
        <style>
            .text-box {
                width: 100%;
                height: 300px;
                background-color: #f9f9f9;
                border: 1px solid #ccc;
                padding: 10px;
                border-radius: 5px;
                overflow-y: scroll;
                white-space: pre-wrap;
                font-family: 'Courier New', Courier, monospace;
            }
        </style>
    </head>
    <body class="p-4">
        <h1 class="mb-3">Extracted Text</h1>
        <div class="text-box">{{ text }}</div>
        <a href="/" class="btn btn-primary mt-3">Go Back</a>
    </body>
    </html>
    ''', text=text)
    
@wPdf.route('/merge_pdf', methods=['POST', 'GET'])
def merge_pdf():
    merger = PdfWriter()

    for pdf in ["file1.pdf", "file2.pdf", "file3.pdf"]:
        merger.append(pdf)

    merger.write("merged-pdf.pdf")
    merger.close()
        
    
    
@wPdf.route('/encrypt_pdf', methods=['POST'])
def encrypt_pdf():
    uploaded_file = request.files['file']  # Get the uploaded file
    password = request.form.get('password')  # Get the password from the form

    if not password:
        return "Password is required for encryption.", 400

    reader = PdfReader(uploaded_file)
    writer = PdfWriter(clone_from=reader)

    # Encrypt the PDF with the provided password
    output_filename = "encrypted_" + uploaded_file.filename
    output_path = os.path.join(ENCRYPTED_DIR, output_filename)
    writer.encrypt(password, algorithm="AES-256")

    with open(output_path, "wb") as f:
        writer.write(f)

    # Render the download page
    return render_template('encrypted.html', filename=output_filename)
    
    
@wPdf.route('/dencrypt_pdf', methods=['POST', 'GET'])
def dencrypt_pdf():
    reader = PdfReader("encrypted-pdf.pdf")

    if reader.is_encrypted:
        reader.decrypt("my-secret-password")

    writer = PdfWriter(clone_from=reader)

    # Save the new PDF to a file
    with open("decrypted-pdf.pdf", "wb") as f:
        writer.write(f)
        
        
@wPdf.route('/download/<filename>')
def download_file(filename):
    # Ensure the file exists in the encrypted directory
    return send_from_directory(ENCRYPTED_DIR, filename, as_attachment=True)
