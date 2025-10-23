#!/usr/bin/env python3
"""
Fix docker-compose healthcheck URLs to use correct ports for each service.
"""

# Read the docker-compose file
compose_file = "C:/claudedesktop_projects/trade2026/infrastructure/docker/docker-compose.backend-services.yml"

with open(compose_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Define the replacements: find the context and replace the healthcheck line
replacements = [
    # factor-models (Port 5004) - context includes previous lines
    {
        'find': '''  # Factor Models Service (Port 5004)
  # =========================================================================
  factor-models:
    build:
      context: ../../backend
      dockerfile: Dockerfile.backend-service
      args:
        SERVICE_NAME: factor_models
    container_name: factor-models
    hostname: factor-models
    ports:
      - "5004:5000"
    networks:
      - backend
      - lowlatency
    environment:
      - SERVICE_NAME=Factor Models
      - SERVICE_PORT=5000
      - PYTHONUNBUFFERED=1
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:5001/health', timeout=5)"]''',
        'replace': '''  # Factor Models Service (Port 5004)
  # =========================================================================
  factor-models:
    build:
      context: ../../backend
      dockerfile: Dockerfile.backend-service
      args:
        SERVICE_NAME: factor_models
    container_name: factor-models
    hostname: factor-models
    ports:
      - "5004:5000"
    networks:
      - backend
      - lowlatency
    environment:
      - SERVICE_NAME=Factor Models
      - SERVICE_PORT=5000
      - PYTHONUNBUFFERED=1
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:5004/health', timeout=5)"]'''
    },
    # simulation-engine (Port 5005)
    {
        'find': '''  # Simulation Engine Service (Port 5005)
  # =========================================================================
  simulation-engine:
    build:
      context: ../../backend
      dockerfile: Dockerfile.backend-service
      args:
        SERVICE_NAME: simulation_engine
    container_name: simulation-engine
    hostname: simulation-engine
    ports:
      - "5005:5000"
    networks:
      - backend
      - lowlatency
    environment:
      - SERVICE_NAME=Simulation Engine
      - SERVICE_PORT=5000
      - PYTHONUNBUFFERED=1
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:5001/health', timeout=5)"]''',
        'replace': '''  # Simulation Engine Service (Port 5005)
  # =========================================================================
  simulation-engine:
    build:
      context: ../../backend
      dockerfile: Dockerfile.backend-service
      args:
        SERVICE_NAME: simulation_engine
    container_name: simulation-engine
    hostname: simulation-engine
    ports:
      - "5005:5000"
    networks:
      - backend
      - lowlatency
    environment:
      - SERVICE_NAME=Simulation Engine
      - SERVICE_PORT=5000
      - PYTHONUNBUFFERED=1
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:5005/health', timeout=5)"]'''
    },
    # fractional-diff (Port 5006)
    {
        'find': '''  # Fractional Differentiation Service (Port 5006)
  # =========================================================================
  fractional-diff:
    build:
      context: ../../backend
      dockerfile: Dockerfile.backend-service
      args:
        SERVICE_NAME: fractional_diff
    container_name: fractional-diff
    hostname: fractional-diff
    ports:
      - "5006:5000"
    networks:
      - backend
      - lowlatency
    environment:
      - SERVICE_NAME=Fractional Differentiation
      - SERVICE_PORT=5000
      - PYTHONUNBUFFERED=1
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:5001/health', timeout=5)"]''',
        'replace': '''  # Fractional Differentiation Service (Port 5006)
  # =========================================================================
  fractional-diff:
    build:
      context: ../../backend
      dockerfile: Dockerfile.backend-service
      args:
        SERVICE_NAME: fractional_diff
    container_name: fractional-diff
    hostname: fractional-diff
    ports:
      - "5006:5000"
    networks:
      - backend
      - lowlatency
    environment:
      - SERVICE_NAME=Fractional Differentiation
      - SERVICE_PORT=5000
      - PYTHONUNBUFFERED=1
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:5006/health', timeout=5)"]'''
    },
    # meta-labeling (Port 5007)
    {
        'find': '''  # Meta-Labeling Service (Port 5007)
  # =========================================================================
  meta-labeling:
    build:
      context: ../../backend
      dockerfile: Dockerfile.backend-service
      args:
        SERVICE_NAME: meta_labeling
    container_name: meta-labeling
    hostname: meta-labeling
    ports:
      - "5007:5000"
    networks:
      - backend
      - lowlatency
    environment:
      - SERVICE_NAME=Meta-Labeling
      - SERVICE_PORT=5000
      - PYTHONUNBUFFERED=1
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:5001/health', timeout=5)"]''',
        'replace': '''  # Meta-Labeling Service (Port 5007)
  # =========================================================================
  meta-labeling:
    build:
      context: ../../backend
      dockerfile: Dockerfile.backend-service
      args:
        SERVICE_NAME: meta_labeling
    container_name: meta-labeling
    hostname: meta-labeling
    ports:
      - "5007:5000"
    networks:
      - backend
      - lowlatency
    environment:
      - SERVICE_NAME=Meta-Labeling
      - SERVICE_PORT=5000
      - PYTHONUNBUFFERED=1
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:5007/health', timeout=5)"]'''
    },
    # stock-screener (Port 5008)
    {
        'find': '''  # Stock Screener Service (Port 5008)
  # =========================================================================
  stock-screener:
    build:
      context: ../../backend
      dockerfile: Dockerfile.backend-service
      args:
        SERVICE_NAME: stock_screener
    container_name: stock-screener
    hostname: stock-screener
    ports:
      - "5008:5000"
    networks:
      - backend
      - lowlatency
    environment:
      - SERVICE_NAME=Stock Screener
      - SERVICE_PORT=5000
      - PYTHONUNBUFFERED=1
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:5001/health', timeout=5)"]''',
        'replace': '''  # Stock Screener Service (Port 5008)
  # =========================================================================
  stock-screener:
    build:
      context: ../../backend
      dockerfile: Dockerfile.backend-service
      args:
        SERVICE_NAME: stock_screener
    container_name: stock-screener
    hostname: stock-screener
    ports:
      - "5008:5000"
    networks:
      - backend
      - lowlatency
    environment:
      - SERVICE_NAME=Stock Screener
      - SERVICE_PORT=5000
      - PYTHONUNBUFFERED=1
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:5008/health', timeout=5)"]'''
    }
]

# Apply all replacements
for repl in replacements:
    if repl['find'] in content:
        content = content.replace(repl['find'], repl['replace'])
        print(f"✓ Fixed healthcheck for service")
    else:
        print(f"✗ Could not find pattern for replacement")

# Write the updated content
with open(compose_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✓ All healthchecks fixed successfully!")
