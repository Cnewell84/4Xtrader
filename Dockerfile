# Base stage with common dependencies
FROM python:3.9-slim AS base
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# API stage
FROM base AS api
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]

# Trading agent stage
FROM base AS trading_agent
COPY . .
CMD ["python", "live_trading.py"]

# Batch jobs stage
FROM base AS batch_jobs
COPY . .
CMD ["python", "auto_retrain.py"]
