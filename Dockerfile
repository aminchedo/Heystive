FROM python:3.11-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends build-essential ffmpeg libsndfile1 portaudio19-dev curl && rm -rf /var/lib/apt/lists/*
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
FROM base AS runtime
WORKDIR /app
COPY . /app
ENV LOG_DIR=/app/.logs
RUN mkdir -p /app/.logs /app/models
EXPOSE 8765
HEALTHCHECK --interval=10s --timeout=3s --retries=5 --start-period=10s CMD curl -fsS http://127.0.0.1:8765/healthz || exit 1
CMD ["python", "server/main.py"]