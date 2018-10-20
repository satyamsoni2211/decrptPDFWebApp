import os
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
from flask import send_from_directory
from PyPDF2 import PdfFileReader, PdfFileWriter

DECRYPT = '/home/vedika/Documents/utils/decrypt'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
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

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            decrypt_pdf(file, \
            os.path.join(app.config['DECRYPT_FOLDER'], filename),
            'ECVPS4023N13061993')
            return redirect(url_for('decrypted_file',
                                    filename=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

@app.route('/decrypt/<filename>')
def decrypted_file(filename):
    return send_from_directory(app.config['DECRYPT_FOLDER'],
                               filename)

if __name__ == '__main__':
    app.run()