from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, current_app, jsonify, send_file
import os 
from blueprints import prossecing
from textblob import TextBlob
import nltk
from nltk import sent_tokenize
import language_tool_python
import pdfkit
import asyncio
from pyppeteer import launch
from blueprints import workink_with_pdf as wpdf
from PIL import Image


app = Flask(__name__, template_folder='templates')
app.secret_key='secret_key'
filename = ''
format = ''


UPLOAD_FOLDER = 'uploads'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'docx'}

def allowed_files(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS





@app.route('/', methods=['GET', 'POST'])
def upload_file():
    global filename, format
    if request.method == 'POST':
        # Get the format from the form
        format = request.form.get('format')
        
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_files(file.filename):
            filename = file.filename
            file_path = os.path.join('uploads', filename)
            file.save(file_path)

            if format == 'pdf':
                # Handle conversion from image to PDF
                pdf_path = os.path.join('uploads', f"{os.path.splitext(filename)[0]}.pdf")
                convert_image_to_pdf(file_path, pdf_path)
                flash('File successfully converted to PDF')
                return redirect(url_for('download_file', filename=f"{os.path.splitext(filename)[0]}.pdf"))
            else:
                flash('File successfully uploaded')
                return redirect(url_for('image_app.pdf_to_image', filename=filename, extension=format))
        
    return render_template('index.html')

def convert_image_to_pdf(image_path, pdf_path):
    image = Image.open(image_path)
    image = image.convert('RGB')  # Ensure the image is in RGB mode
    image.save(pdf_path)





@app.route('/download')
def download_page():
    return render_template('download.html', filename=filename)



@app.route('/upload/<filename>/')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, download_name=f'{filename}', as_attachment=True)

@app.route('/grammar_correction', methods=['POST'])
def grammar_correction():
    text = request.form.get('text')
    if text:
        blob = TextBlob(text)
        corrected_text = str(blob.correct())
        return jsonify({'corrected_text': corrected_text})
    return jsonify({'error': 'No text provided'})

# @app.route('/essay_assistant', methods=['POST'])
# def essay_assistant():
#     text = request.form.get('text')
#     if not text:
#         return jsonify({'error': 'No text provided'})

#     # Basic analysis with TextBlob
#     blob = TextBlob(text)
    
#     # Sentence analysis
#     sentences = sent_tokenize(text)
#     structure_suggestions = {
#         'introduction': 'Make sure to start with a clear introduction that outlines your main argument.',
#         'body': 'Ensure each paragraph has a topic sentence and relevant supporting details.',
#         'conclusion': 'End with a summary that reinforces your main points.'
#     }

#     # Vocabulary enhancement
#     vocab_suggestions = []
#     for word in blob.words:
#         if len(word) > 6:  # Example criterion for "complex" words
#             vocab_suggestions.append(f"Consider simplifying the word '{word}' for better readability.")
    
#     response = {
#         'structure_suggestions': structure_suggestions,
#         'cohesiveness_score': blob.sentiment.polarity,  # Basic indicator of positivity/negativity
#         'vocab_suggestions': vocab_suggestions
#     }
#     print(response)

#     return jsonify(response)


@app.route('/essay_assistant', methods=['POST', 'GET'])
def essay_assistant():
      # Get the text from the request
    text = request.form.get('text')
    if not text:
        return jsonify({'error': 'No text provided'})
    
    # Initialize LanguageTool
    tool = language_tool_python.LanguageTool('en-US')

    # Check for spelling errors using TextBlob
    blob = TextBlob(text)
    corrected_text_blob = blob.correct()

    # Grammar and punctuation corrections using LanguageTool
    matches = tool.check(text)
    corrected_text_tool = tool.correct(text)

    # Gather suggestions for grammar and punctuation
    grammar_suggestions = [
        {
            'message': match.message,
            'incorrect_text': text[match.offset:match.offset + match.errorLength],
            'suggestions': match.replacements
        }
        for match in matches
    ]

    # Response with corrections
    response = {
        'original_text': text,
        'corrected_text': str(corrected_text_blob),  # TextBlob correction
        'corrected_text_advanced': corrected_text_tool,  # LanguageTool correction
        'grammar_suggestions': grammar_suggestions
    }

    return jsonify(response)

    # Response compilation
    response = {
        'corrected_text': corrected_text,
        'structure_suggestions': structure_suggestions,
        'cohesiveness_score': blob.sentiment.polarity,  # Basic indicator of positivity/negativity
        'vocab_suggestions': vocab_suggestions,
        'grammar_suggestions': grammar_suggestions
    }

    return jsonify(response)


async def generate_pdf(url, pdf_path):
    browser = await launch()
    page = await browser.newPage()
    
    await page.goto(url, {"waitUntil": "networkidle2"})  # Ensures the page is fully loaded
    await page.pdf({'path': pdf_path, 'format': 'A4'})
    
    await browser.close()

@app.route('/convert_to_pdf', methods=['POST','GET'])
def convert_to_pdf():
    try:
        url = request.form.get('url')
        pdf_path = 'generated_webpage.pdf'
        
        # Run the async function
        asyncio.run(generate_pdf(url, pdf_path))
        
        # Send the generated PDF file as a response
        return send_file(pdf_path, as_attachment=True)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

app.register_blueprint(prossecing.image_app)
app.register_blueprint(wpdf.wPdf)


if __name__ == '__main__':
   
    app.run(host = '0.0.0.0', port=10000)            
            
            
            