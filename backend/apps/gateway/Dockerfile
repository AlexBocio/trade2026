# Multi-stage build for Trade2025 Market Gateway
FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /build

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final stage
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 -s /bin/bash trader

# Set working directory
WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /root/.local /home/trader/.local

# Copy application files
COPY --chown=trader:trader main.py .
COPY --chown=trader:trader config.yaml .

# Create writable log directory for cryptofeed
RUN mkdir -p /app/logs && chown trader:trader /app/logs

# Set Python path
ENV PATH=/home/trader/.local/bin:$PATH
ENV PYTHONPATH=/home/trader/.local/lib/python3.11/site-packages

# Switch to non-root user
USER trader

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# Expose FastAPI port
EXPOSE 8080

# Run the application
CMD ["python", "-u", "main.py"]