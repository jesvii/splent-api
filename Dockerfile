FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=run.py
ENV FLASK_ENV=production
ENV PORT=80
ENV PACKAGES_FILE=/data/packages.json
ENV PACKAGE_SOURCES=github,registry

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /data

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1/health', timeout=3).read()"


CMD ["gunicorn", "--bind", "0.0.0.0:80", "--workers", "2", "run:app"]
