FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PORT=8080

WORKDIR /app

RUN addgroup \
        --system \
        --gid 10001 \
        performancelab \
    && adduser \
        --system \
        --uid 10001 \
        --ingroup performancelab \
        performancelab

COPY pyproject.toml README.md ./
COPY performancelab ./performancelab

RUN python -m pip install --upgrade pip \
    && python -m pip install .

COPY app ./app
COPY migrations ./migrations
COPY alembic.ini ./

RUN chown -R performancelab:performancelab /app

USER performancelab

EXPOSE 8080

HEALTHCHECK \
    --interval=30s \
    --timeout=5s \
    --start-period=30s \
    --retries=3 \
    CMD python -c \
    "import os, urllib.request; urllib.request.urlopen(f'http://127.0.0.1:{os.environ.get(\"PORT\", \"8080\")}/_stcore/health', timeout=3)"

CMD ["sh", "-c", "python -m streamlit run app/app.py --server.address=0.0.0.0 --server.port=${PORT:-8080} --server.headless=true"]