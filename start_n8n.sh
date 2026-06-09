#!/bin/zsh
# start_n8n.sh — starts n8n with correct HTTPS webhook config for Telegram

NGROK_URL="https://55a4-2405-201-c003-5823-506e-8ba1-5ec1-2c38.ngrok-free.app"

export N8N_HOST="0.0.0.0"
export N8N_PORT="5678"
export N8N_PROTOCOL="https"
export WEBHOOK_URL="${NGROK_URL}/"
export N8N_EDITOR_BASE_URL="http://localhost:5678"

echo "Starting n8n with:"
echo "  WEBHOOK_URL = $WEBHOOK_URL"
echo "  N8N_PROTOCOL = $N8N_PROTOCOL"

exec n8n start --data-dir /Users/rameshinampudi/n8n/.n8n
