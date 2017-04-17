FROM python:2.7

WORKDIR /app/
COPY requirements.txt .

RUN apt update; apt install -y imagemagick ghostscript
RUN pip install -r requirements.txt

COPY fd_rechenwesen.py .
COPY templates/ ./templates/
COPY frontpage.html .

ENV GUNICORN_CMD_ARGS="--bind=0.0.0.0"

CMD ["gunicorn", "fd_rechenwesen:app"]