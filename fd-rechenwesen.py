import os

from flask import Flask, request, render_template
from werkzeug.utils import secure_filename

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
        for filename, file in request.files.items():
            filename = secure_filename(file.filename)
            file.save(os.path.sep.join((UPLOAD_DIR, filename)))
        return render_template('index.html', message='Danke für dein Wisch!')
    return 'Strange thinks happend'


if __name__ == '__main__':
    app.run(debug=True)
