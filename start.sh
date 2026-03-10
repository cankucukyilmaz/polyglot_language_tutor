#!/bin/bash

echo "Checking if Voice & STT models exist..."
# This runs the download script INSIDE the Docker container!
python scripts/setup_models.py

echo "Starting the Polyglot AI Tutor server..."
uvicorn src.main:app --host 0.0.0.0 --port 8000