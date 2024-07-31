from flask import Flask, request, render_template, redirect, url_for, flash, make_response
import os
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak

import fitz  # PyMuPDF
from extract import extract_highlighted_paragraphs_with_pages

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'  # Folder to store uploaded files
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max file size
app.secret_key = 'your_secret_key'  # Required for flash messages

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/', methods=['GET', 'POST'])
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
            global current_file_path
            current_file_path = file_path
            paragraphs = extract_highlighted_paragraphs_with_pages(file_path)
            return render_template('results.html', paragraphs=paragraphs)
    return render_template('home.html')

@app.route('/download_pdf')
def download_pdf():
    if 'current_file_path' not in globals():
        flash('No file selected')
        return redirect(url_for('upload_file'))

    # Create a BytesIO object to hold the PDF data in memory
    pdf_buffer = BytesIO()
    
    # Create a SimpleDocTemplate to manage the PDF layout
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Build the PDF content
    story = []

    # Add title
    title_style = styles['Title']
    story.append(Paragraph("Highlighted Text from PDF", title_style))
    story.append(Spacer(1, 12))

    # Extract highlights
    paragraphs = extract_highlighted_paragraphs_with_pages(current_file_path)
    
    for page, paragraph in paragraphs:
        story.append(Paragraph(f"<b>Page {page}</b>", styles['Heading2']))
        story.append(Spacer(1, 6))
        # Ensure text wrapping and proper layout
        body_style = styles['BodyText']
        story.append(Paragraph(paragraph, body_style))
        story.append(Spacer(1, 12))
    
    # Build the PDF
    doc.build(story)
    
    # Rewind the buffer
    pdf_buffer.seek(0)

    # Send the generated PDF to the browser
    response = make_response(pdf_buffer.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=highlights.pdf'
    return response

if __name__ == '__main__':
    app.run(debug=True)
