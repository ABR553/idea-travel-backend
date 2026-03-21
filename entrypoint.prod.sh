#!/bin/bash
set -e
echo "Running migrations..."
alembic upgrade head
echo "Starting API server on port ${PORT:-8000}..."
exec gunicorn app.main:app \
    -w 4 \
    -k uvicorn.workers.UvicornWorker \
    --bind "0.0.0.0:${PORT:-8000}"
