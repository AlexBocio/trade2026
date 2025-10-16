# Data Normalizer Service
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir \
    fastapi==0.104.1 \
    uvicorn==0.24.0 \
    nats-py==2.6.0 \
    redis==5.0.1 \
    httpx==0.25.0 \
    pyyaml==6.0.1

# Copy application files
COPY main.py /app/
# Note: config.yaml will be mounted from config/backend/normalizer/

# Create log directory
RUN mkdir -p /var/log/normalizer

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8081/health || exit 1

# Expose port
EXPOSE 8081

# Run the service
CMD ["python", "-u", "main.py"]