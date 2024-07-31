from flask import Flask, request, render_template, redirect, url_for, flash
import os
import fitz  # PyMuPDF

from extract import extract_highlighted_paragraphs_with_pages

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'  # Folder to store uploaded files
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max file size

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/home', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and file.filename.endswith('.pdf'):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            paragraphs = extract_highlighted_paragraphs_with_pages(file_path)
            return render_template('results.html', paragraphs=paragraphs)
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)