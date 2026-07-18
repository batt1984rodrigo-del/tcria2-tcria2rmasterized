FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TCRIA_ENV=production \
    TCRIA_JOB_ROOT=/var/lib/tcria/jobs

RUN apt-get update \
    && apt-get install --yes --no-install-recommends poppler-utils tesseract-ocr tesseract-ocr-por \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir --requirement requirements.txt
COPY . .
RUN mkdir -p /var/lib/tcria/jobs && chown -R nobody:nogroup /var/lib/tcria

USER nobody
EXPOSE 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers"]
