from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
filename = ''
format = ''
# Set the upload folder path
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allowed extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'docx'}

# Check if the file is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    global filename, format
    if request.method == 'POST':
        # Check if the POST request has the file part
        format = request.form.get('format')
        print(format)
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, browser may submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('File successfully uploaded')
            return redirect(url_for('download_page', filename=filename))
    return render_template('index.html')

@app.route('/download')
def download_page():
    return render_template('download.html', filename = filename)

@app.route('/uploads/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename,  download_name=f'{filename}.{format}',  as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
