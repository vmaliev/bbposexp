#!/bin/bash
echo "Starting script..." > debug_script.log
cd "$(dirname "$0")"
echo "Changed directory to $(pwd)" >> debug_script.log
source venv/bin/activate
echo "Activated venv" >> debug_script.log
which uvicorn >> debug_script.log
./venv/bin/uvicorn server:app --host 0.0.0.0 --port 8000 --timeout-keep-alive 60 > server_standalone.log 2>&1
echo "Uvicorn exited with $?" >> debug_script.log