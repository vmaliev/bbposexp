#!/bin/bash
export $(grep -v '^#' ../.env | xargs)
export WEB_APP_URL="https://1e8ab031daab.ngrok-free.app"
./venv/bin/uvicorn server:app --host 0.0.0.0 --port 8000
