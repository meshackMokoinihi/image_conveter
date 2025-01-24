from flask import Flask, Blueprint, request, render_template_string, render_template, send_from_directory, send_file
import os
from pdf2image import convert_from_bytes
from flask import Flask, request, render_template_string
from PyMuPDF import fitz # PyMuPDF
import zipfile 
import io
from PyPDF2 import PdfWriter, PdfReader
# from fpdf import FPDF
import pdfplumber
from docx2pdf import convert as docx_to_pdf_convert
from pdf2docx import Converter as pdf_to_docx_convert
from urllib.parse import unquote
import pypandoc


wPdf = Blueprint('workingPdf', __name__ )


ENCRYPTED_DIR = "encrypted_files"
DECRYPTED_DIR = "dencrypted_files"
os.makedirs(ENCRYPTED_DIR, exist_ok=True)
os.makedirs(DECRYPTED_DIR, exist_ok=True)

@wPdf.route('/extract_images', methods=['POST', 'GET'])
def extract_images():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        pdf_document = fitz.open(stream=uploaded_file.read(), filetype="pdf")

        output_dir = "static/extracted_images"
        os.makedirs(output_dir, exist_ok=True)

        image_paths = []

        for page_number in range(len(pdf_document)):
            page = pdf_document.load_page(page_number)
            images = page.get_images(full=True)

            for img_index, img in enumerate(images):
                xref = img[0]
                base_image = pdf_document.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                image_path = os.path.join(output_dir, f"page_{page_number + 1}_image_{img_index + 1}.{image_ext}")

                with open(image_path, "wb") as img_file:
                    img_file.write(image_bytes)

                image_paths.append(f"extracted_images/{os.path.basename(image_path)}")

        return render_template_string('''
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/css/bootstrap.min.css" rel="stylesheet">
                <title>Extracted Images</title>
                <style>
                    .image-container {
                        display: flex;
                        flex-wrap: wrap;
                        gap: 10px;
                    }
                    .image-container img {
                        max-width: 100%;
                        height: auto;
                        border: 1px solid #ccc;
                        border-radius: 5px;
                        cursor: pointer;
                    }
                </style>
            </head>
            <body class="p-4">
                <h1 class="mb-3">Extracted Images</h1>
                <div class="image-container">
                    {% for image_path in image_paths %}
                        <div class="col-md-3 mb-3">
                            <a href="{{ url_for('static', filename=image_path) }}" download>
                                <img src="{{ url_for('static', filename=image_path) }}" alt="Extracted Image">
                            </a>
                        </div>
                    {% endfor %}
                </div>
                <a href="/download_all" class="btn btn-primary mt-3">Download All</a>
                <a href="/" class="btn btn-secondary mt-3">Go Back</a>
            </body>
            </html>
        ''', image_paths=image_paths)

    return '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/css/bootstrap.min.css" rel="stylesheet">
            <title>Upload PDF</title>
        </head>
        <body class="p-4">
            <h1 class="mb-3">Upload PDF</h1>
            <form method="post" enctype="multipart/form-data">
                <div class="mb-3">
                    <label for="file" class="form-label">Choose PDF file</label>
                    <input class="form-control" type="file" id="file" name="file" accept="application/pdf" required>
                </div>
                <button type="submit" class="btn btn-primary">Extract Images</button>
            </form>
        </body>
        </html>
    '''

@wPdf.route('/download_all')
def download_all():
    output_dir = "static/extracted_images"
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        for foldername, subfolders, filenames in os.walk(output_dir):
            for filename in filenames:
                file_path = os.path.join(foldername, filename)
                zf.write(file_path, os.path.relpath(file_path, output_dir))
    memory_file.seek(0)
    return send_file(memory_file, attachment_filename='extracted_images.zip', as_attachment=True)






@wPdf.route('/encrypt_pdf', methods=['POST'])
def encrypt_pdf():
    uploaded_file = request.files['file']
    password = request.form.get('encryptionPassword')

    if not password:
        return "Password is required for encryption.", 400

    reader = PdfReader(uploaded_file)
    writer = PdfWriter(clone_from=reader)
    writer.encrypt(password, algorithm="AES-256")

    output_filename = uploaded_file.filename
    output_path = os.path.join(ENCRYPTED_DIR, output_filename)
    with open(output_path, "wb") as f:
        writer.write(f)

    return render_template('encrypted.html', filename=output_filename)

@wPdf.route('/decrypt_pdf', methods=['POST'])
def decrypt_pdf():
    uploaded_file = request.files['file']
    password = request.form.get('password')

    if not password:
        return "Password is required for decryption.", 400

    reader = PdfReader(uploaded_file)

    if reader.is_encrypted:
        try:
            reader.decrypt(password)
        except Exception as e:
            return f"Decryption failed: {str(e)}", 400

    writer = PdfWriter(clone_from=reader)

    output_filename = uploaded_file.filename
    output_path = os.path.join(DECRYPTED_DIR, output_filename)
    with open(output_path, "wb") as f:
        writer.write(f)

    return render_template('decrypted.html', filename=output_filename)

@wPdf.route('/download/<filename>')
def download_file(filename):
    print(filename)
    return send_from_directory(ENCRYPTED_DIR, filename, as_attachment=True)

@wPdf.route('/download_decrypted/<filename>')
def download_decrypted(filename):
    
    return send_from_directory(DECRYPTED_DIR, filename, as_attachment=True)

















@wPdf.route('/merge_pdf', methods=['POST', 'GET'])
def merge_pdf():
    if request.method == 'POST':
        uploaded_files = request.files.getlist('files')
        output_dir = "static/merged_files"
        os.makedirs(output_dir, exist_ok=True)

        merger = PdfWriter()
        temp_pdf_paths = []

        for uploaded_file in uploaded_files:
            file_ext = os.path.splitext(uploaded_file.filename)[1].lower()

            if file_ext == '.pdf':
                pdf_path = os.path.join(output_dir, uploaded_file.filename)
                uploaded_file.save(pdf_path)
                temp_pdf_paths.append(pdf_path)
                merger.append(pdf_path)

            elif file_ext in ['.png', '.jpg', '.jpeg']:
                image_pdf = FPDF()
                image_pdf.add_page()
                # Converting image data to temporary path
                image_path = os.path.join(output_dir, uploaded_file.filename)
                uploaded_file.save(image_path)
                image_pdf.image(image_path, 10, 10, 200, 280)
                image_pdf_path = os.path.join(output_dir, f"{os.path.splitext(uploaded_file.filename)[0]}.pdf")
                image_pdf.output(image_pdf_path)

                temp_pdf_paths.append(image_pdf_path)
                merger.append(image_pdf_path)

        merged_pdf_path = os.path.join(output_dir, "merged.pdf")
        with open(merged_pdf_path, 'wb') as f:
            merger.write(f)

        for temp_pdf_path in temp_pdf_paths:
            os.remove(temp_pdf_path)

        return send_file(merged_pdf_path, as_attachment=True)

    return '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/css/bootstrap.min.css" rel="stylesheet">
            <title>Merge Files</title>
        </head>
        <body class="p-4">
            <h1 class="mb-3">Merge Files</h1>
            <form method="post" enctype="multipart/form-data">
                <div class="mb-3">
                    <label for="files" class="form-label">Choose PDF and Image files</label>
                    <input class="form-control" type="file" id="files" name="files" multiple required>
                </div>
                <button type="submit" class="btn btn-primary">Merge Files</button>
            </form>
        </body>
        </html>
    '''

@wPdf.route('/extract_text', methods=['POST', 'GET'])
def extract_text():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        page_number = int(request.form.get('page_number', 0))
        pdf_document = fitz.open(stream=uploaded_file.read(), filetype="pdf")

        if page_number > 0 and page_number <= len(pdf_document):
            page = pdf_document.load_page(page_number - 1)
            text_content = page.get_text()
        else:
            text_content = "Invalid page number."

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
                <button class="btn btn-secondary mt-3" onclick="copyText()">Copy Text</button>
                <a href="/" class="btn btn-primary mt-3">Go Back</a>
                <script>
                    function copyText() {
                        const textBox = document.querySelector('.text-box');
                        navigator.clipboard.writeText(textBox.innerText).then(() => {
                            alert('Text copied to clipboard');
                        }).catch(err => {
                            console.error('Error copying text: ', err);
                        });
                    }
                </script>
            </body>
            </html>
        ''', text=text_content)

    return '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/css/bootstrap.min.css" rel="stylesheet">
            <title>Extract Text</title>
        </head>
        <body class="p-4">
            <h1 class="mb-3">Extract Text from PDF</h1>
            <form method="post" enctype="multipart/form-data">
                <div class="mb-3">
                    <label for="file" class="form-label">Choose PDF file</label>
                    <input class="form-control" type="file" id="file" name="file" accept="application/pdf" required>
                </div>
                <div class="mb-3">
                    <label for="page_number" class="form-label">Enter Page Number (0 for all pages)</label>
                    <input class="form-control" type="number" id="page_number" name="page_number" min="0" required>
                </div>
                <button type="submit" class="btn btn-primary">Extract Text</button>
            </form>
        </body>
        </html>
    '''



























@wPdf.route('/edit_pdf', methods=['POST'])
def edit_pdf():
    uploaded_file = request.files['file']
    upload_folder = "static/uploads"
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, uploaded_file.filename)
    uploaded_file.save(file_path)

    return render_template_string('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/css/bootstrap.min.css" rel="stylesheet">
            <title>Edit PDF</title>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.7.570/pdf.min.js"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/fabric.js/4.6.0/fabric.min.js"></script>
            <style>
                .pdf-page {
                    margin-bottom: 20px;
                    border: 1px solid #ccc;
                }
                .text-options {
                    margin-bottom: 20px;
                }
            </style>
        </head>
        <body class="p-4">
            <h1 class="mb-3">Edit PDF</h1>
            <div class="text-options">
                <input type="text" id="custom-text" placeholder="Enter text here">
                <select id="font-color">
                    <option value="black">Black</option>
                    <option value="red">Red</option>
                    <option value="blue">Blue</option>
                    <option value="green">Green</option>
                </select>
                <select id="font-style">
                    <option value="Arial">Arial</option>
                    <option value="Courier">Courier</option>
                    <option value="Times New Roman">Times New Roman</option>
                </select>
                <button class="btn btn-secondary" id="add-text">Add Text</button>
            </div>
            <div id="pdf-container"></div>
            <button class="btn btn-primary mt-3" onclick="savePDF()">Save PDF</button>
            <script>
                const url = "{{ url_for('static', filename='uploads/' + filename) }}";
                const pdfContainer = document.getElementById('pdf-container');
                const addTextBtn = document.getElementById('add-text');
                let pdfDoc = null;
                let pages = [];
                let activeCanvas = null;

                pdfjsLib.getDocument(url).promise.then(doc => {
                    pdfDoc = doc;
                    for (let i = 1; i <= doc.numPages; i++) {
                        doc.getPage(i).then(page => {
                            const viewport = page.getViewport({ scale: 1.5 });
                            const canvas = document.createElement('canvas');
                            canvas.classList.add('pdf-page');
                            canvas.width = viewport.width;
                            canvas.height = viewport.height;
                            const ctx = canvas.getContext('2d');
                            page.render({ canvasContext: ctx, viewport: viewport }).promise.then(() => {
                                const fabricCanvas = new fabric.Canvas(canvas);
                                fabricCanvas.setWidth(canvas.width);
                                fabricCanvas.setHeight(canvas.height);
                                fabricCanvas.setBackgroundImage(canvas.toDataURL('image/png'), fabricCanvas.renderAll.bind(fabricCanvas));
                                pages.push({ canvas: fabricCanvas, pageNumber: i });
                                fabricCanvas.on('mouse:down', function (options) {
                                    if (isTextMode) {
                                        const text = new fabric.IText('Enter text here', {
                                            left: options.pointer.x,
                                            top: options.pointer.y,
                                            fontSize: 20,
                                            fill: 'black'
                                        });
                                        fabricCanvas.add(text);
                                        fabricCanvas.setActiveObject(text);
                                        text.enterEditing();
                                        text.selectAll();
                                    }
                                    activeCanvas = fabricCanvas;
                                });
                            });
                            pdfContainer.appendChild(canvas);
                        });
                    }
                }).catch(error => {
                    console.error('Error rendering PDF:', error);
                });

                let isTextMode = false;
                addTextBtn.addEventListener('click', () => {
                    isTextMode = !isTextMode;
                    addTextBtn.textContent = isTextMode ? 'Exit Text Mode' : 'Add Text';
                });

                async function savePDF() {
                    const { PDFDocument } = PDFLib;
                    const existingPdfBytes = await fetch(url).then(res => res.arrayBuffer());
                    const pdfDoc = await PDFDocument.load(existingPdfBytes);

                    for (const page of pages) {
                        const firstPage = pdfDoc.getPage(page.pageNumber - 1);
                        const imageData = page.canvas.toDataURL('image/png');

                        const pngImageBytes = await fetch(imageData).then(res => res.arrayBuffer());
                        const pngImage = await pdfDoc.embedPng(pngImageBytes);
                        firstPage.drawImage(pngImage, {
                            x: 0,
                            y: 0,
                            width: firstPage.getWidth(),
                            height: firstPage.getHeight()
                        });
                    }

                    const pdfBytes = await pdfDoc.save();
                    const blob = new Blob([pdfBytes], { type: 'application/pdf' });
                    const link = document.createElement('a');
                    link.href = URL.createObjectURL(blob);
                    link.download = 'edited.pdf';
                    link.click();
                }
            </script>
        </body>
        </html>
    ''', filename=uploaded_file.filename)














DOCX_DIR = "docx_files"
PDF_DIR = "pdf_files"


os.makedirs(DOCX_DIR, exist_ok=True)
os.makedirs(PDF_DIR, exist_ok=True)



@wPdf.route('/convert_docx_to_pdf', methods=['POST'])
def convert_docx_to_pdf():
    uploaded_file = request.files['file']
    docx_path = os.path.join(DOCX_DIR, uploaded_file.filename)
    uploaded_file.save(docx_path)

    # Convert DOCX to PDF using pypandoc
    output_filename = f"{os.path.splitext(uploaded_file.filename)[0]}.pdf"
    pdf_output_path = os.path.join(PDF_DIR, output_filename)
    pypandoc.convert_file(docx_path, 'pdf', outputfile=pdf_output_path)

    return render_template('docxtopdf.html', filename=os.path.basename(pdf_output_path) )



@wPdf.route('/convert_pdf_to_docx', methods=['POST', 'GET'])
def convert_pdf_to_docx():
    uploaded_file = request.files['file']
    output_filename = f"{os.path.splitext(uploaded_file.filename)[0]}.docx"
    output_path = os.path.join(DOCX_DIR, output_filename)

    pdf_path = os.path.join(PDF_DIR, uploaded_file.filename)
    uploaded_file.save(pdf_path)

    # Convert PDF to DOCX
    cv = pdf_to_docx_convert(pdf_path)
    cv.convert(output_path)
    cv.close()

    return render_template('pdftodocx.html', filename=output_filename)



@wPdf.route('/download_pdf_to_docx/<filename>')
def download_pdf_to_docx(filename):
    print(filename)
    if '%' in filename:
        filename.replace('%', ' ')
    return send_from_directory(DOCX_DIR, filename, as_attachment=True)


@wPdf.route('/download_docx_to_pdf/<filename>')
def download_docx_to_pdf(filename):
    print(filename)
    if '%' in filename:
        filename.replace('%', ' ')
    return send_from_directory(PDF_DIR, filename, as_attachment=True)