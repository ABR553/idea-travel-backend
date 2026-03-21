#!/bin/bash
set -e
echo "Running migrations..."
alembic upgrade head
echo "Generating Postman collection..."
python -m scripts.generate_postman
echo "Starting API server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
