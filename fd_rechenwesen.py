# coding=utf-8
import os
import shutil
from easywebdav import connect as easywebdav_connect

from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
dir_path = os.path.dirname(os.path.realpath(__file__))

username = os.environ.get('WEBDAV_USER') or "rechenwesen"
password = os.environ.get('WEBDAV_PASSWORD')

webdav = easywebdav_connect("cloud.flipdot.org", protocol='https', username=username, password=password)


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

            replacements = {'{{SHOPNAME}}': shop_name, '{{TAGS}}': tags, '{{BETRAG}}': price}
            with open(dir_path + "/frontpage.html") as infile, open(frontpage_template, 'w') as outfile:
                for line in infile:
                    for src, target in replacements.iteritems():
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
    app.run(debug=True)
