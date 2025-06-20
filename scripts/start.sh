#!/bin/bash
set -e
 
# Run uvicorn from the /app directory
# Use --no-access-log to keep logs clean
exec /usr/local/bin/python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --no-access-log 