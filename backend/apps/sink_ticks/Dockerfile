# Sink Ticks Service
# Phase 7B: Data Lake Sinks

FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 sinkuser

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=sinkuser:sinkuser . .

# Switch to non-root user
USER sinkuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8111/health || exit 1

# Expose ports
EXPOSE 8111 9111

# Run service
CMD ["python", "/app/service.py"]