
FROM python:3.12-slim

WORKDIR /app

# Update OS packages to receive available security fixes
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

COPY --chown=appuser:appgroup app/ ./app/

EXPOSE 8002

USER appuser

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]

