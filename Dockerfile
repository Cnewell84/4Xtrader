# Base stage with common dependencies
FROM python:3.9-slim AS base
WORKDIR /app

# Set Python to not write bytecode and not buffer output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    rm -rf /root/.cache/pip/* && \
    find /usr/local -name '*.pyc' -delete && \
    find /usr/local -name '__pycache__' -delete

# Copy all Python modules
COPY *.py .
COPY utils/ ./utils/
COPY templates/ ./templates/

# Create and set permissions for data directories
RUN mkdir -p /app/data /app/logs && \
    chmod -R 777 /app/data /app/logs

ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

CMD ["python", "app.py"]

# API stage
FROM base AS api
EXPOSE 5000
CMD ["python", "app.py"]

# Trading agent stage
FROM base AS trading_agent
CMD ["python", "live_trading.py"]

# Batch jobs stage
FROM base AS batch_jobs
CMD ["python", "auto_retrain.py"]

