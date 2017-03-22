FROM python:alpine

WORKDIR /app/
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY fd_rechenwesen.py .
COPY templates/ ./templates/

ENV GUNICORN_CMD_ARGS="--bind=0.0.0.0"

CMD ["gunicorn", "fd_rechenwesen:app"]