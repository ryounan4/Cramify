"""
Flash API that Receives PDFs → Generates cheat sheet → Returns PDF
"""

import os
import io
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from .cheatsheet_pipeline import generate_cheatsheet

app = Flask(__name__)

# Configure CORS to only allow requests from your frontend
# Add your Vercel URL to ALLOWED_ORIGINS environment variable in Railway
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000,https://cramify-six.vercel.app').split(',')
CORS(app, origins=ALLOWED_ORIGINS)

# Security Configuration
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB per file
MAX_FILES = 10  # Maximum 10 files per request
ALLOWED_EXTENSIONS = {'pdf'}


def allowed_file(filename):
    """Check if filename has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_pdf_content(pdf_bytes):
    """Verify file is actually a PDF by checking magic bytes"""
    if len(pdf_bytes) < 4:
        return False
    # PDF files start with %PDF
    return pdf_bytes[:4] == b'%PDF'


@app.route('/api/generate', methods=['POST'])
def generate():

    #Receive PDFs, return cheat sheet

    files = request.files.getlist('files')

    # Validate: Check if any files uploaded
    if not files or len(files) == 0:
        return jsonify({'error': 'No files uploaded'}), 400

    # Validate: Check file count limit
    if len(files) > MAX_FILES:
        return jsonify({'error': f'Maximum {MAX_FILES} files allowed'}), 400

    pdf_files = []
    filenames = []

    for file in files:
        # Validate: Check if filename exists
        if not file.filename:
            return jsonify({'error': 'File has no name'}), 400

        # Validate: Check file extension
        if not allowed_file(file.filename):
            return jsonify({'error': f'Invalid file type: {file.filename}. Only PDF files allowed.'}), 400

        # Sanitize filename (removes dangerous characters like ../)
        safe_filename = secure_filename(file.filename)

        # Validate: Check file size and read content
        pdf_bytes = file.read(MAX_FILE_SIZE + 1)
        if len(pdf_bytes) > MAX_FILE_SIZE:
            return jsonify({'error': f'File too large: {safe_filename}. Maximum size is 50MB.'}), 400

        # Validate: Verify it's actually a PDF (not renamed .exe, etc.)
        if not validate_pdf_content(pdf_bytes):
            return jsonify({'error': f'Invalid PDF file: {safe_filename}'}), 400

        pdf_files.append(pdf_bytes)
        filenames.append(safe_filename)

    print(f" Received {len(pdf_files)} PDF file(s): {filenames}")

    api_key = os.getenv('GEMINI_API_KEY')

    if not api_key:
        return jsonify({'error': 'GEMINI_API_KEY not set on server'}), 500

    # Run the generation pipeline
    try:
        result = generate_cheatsheet(
            pdf_files=pdf_files,
            filenames=filenames,
            api_key=api_key
        )
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': f'Pipeline error: {str(e)}'}), 500

    # Check if generation succeeded
    if not result['success']:
        error_msg = result.get('error', 'Failed to generate cheat sheet')
        return jsonify({'error': error_msg}), 500

    # Return the PDF file to frontend
    if result['pdf_bytes']:
        return send_file(
            io.BytesIO(result['pdf_bytes']),
            mimetype='application/pdf',
            as_attachment=True,
            download_name='cramify-cheatsheet.pdf'
        )
    else:
        return jsonify({'error': 'No PDF generated'}), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'gemini_api_key': '✓' if os.getenv('GEMINI_API_KEY') else '✗'
    })


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    print("Cramify API Server")
    print(f"   Starting on http://0.0.0.0:{port}")
    print()

    app.run(host='0.0.0.0', port=port, debug=False)
