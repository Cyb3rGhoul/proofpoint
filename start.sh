#!/usr/bin/env sh
set -eu

ollama serve &
OLLAMA_PID=$!

echo "Waiting for Ollama..."
until curl -fsS http://127.0.0.1:11434/api/tags >/dev/null 2>&1; do
  sleep 2
done

echo "Pulling Gemma model if needed: ${PROOFPRINT_MODEL:-gemma4:e2b}"
ollama pull "${PROOFPRINT_MODEL:-gemma4:e2b}"

streamlit run app.py \
  --server.address 0.0.0.0 \
  --server.port 7860 \
  --server.headless true \
  --browser.gatherUsageStats false

kill "$OLLAMA_PID"
