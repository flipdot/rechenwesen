from flask import Flask, request, render_template

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    elif request.method == 'POST':
        print(request.form)
        print(request.files)
        return render_template('index.html', message='Danke für dein Wisch!')
    return 'Strange thinks happend'


if __name__ == '__main__':
    app.run(debug=True)
