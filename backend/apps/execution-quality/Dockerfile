FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 trader

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=trader:trader . .

# Create config directory and set permissions
RUN mkdir -p /app/config && chown -R trader:trader /app

# Switch to non-root user
USER trader

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8092/health || exit 1

# Expose ports
EXPOSE 8092 9092

# Run the service
CMD ["python", "-u", "service.py"]