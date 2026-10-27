# coding=utf-8
import os
import secrets
import shutil
from easywebdav import connect as easywebdav_connect

from flask import Flask, request, render_template, Response, current_app
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
dir_path = os.path.dirname(os.path.realpath(__file__))

username = os.environ.get('WEBDAV_USER') or "rechenwesen"
password = os.environ.get('WEBDAV_PASSWORD')

# Basic-Auth (Issue #1): nur aktiv, wenn AUTH_PASSWORD gesetzt ist.
# Ohne gesetztes Passwort bleibt die Seite frei erreichbar (Tests, lokale Dev).
app.config['AUTH_USER'] = os.environ.get('AUTH_USER') or "rechenwesen"
app.config['AUTH_PASSWORD'] = os.environ.get('AUTH_PASSWORD')

webdav = easywebdav_connect("cloud.flipdot.org", protocol='https', username=username, password=password)


def _unauthorized():
    return Response(
        "Authentifizierung erforderlich",
        status=401,
        headers={'WWW-Authenticate': 'Basic realm="flipdot Rechenwesen"'},
    )


@app.before_request
def require_auth():
    """Blockt alle Requests, wenn AUTH_PASSWORD gesetzt ist und die
    Basic-Auth-Credentials nicht stimmen. Ohne AUTH_PASSWORD: kein Schutz."""
    auth_password = current_app.config.get('AUTH_PASSWORD')
    if not auth_password:
        return None

    auth = request.authorization
    username = getattr(auth, 'username', None) if auth else None
    password = getattr(auth, 'password', None) if auth else None

    user_ok = secrets.compare_digest(username or "", current_app.config.get('AUTH_USER') or "")
    pass_ok = secrets.compare_digest(password or "", auth_password)
    if not (user_ok and pass_ok):
        return _unauthorized()


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html', message="")
    elif request.method == 'POST':
        for filepath, file in request.files.items():
            if not file.filename:
                return render_template('index.html', message='Irgendwas war komisch', error=True)

            filepath = '{}_{}'.format(
                datetime.now().isoformat(),
                secure_filename(file.filename),
            )

            filepath = os.path.sep.join(("/tmp", filepath))
            file.save(filepath)

            pdf_filepath = filepath + ".pdf"
            os.system("convert \""+ filepath + "\" \""+pdf_filepath+"\"")

            frontpage_path = filepath + "-frontpage.pdf"
            frontpage_template = filepath + "-frontpage.html"

            get = lambda x: request.form.get(x, '').replace('\n', '') + '\n'
            getlist = lambda x: ','.join([y.replace('\n', '') for y in request.form.getlist(x)]) + '\n'

            shop_name = get('shop-name')
            tags = getlist('tags')
            price = get('price')
            person = get('person')
            iban = get('iban')

            replacements = {
                '{{SHOPNAME}}': shop_name,
                '{{TAGS}}': tags,
                '{{BETRAG}}': price,
                '{{PERSON}}': person,
                '{{IBAN}}': iban,
            }
            with open(dir_path + "/frontpage.html") as infile, open(frontpage_template, 'w') as outfile:
                for line in infile:
                    for src, target in list(replacements.items()):
                        line = line.replace(src, target)
                    outfile.write(line)

            os.system("weasyprint \""+frontpage_template+"\" \""+frontpage_path+"\"")

            final_pdf = filepath + "-final.pdf"
            os.system('gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite -sOutputFile="'+final_pdf+'" "'+frontpage_path+'" "'+pdf_filepath+'"')

            pdf_filename = os.path.basename(pdf_filepath)
            remote_path = "/remote.php/webdav/Rechenwesen-Belege/" + pdf_filename
            webdav.upload(final_pdf, remote_path)

            os.remove(pdf_filepath)
            os.remove(frontpage_path)
            os.remove(final_pdf)
            os.remove(frontpage_template)

        return render_template('index.html', message=u'Danke für dein Wisch!')
    return 'Strange thinks happend'


if __name__ == '__main__':
    # Debug-Modus nur explizit via FLASK_DEBUG=1, sonst aus (kein RCE über die
    # Werkzeug-Debugger-Konsole). Produktion läuft ohnehin über Gunicorn.
    app.run(debug=os.environ.get('FLASK_DEBUG', '0') == '1')
