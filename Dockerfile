FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV OLLAMA_HOST=127.0.0.1:11434
ENV OLLAMA_MODELS=/opt/ollama/models
ENV PROOFPRINT_MODEL=gemma4:e2b

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates zstd \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://ollama.com/install.sh | sh

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chmod +x start.sh

EXPOSE 7860

CMD ["./start.sh"]
