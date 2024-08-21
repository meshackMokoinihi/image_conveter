from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, current_app
import os 
from blueprints.prossecing import image_app



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
        # Check if the POST request has the file part
        format = request.form.get('format')
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']

        # If the user does not select a file, the browser may submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_files(file.filename):
            filename = file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            flash('File successfully uploaded')
            
            return redirect(url_for('image_app.pdf_to_image', filename=filename, extension=request.form.get('format')))
        
    return render_template('index.html')



@app.route('/download')
def download_page():
    return render_template('download.html', filename=filename)



@app.route('/upload/<filename>/')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, download_name=f'{filename}', as_attachment=True)


app.register_blueprint(image_app)



if __name__ == '__main__':
    app.run(host = '0.0.0.0' ,debug=True)            
            
            
            