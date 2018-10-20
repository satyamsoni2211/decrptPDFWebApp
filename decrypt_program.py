import os
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
from flask import send_from_directory
from PyPDF2 import PdfFileReader, PdfFileWriter
import sys

ALLOWED_EXTENSIONS = set(['pdf'])

app = Flask(__name__)
DECRYPT = os.path.join(app.root_path, 'decrypt')
app.config['DECRYPT_FOLDER'] = DECRYPT

def decrypt_pdf(input_file, output_path, password):
  with open(output_path, 'wb') as output_file:
    reader = PdfFileReader(input_file)
    reader.decrypt(password)

    writer = PdfFileWriter()

    for i in range(reader.getNumPages()):
      writer.addPage(reader.getPage(i))

    writer.write(output_file)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def removeFiles():
    for i in os.listdir(app.config['DECRYPT_FOLDER']):
        os.remove(os.path.join(app.config['DECRYPT_FOLDER'],i))

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        removeFiles()
        password = request.form['password'].decode().encode(sys.getdefaultencoding())
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            try:
                decrypt_pdf(file, \
                os.path.join(app.config['DECRYPT_FOLDER'], filename),
                password)
                # return redirect(url_for('decrypted_file',
                #                         filename=filename))
                return render_template('decrypt.html', filename=filename)
            except:
                return render_template('decrypt.html', fail=filename)
        if not allowed_file(file.filename):
            filename = secure_filename(file.filename)
            return render_template('decrypt.html', incorrect=filename)

    return render_template('decrypt.html')

@app.route('/decrypt/<filename>')
def decrypted_file(filename):
    return send_from_directory(app.config['DECRYPT_FOLDER'],
                               filename)

if __name__ == '__main__':
    app.run(debug=True)