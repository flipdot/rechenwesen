import os

from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)

UPLOAD_DIR = os.environ.get('UPLOAD_DIR', os.path.join(os.path.dirname(__file__), 'upload'))

if not (os.path.exists(UPLOAD_DIR)):
    os.makedirs(UPLOAD_DIR)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    elif request.method == 'POST':
        print(request.form)
        print(request.files)
        for pdf_filepath, file in request.files.items():
            if not file.filename:
                return render_template('index.html', message='Irgendwas war komisch', error=True)
            pdf_filepath = '{}_{}'.format(
                datetime.now().isoformat(),
                secure_filename(file.filename),
            )
            pdf_filepath = os.path.sep.join((UPLOAD_DIR, pdf_filepath))
            file.save(pdf_filepath)
            txt_filepath = pdf_filepath.replace('.pdf', '.txt')
            with open(txt_filepath, 'w') as f:
                get = lambda x: request.form.get(x, '').replace('\n', '') + '\n'
                getlist = lambda x: ','.join([y.replace('\n', '') for y in request.form.getlist(x)]) + '\n'
                f.writelines([
                    get('shop-name'),
                    getlist('tags'),
                    get('price'),
                ])
        return render_template('index.html', message='Danke für dein Wisch!')
    return 'Strange thinks happend'


if __name__ == '__main__':
    app.run(debug=True)
