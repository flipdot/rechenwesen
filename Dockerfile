FROM python:3.12-slim

# C libraries the weasyprint CLI needs (pango/harfbuzz/gdk-pixbuf), plus the
# imagemagick (convert) and ghostscript (gs) CLIs the app shells out to.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ghostscript \
        imagemagick \
        libgdk-pixbuf-2.0-0 \
        libharfbuzz-subset0 \
        libpango-1.0-0 \
        libpangoft2-1.0-0 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

WORKDIR /app
COPY pyproject.toml uv.lock .python-version ./
RUN uv venv .venv && uv sync --frozen --no-dev

COPY fd_rechenwesen.py .
COPY templates/ ./templates/
COPY frontpage.html .

# The app runs `weasyprint` as a CLI, so the venv must be on PATH.
ENV PATH="/app/.venv/bin:$PATH"
ENV GUNICORN_CMD_ARGS="--bind=0.0.0.0"

CMD ["gunicorn", "fd_rechenwesen:app"]
