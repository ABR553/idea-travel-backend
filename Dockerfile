FROM python:3.12-slim AS base
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM base AS development
COPY . .
CMD ["bash", "entrypoint.sh"]

FROM base AS production
COPY . .
CMD ["bash", "entrypoint.prod.sh"]
