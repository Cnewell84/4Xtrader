# Base stage with common dependencies
FROM python:3.9-slim as base
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# API stage
FROM base as api
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]

# Trading agent stage
FROM base as trading_agent
COPY . .
CMD ["python", "live_trading.py"]

# Batch jobs stage
FROM base as batch_jobs
COPY . .
CMD ["python", "auto_retrain.py"]
