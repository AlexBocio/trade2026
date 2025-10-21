# Phase 3 - Prompt 06: Build and Containerize Frontend

**Phase**: 3 - Frontend Integration  
**Prompt**: 06 of 08  
**Purpose**: Create production Docker image for frontend  
**Duration**: 3 hours  
**Status**: ⏸️ Ready after Prompt 05 complete

---

## 🛑 PREREQUISITES

- [ ] Prompt 05 complete (Nginx configured)
- [ ] Frontend builds successfully
- [ ] All API integrations working
- [ ] Docker installed

---

## 🎯 TASK OVERVIEW

### What This Prompt Does

Creates a production-ready Docker container for the frontend:
1. Multi-stage Docker build
2. Optimized production bundle
3. Minimal final image
4. Integrated with backend services
5. Environment variable configuration
6. Health checks

---

## 📋 STEP-BY-STEP INSTRUCTIONS

### Step 1: Create Multi-Stage Dockerfile

```bash
cd C:\ClaudeDesktop_Projects\Trade2026\frontend

# Create optimized Dockerfile
cat > Dockerfile << 'EOF'
# Trade2026 Frontend Production Dockerfile
# Multi-stage build for optimal size and security

# Stage 1: Dependencies
FROM node:18-alpine AS dependencies

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install production dependencies
RUN npm ci --only=production

# Copy all dependencies (including dev) for build
COPY package*.json ./
RUN npm ci

# Stage 2: Build
FROM node:18-alpine AS builder

WORKDIR /app

# Copy dependencies from previous stage
COPY --from=dependencies /app/node_modules ./node_modules

# Copy source code
COPY . .

# Build arguments for environment variables
ARG VITE_API_URL=/api
ARG VITE_OMS_URL=/api/oms
ARG VITE_RISK_URL=/api/risk
ARG VITE_GATEWAY_URL=/api/gateway
ARG VITE_LIVE_GATEWAY_URL=/api/live-gateway
ARG VITE_PTRC_URL=/api/ptrc
ARG VITE_AUTH_URL=/api/auth
ARG VITE_WS_URL=/ws
ARG VITE_APP_NAME=Trade2026
ARG VITE_ENV=production

# Set environment variables for build
ENV VITE_API_URL=$VITE_API_URL \
    VITE_OMS_URL=$VITE_OMS_URL \
    VITE_RISK_URL=$VITE_RISK_URL \
    VITE_GATEWAY_URL=$VITE_GATEWAY_URL \
    VITE_LIVE_GATEWAY_URL=$VITE_LIVE_GATEWAY_URL \
    VITE_PTRC_URL=$VITE_PTRC_URL \
    VITE_AUTH_URL=$VITE_AUTH_URL \
    VITE_WS_URL=$VITE_WS_URL \
    VITE_APP_NAME=$VITE_APP_NAME \
    VITE_ENV=$VITE_ENV

# Build the application
RUN npm run build

# Stage 3: Production
FROM nginx:alpine AS production

# Install curl for health checks
RUN apk add --no-cache curl

# Copy custom nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# Copy built application from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001 && \
    chown -R nodejs:nodejs /usr/share/nginx/html && \
    chown -R nodejs:nodejs /var/cache/nginx && \
    chown -R nodejs:nodejs /var/log/nginx && \
    chown -R nodejs:nodejs /etc/nginx/conf.d && \
    touch /var/run/nginx.pid && \
    chown -R nodejs:nodejs /var/run/nginx.pid

# Expose port 80
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost/health || exit 1

# Switch to non-root user
USER nodejs

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
EOF
```

---

### Step 2: Create Frontend-Specific Nginx Config

```bash
# Create nginx config for frontend container
cat > nginx.conf << 'EOF'
# Nginx configuration for frontend container
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent"';

    access_log /var/log/nginx/access.log main;

    # Performance settings
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript 
               application/json application/javascript application/xml+rss 
               application/rss+xml application/atom+xml image/svg+xml;

    server {
        listen 80;
        server_name localhost;
        root /usr/share/nginx/html;
        index index.html;

        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;

        # Health check endpoint
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }

        # Serve static files with caching
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
            access_log off;
        }

        # React app - serve index.html for all routes
        location / {
            try_files $uri $uri/ /index.html;
            
            # Don't cache index.html
            location = /index.html {
                add_header Cache-Control "no-cache, no-store, must-revalidate";
                add_header Pragma "no-cache";
                add_header Expires "0";
            }
        }

        # API routes (when running standalone, proxy to backend)
        # These are handled by the main Nginx gateway in production
        location /api/ {
            return 503 "API gateway not configured in standalone mode";
            add_header Content-Type text/plain;
        }
    }
}
EOF
```

---

### Step 3: Create Docker Compose for Frontend

```bash
# Update docker-compose to include frontend
cat > infrastructure/docker/docker-compose.frontend-app.yml << 'EOF'
version: '3.8'

services:
  frontend:
    build:
      context: ../../frontend
      dockerfile: Dockerfile
      args:
        - VITE_API_URL=/api
        - VITE_OMS_URL=/api/oms
        - VITE_RISK_URL=/api/risk
        - VITE_GATEWAY_URL=/api/gateway
        - VITE_LIVE_GATEWAY_URL=/api/live-gateway
        - VITE_PTRC_URL=/api/ptrc
        - VITE_AUTH_URL=/api/auth
        - VITE_WS_URL=/ws
        - VITE_APP_NAME=Trade2026
        - VITE_ENV=production
    image: localhost/trade2026-frontend:latest
    container_name: trade2026-frontend
    ports:
      - "3000:80"  # Expose on port 3000 for standalone testing
    networks:
      - frontend
    restart: unless-stopped
    labels:
      - "com.trade2026.service=frontend"
      - "com.trade2026.type=ui"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 256M
        reservations:
          cpus: '0.25'
          memory: 128M

networks:
  frontend:
    external: true
    name: trade2026_frontend
EOF
```

---

### Step 4: Create Build Script

```bash
# Create build script for CI/CD
cat > scripts/build_frontend.sh << 'EOF'
#!/bin/bash

# Trade2026 Frontend Build Script
set -e

echo "🚀 Building Trade2026 Frontend..."

# Change to frontend directory
cd "$(dirname "$0")/../frontend"

# Check Node.js version
node_version=$(node -v)
echo "Node.js version: $node_version"

# Install dependencies
echo "📦 Installing dependencies..."
npm ci

# Run tests (if available)
if [ -f "package.json" ] && grep -q "\"test\"" package.json; then
    echo "🧪 Running tests..."
    npm test -- --run || echo "⚠️ Tests failed or not configured"
fi

# Build production bundle
echo "🔨 Building production bundle..."
npm run build

# Check build output
if [ ! -d "dist" ]; then
    echo "❌ Build failed: dist/ directory not created"
    exit 1
fi

# Calculate bundle size
bundle_size=$(du -sh dist | cut -f1)
echo "📊 Bundle size: $bundle_size"

# Build Docker image
echo "🐳 Building Docker image..."
docker build \
    -t localhost/trade2026-frontend:latest \
    -t localhost/trade2026-frontend:$(date +%Y%m%d-%H%M%S) \
    .

echo "✅ Frontend build complete!"
echo ""
echo "To run standalone:"
echo "  docker run -p 3000:80 localhost/trade2026-frontend:latest"
echo ""
echo "To deploy with backend:"
echo "  cd infrastructure/docker"
echo "  docker-compose -f docker-compose.frontend-app.yml up -d"
EOF

chmod +x scripts/build_frontend.sh
```

---

### Step 5: Build Frontend Image

```bash
cd C:\ClaudeDesktop_Projects\Trade2026

# Run build script
./scripts/build_frontend.sh

# Or manually:
cd frontend
npm ci
npm run build
docker build -t localhost/trade2026-frontend:latest .

# Verify image was created
docker images | grep trade2026-frontend
```

**Build Checklist**:
- [ ] Dependencies installed
- [ ] Production build successful
- [ ] Docker image built
- [ ] Image tagged correctly
- [ ] No build errors

---

### Step 6: Test Frontend Container

```bash
# Run frontend container standalone
docker run -d \
    --name trade2026-frontend-test \
    -p 3000:80 \
    localhost/trade2026-frontend:latest

# Check container is running
docker ps | grep trade2026-frontend-test

# Test health endpoint
curl http://localhost:3000/health
# Expected: healthy

# Open browser to http://localhost:3000
# Should see the app (API calls will fail in standalone mode)

# Check container logs
docker logs trade2026-frontend-test

# Stop test container
docker stop trade2026-frontend-test
docker rm trade2026-frontend-test
```

**Test Checklist**:
- [ ] Container starts successfully
- [ ] Health check passes
- [ ] Frontend loads in browser
- [ ] Static assets served
- [ ] No errors in logs

---

### Step 7: Integrate with Full Stack

```bash
cd C:\ClaudeDesktop_Projects\Trade2026\infrastructure\docker

# Start full stack with containerized frontend
docker-compose \
    -f docker-compose.base.yml \
    -f docker-compose.apps.yml \
    -f docker-compose.frontend.yml \
    -f docker-compose.frontend-app.yml \
    up -d

# Verify all services running
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Test through main Nginx gateway
curl http://localhost/health
curl http://localhost/api/oms/health
curl http://localhost/api/risk/health

# Open browser to http://localhost
# Full app should work with real backend
```

**Integration Checklist**:
- [ ] All services running
- [ ] Frontend accessible through Nginx
- [ ] API calls working
- [ ] Authentication working
- [ ] Can submit orders
- [ ] Market data displays

---

### Step 8: Optimize Image Size

```bash
# Check image size
docker images localhost/trade2026-frontend:latest

# Analyze image layers
docker history localhost/trade2026-frontend:latest

# Run security scan
docker scout cves localhost/trade2026-frontend:latest || \
    trivy image localhost/trade2026-frontend:latest || \
    echo "Install docker scout or trivy for security scanning"
```

Create optimized Dockerfile if needed:
```dockerfile
# ... existing stages ...

# Additional optimizations
FROM nginx:alpine AS production

# Remove unnecessary files
RUN rm -rf /usr/share/nginx/html/* \
    && rm -rf /etc/nginx/conf.d/default.conf

# Copy only necessary files
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

# Minimize layers
RUN apk add --no-cache curl && \
    addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001 && \
    chown -R nodejs:nodejs /usr/share/nginx/html /var/cache/nginx /var/log/nginx /etc/nginx/conf.d && \
    touch /var/run/nginx.pid && \
    chown nodejs:nodejs /var/run/nginx.pid

# ... rest of Dockerfile ...
```

---

### Step 9: Create Deployment Documentation

```bash
cat > frontend/DEPLOYMENT.md << 'EOF'
# Trade2026 Frontend Deployment

## Building

### Local Build
```bash
npm ci
npm run build
```

### Docker Build
```bash
docker build -t localhost/trade2026-frontend:latest .
```

### Using Build Script
```bash
../scripts/build_frontend.sh
```

## Running

### Standalone (Testing)
```bash
docker run -d -p 3000:80 localhost/trade2026-frontend:latest
```

### With Full Stack
```bash
cd ../infrastructure/docker
docker-compose \
    -f docker-compose.base.yml \
    -f docker-compose.apps.yml \
    -f docker-compose.frontend.yml \
    -f docker-compose.frontend-app.yml \
    up -d
```

## Configuration

Environment variables are baked into the image at build time:
- `VITE_API_URL` - Base API URL
- `VITE_*_URL` - Service endpoints
- See Dockerfile for full list

## Health Check

```bash
curl http://localhost/health
```

## Monitoring

```bash
# Container logs
docker logs trade2026-frontend

# Container stats
docker stats trade2026-frontend

# Inside container
docker exec -it trade2026-frontend sh
```

## Troubleshooting

### Container won't start
- Check port 80 is not in use
- Verify image built successfully
- Check docker logs

### Assets not loading
- Verify dist/ was created during build
- Check nginx.conf paths
- Inspect browser network tab

### API calls failing
- Verify backend services running
- Check Nginx gateway configuration
- Verify environment variables

## Security

- Runs as non-root user (nodejs:1001)
- Alpine Linux base for minimal attack surface
- Security headers configured in nginx.conf
- Regular updates recommended

## Performance

- Gzip compression enabled
- Static assets cached for 1 year
- index.html not cached
- Multi-stage build for smaller image
- Resource limits configured in docker-compose
EOF
```

---

### Step 10: Create CI/CD Pipeline (GitHub Actions Example)

```bash
cat > .github/workflows/frontend.yml << 'EOF'
name: Frontend CI/CD

on:
  push:
    branches: [ main, develop ]
    paths:
      - 'frontend/**'
      - '.github/workflows/frontend.yml'
  pull_request:
    branches: [ main ]
    paths:
      - 'frontend/**'

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
        cache-dependency-path: frontend/package-lock.json
    
    - name: Install dependencies
      working-directory: frontend
      run: npm ci
    
    - name: Run tests
      working-directory: frontend
      run: npm test -- --run
      continue-on-error: true
    
    - name: Build production bundle
      working-directory: frontend
      run: npm run build
    
    - name: Build Docker image
      working-directory: frontend
      run: |
        docker build -t trade2026-frontend:${{ github.sha }} .
        docker tag trade2026-frontend:${{ github.sha }} trade2026-frontend:latest
    
    - name: Save Docker image
      if: github.ref == 'refs/heads/main'
      run: |
        docker save trade2026-frontend:latest | gzip > frontend-image.tar.gz
    
    - name: Upload artifact
      if: github.ref == 'refs/heads/main'
      uses: actions/upload-artifact@v3
      with:
        name: frontend-docker-image
        path: frontend-image.tar.gz
        retention-days: 7
EOF
```

---

## ✅ PROMPT 06 DELIVERABLES

### Files Created

- [ ] `frontend/Dockerfile` - Multi-stage Docker build
- [ ] `frontend/nginx.conf` - Container nginx config
- [ ] `frontend/DEPLOYMENT.md` - Deployment documentation
- [ ] `infrastructure/docker/docker-compose.frontend-app.yml` - Frontend compose
- [ ] `scripts/build_frontend.sh` - Build automation script
- [ ] `.github/workflows/frontend.yml` - CI/CD pipeline (optional)

### Docker Images

- [ ] Frontend image built successfully
- [ ] Image tagged appropriately
- [ ] Image size optimized (< 100MB ideal)
- [ ] Security scan passed

### Testing Complete

- [ ] Container runs standalone
- [ ] Health check works
- [ ] Integrates with full stack
- [ ] Frontend accessible
- [ ] API calls working
- [ ] No errors in logs

---

## 🚦 VALIDATION GATE

### Containerization Complete?

**Check**:
- [ ] Docker image builds without errors
- [ ] Container starts successfully
- [ ] Health check passes
- [ ] Frontend serves correctly
- [ ] Image size reasonable (< 200MB)
- [ ] Runs as non-root user
- [ ] Integrates with backend services

**Decision**:
- ✅ ALL COMPLETE → Proceed to Prompt 07 (integration testing)
- ❌ BUILD FAILS → Fix Dockerfile
- ❌ RUNTIME ERRORS → Check configuration
- ❌ INTEGRATION ISSUES → Verify networking

---

## 📊 PROMPT 06 COMPLETION CRITERIA

Prompt 06 complete when:

- [ ] Frontend Docker image created
- [ ] Multi-stage build optimized
- [ ] Container runs successfully
- [ ] Health checks configured
- [ ] Security best practices applied
- [ ] Documentation complete
- [ ] Integration verified
- [ ] COMPLETION_TRACKER.md updated

**Next Prompt**: PHASE3_PROMPT07_INTEGRATION_TESTING.md

---

**Prompt Status**: ⏸️ READY (after Prompt 05 complete)

**Estimated Time**: 3 hours

**Outcome**: Production-ready containerized frontend with optimized Docker image
