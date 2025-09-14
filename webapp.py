#!/usr/bin/env python3
from flask import Flask, render_template, request, Response, send_file
import tempfile
import os
import base64
import urllib.parse
import io
from image_to_ascii import create_ascii_art, save_ascii_image
from prompt_to_ascii import create_image

app = Flask(__name__)

CHARSETS = {
    'standard': ' .-~:+=*#%@',
    'blocks': ' ░▒▓█',
    'dots': ' .oO@',
    'dense': '@%#*+=-:. ',
    'binary': '01',
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    uploaded = request.files.get('image')
    if not uploaded or uploaded.filename == '':
        return 'No image uploaded', 400
    width = int(request.form.get('width', 160))
    custom_charset = request.form.get('custom_charset', '').strip()
    charset_key = request.form.get('charset', 'standard')
    charset = custom_charset or CHARSETS.get(charset_key, CHARSETS['standard'])
    suffix = os.path.splitext(uploaded.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        uploaded.save(tmp.name)
        ascii_art = create_ascii_art(tmp.name, ascii_chars=charset, width=width)
    data = urllib.parse.quote_plus(base64.b64encode(ascii_art.encode()).decode())
    return render_template('result.html', ascii_art=ascii_art, data=data)

@app.route('/prompt', methods=['POST'])
def prompt_to_ascii():
    prompt = request.form.get('prompt')
    if not prompt:
        return 'No prompt provided', 400
    width = int(request.form.get('width', 160))
    custom_charset = request.form.get('custom_charset', '').strip()
    charset_key = request.form.get('charset', 'standard')
    charset = custom_charset or CHARSETS.get(charset_key, CHARSETS['standard'])
    with tempfile.NamedTemporaryFile(delete=False, suffix='.webp') as tmp:
        create_image(prompt, tmp.name)
        ascii_art = create_ascii_art(tmp.name, ascii_chars=charset, width=width)
    data = urllib.parse.quote_plus(base64.b64encode(ascii_art.encode()).decode())
    return render_template('result.html', ascii_art=ascii_art, data=data)

@app.route('/download/txt')
def download_txt():
    data = request.args.get('data')
    if not data:
        return 'No data provided', 400
    ascii_art = base64.b64decode(data.encode()).decode()
    return Response(
        ascii_art,
        mimetype='text/plain',
        headers={'Content-Disposition': 'attachment; filename=ascii_art.txt'}
    )

@app.route('/download/img')
def download_img():
    data = request.args.get('data')
    if not data:
        return 'No data provided', 400
    ascii_art = base64.b64decode(data.encode()).decode()
    buf = io.BytesIO()
    save_ascii_image(ascii_art, buf)
    buf.seek(0)
    return send_file(buf, mimetype='image/png', as_attachment=True, download_name='ascii_art.png')

if __name__ == '__main__':
    app.run(debug=True)
