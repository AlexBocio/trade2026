# Phase 3 - Prompt 05: Setup Nginx Reverse Proxy

**Phase**: 3 - Frontend Integration  
**Prompt**: 05 of 08  
**Purpose**: Configure Nginx as unified API gateway  
**Duration**: 4 hours  
**Status**: ⏸️ Ready after Prompt 04 complete

---

## 🛑 PREREQUISITES

- [ ] Prompts 03-04 complete (all mock APIs replaced)
- [ ] Frontend can call backend services directly
- [ ] All backend services running and healthy
- [ ] Docker and docker-compose installed

---

## 🎯 TASK OVERVIEW

### What This Prompt Does

Sets up Nginx as a reverse proxy to:
1. Serve the frontend static files
2. Route API calls to backend services
3. Handle WebSocket connections
4. Provide a single entry point (port 80)
5. Enable CORS and security headers
6. Load balance if needed

---

## 📋 STEP-BY-STEP INSTRUCTIONS

### Step 1: Create Nginx Configuration

```bash
cd C:\ClaudeDesktop_Projects\Trade2026

# Create nginx config directory
mkdir -p config/nginx

# Create main nginx configuration
cat > config/nginx/nginx.conf << 'EOF'
# Trade2026 Nginx Configuration
# Serves frontend and proxies to backend services

worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 4096;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for" '
                    'rt=$request_time uct="$upstream_connect_time" '
                    'uht="$upstream_header_time" urt="$upstream_response_time"';

    access_log /var/log/nginx/access.log main;

    # Performance optimizations
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 20M;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript 
               application/json application/javascript application/xml+rss 
               application/rss+xml application/atom+xml image/svg+xml 
               text/x-js text/x-cross-domain-policy application/x-font-ttf 
               application/x-font-opentype application/vnd.ms-fontobject 
               image/x-icon;

    # Backend service upstreams
    upstream oms {
        least_conn;
        server oms:8099 max_fails=3 fail_timeout=30s;
        keepalive 32;
    }

    upstream risk {
        least_conn;
        server risk:8103 max_fails=3 fail_timeout=30s;
        keepalive 32;
    }

    upstream gateway {
        least_conn;
        server gateway:8080 max_fails=3 fail_timeout=30s;
        keepalive 32;
    }

    upstream live-gateway {
        least_conn;
        server live-gateway:8200 max_fails=3 fail_timeout=30s;
        keepalive 32;
    }

    upstream ptrc {
        least_conn;
        server ptrc:8109 max_fails=3 fail_timeout=30s;
        keepalive 32;
    }

    upstream authn {
        least_conn;
        server authn:8001 max_fails=3 fail_timeout=30s;
        keepalive 32;
    }

    upstream normalizer {
        least_conn;
        server normalizer:8097 max_fails=3 fail_timeout=30s;
        keepalive 32;
    }

    # Rate limiting zones
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/s;
    limit_req_zone $binary_remote_addr zone=auth_limit:10m rate=5r/s;

    # Main server block
    server {
        listen 80 default_server;
        listen [::]:80 default_server;
        server_name localhost;

        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;

        # Frontend root
        root /usr/share/nginx/html;
        index index.html;

        # Frontend routes (React SPA)
        location / {
            try_files $uri $uri/ /index.html;
            
            # Cache static assets
            location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
                expires 1y;
                add_header Cache-Control "public, immutable";
            }
        }

        # Health check endpoint
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }

        # API Routes with rate limiting
        
        # Authentication service (strict rate limit)
        location /api/auth/ {
            limit_req zone=auth_limit burst=10 nodelay;
            
            proxy_pass http://authn/;
            proxy_http_version 1.1;
            
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # CORS headers
            add_header 'Access-Control-Allow-Origin' '$http_origin' always;
            add_header 'Access-Control-Allow-Credentials' 'true' always;
            add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
            add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type' always;
            
            if ($request_method = 'OPTIONS') {
                return 204;
            }
        }

        # OMS service
        location /api/oms/ {
            limit_req zone=api_limit burst=20 nodelay;
            
            proxy_pass http://oms/;
            proxy_http_version 1.1;
            
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header Connection "";
            
            # Timeouts for long-running requests
            proxy_connect_timeout 5s;
            proxy_send_timeout 10s;
            proxy_read_timeout 10s;
            
            # CORS headers
            add_header 'Access-Control-Allow-Origin' '$http_origin' always;
            add_header 'Access-Control-Allow-Credentials' 'true' always;
            add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
            add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type' always;
            
            if ($request_method = 'OPTIONS') {
                return 204;
            }
        }

        # Risk service (low latency critical)
        location /api/risk/ {
            limit_req zone=api_limit burst=50 nodelay;
            
            proxy_pass http://risk/;
            proxy_http_version 1.1;
            
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header Connection "";
            
            # Very short timeouts for risk checks
            proxy_connect_timeout 1s;
            proxy_send_timeout 2s;
            proxy_read_timeout 2s;
            
            # CORS headers
            add_header 'Access-Control-Allow-Origin' '$http_origin' always;
            add_header 'Access-Control-Allow-Credentials' 'true' always;
            add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
            add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type' always;
            
            if ($request_method = 'OPTIONS') {
                return 204;
            }
        }

        # Gateway service (market data)
        location /api/gateway/ {
            limit_req zone=api_limit burst=30 nodelay;
            
            proxy_pass http://gateway/;
            proxy_http_version 1.1;
            
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header Connection "";
            
            # CORS headers
            add_header 'Access-Control-Allow-Origin' '$http_origin' always;
            add_header 'Access-Control-Allow-Credentials' 'true' always;
            add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
            add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type' always;
            
            if ($request_method = 'OPTIONS') {
                return 204;
            }
        }

        # Live Gateway service (order routing)
        location /api/live-gateway/ {
            limit_req zone=api_limit burst=20 nodelay;
            
            proxy_pass http://live-gateway/;
            proxy_http_version 1.1;
            
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header Connection "";
            
            # CORS headers
            add_header 'Access-Control-Allow-Origin' '$http_origin' always;
            add_header 'Access-Control-Allow-Credentials' 'true' always;
            add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
            add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type' always;
            
            if ($request_method = 'OPTIONS') {
                return 204;
            }
        }

        # PTRC service (P&L and reports)
        location /api/ptrc/ {
            limit_req zone=api_limit burst=10 nodelay;
            
            proxy_pass http://ptrc/;
            proxy_http_version 1.1;
            
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header Connection "";
            
            # Longer timeout for report generation
            proxy_connect_timeout 5s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
            
            # CORS headers
            add_header 'Access-Control-Allow-Origin' '$http_origin' always;
            add_header 'Access-Control-Allow-Credentials' 'true' always;
            add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
            add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type' always;
            
            if ($request_method = 'OPTIONS') {
                return 204;
            }
        }

        # Normalizer service (data processing)
        location /api/normalizer/ {
            limit_req zone=api_limit burst=10 nodelay;
            
            proxy_pass http://normalizer/;
            proxy_http_version 1.1;
            
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header Connection "";
            
            # CORS headers
            add_header 'Access-Control-Allow-Origin' '$http_origin' always;
            add_header 'Access-Control-Allow-Credentials' 'true' always;
            add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
            add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type' always;
            
            if ($request_method = 'OPTIONS') {
                return 204;
            }
        }

        # WebSocket support for real-time data
        location /ws {
            proxy_pass http://gateway/ws;
            proxy_http_version 1.1;
            
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # WebSocket timeouts
            proxy_connect_timeout 7d;
            proxy_send_timeout 7d;
            proxy_read_timeout 7d;
        }

        # Metrics endpoint (optional)
        location /metrics {
            stub_status;
            access_log off;
            allow 127.0.0.1;
            deny all;
        }
    }

    # HTTPS server block (optional, for production)
    # server {
    #     listen 443 ssl http2;
    #     listen [::]:443 ssl http2;
    #     server_name trade2026.com;
    #
    #     ssl_certificate /etc/nginx/ssl/cert.pem;
    #     ssl_certificate_key /etc/nginx/ssl/key.pem;
    #     ssl_protocols TLSv1.2 TLSv1.3;
    #     ssl_ciphers HIGH:!aNULL:!MD5;
    #
    #     # Include all location blocks from above
    # }
}
EOF
```

---

### Step 2: Create Docker Configuration for Nginx

```bash
# Create Nginx Dockerfile
cat > config/nginx/Dockerfile << 'EOF'
FROM nginx:alpine

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy our nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# Create directory for frontend files
RUN mkdir -p /usr/share/nginx/html

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost/health || exit 1

# Expose ports
EXPOSE 80 443

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
EOF
```

---

### Step 3: Add Nginx to Docker Compose

```bash
# Create docker-compose file for frontend and nginx
cat > infrastructure/docker/docker-compose.frontend.yml << 'EOF'
version: '3.8'

services:
  nginx:
    build:
      context: ../../config/nginx
      dockerfile: Dockerfile
    container_name: nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ../../frontend/dist:/usr/share/nginx/html:ro
      - nginx_logs:/var/log/nginx
    networks:
      - frontend
      - backend
    depends_on:
      - oms
      - risk
      - gateway
      - live-gateway
      - ptrc
      - authn
    restart: unless-stopped
    labels:
      - "com.trade2026.service=nginx"
      - "com.trade2026.type=gateway"
    healthcheck:
      test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

volumes:
  nginx_logs:
    driver: local

networks:
  frontend:
    external: true
    name: trade2026_frontend
  backend:
    external: true
    name: trade2026_backend
EOF
```

---

### Step 4: Update Frontend Environment for Nginx

```bash
cd C:\ClaudeDesktop_Projects\Trade2026\frontend

# Update production environment to use Nginx routes
cat > .env.production << 'EOF'
# Trade2026 Frontend Production Configuration
# Routes through Nginx on port 80

# Base URL (Nginx)
VITE_API_URL=http://localhost

# Service endpoints via Nginx reverse proxy
VITE_OMS_URL=/api/oms
VITE_RISK_URL=/api/risk
VITE_GATEWAY_URL=/api/gateway
VITE_LIVE_GATEWAY_URL=/api/live-gateway
VITE_PTRC_URL=/api/ptrc
VITE_AUTH_URL=/api/auth

# WebSocket endpoint
VITE_WS_URL=ws://localhost/ws

# Application settings
VITE_APP_NAME=Trade2026
VITE_ENV=production
VITE_LOG_LEVEL=warn

# Feature flags
VITE_ENABLE_PAPER_TRADING=true
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_BACKTESTING=false
EOF
```

---

### Step 5: Build Frontend for Production

```bash
cd C:\ClaudeDesktop_Projects\Trade2026\frontend

# Build production bundle
npm run build

# This creates dist/ directory with:
# - index.html
# - assets/ (JS, CSS, images)
# - favicon.ico

# Verify build output
ls -la dist/
```

**Build Checklist**:
- [ ] Build completes without errors
- [ ] dist/ directory created
- [ ] index.html present
- [ ] JS/CSS bundles created
- [ ] Assets optimized

---

### Step 6: Start Nginx Container

```bash
cd C:\ClaudeDesktop_Projects\Trade2026\infrastructure\docker

# Build and start Nginx
docker-compose -f docker-compose.frontend.yml up -d --build

# Check Nginx is running
docker ps | grep nginx

# Check Nginx logs
docker logs nginx

# Test health endpoint
curl http://localhost/health
# Expected: healthy
```

**Startup Checklist**:
- [ ] Nginx container builds successfully
- [ ] Container starts without errors
- [ ] Health check passes
- [ ] Logs show no errors

---

### Step 7: Test Frontend Through Nginx

```bash
# Open browser to http://localhost

# Test each route:
# 1. Static files loading (check network tab)
# 2. Login page loads
# 3. Can login (calls /api/auth/login)
# 4. Dashboard loads
# 5. API calls go through /api/* routes
# 6. No CORS errors
```

**Testing Checklist**:
- [ ] Frontend loads at http://localhost
- [ ] Static assets served correctly
- [ ] Login works through /api/auth
- [ ] Dashboard data loads
- [ ] Market data displays
- [ ] Orders can be submitted
- [ ] No CORS errors in console
- [ ] WebSocket connects (if used)

---

### Step 8: Test All API Routes

```bash
# Test each API route through Nginx

# Auth service
curl -X POST http://localhost/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@trade2026.com","password":"demo123"}'

# OMS service
curl http://localhost/api/oms/health

# Risk service
curl http://localhost/api/risk/health

# Gateway service
curl http://localhost/api/gateway/health

# Live Gateway service
curl http://localhost/api/live-gateway/health

# PTRC service
curl http://localhost/api/ptrc/health

# All should return successful responses
```

**API Route Checklist**:
- [ ] /api/auth/* routes work
- [ ] /api/oms/* routes work
- [ ] /api/risk/* routes work
- [ ] /api/gateway/* routes work
- [ ] /api/live-gateway/* routes work
- [ ] /api/ptrc/* routes work

---

### Step 9: Configure Logging and Monitoring

```bash
# View Nginx access logs
docker exec nginx tail -f /var/log/nginx/access.log

# View Nginx error logs
docker exec nginx tail -f /var/log/nginx/error.log

# Check upstream connections
docker exec nginx cat /etc/nginx/nginx.conf | grep upstream

# Monitor performance
docker stats nginx
```

Create monitoring script:
```bash
cat > scripts/monitor_nginx.sh << 'EOF'
#!/bin/bash

echo "=== Nginx Status ==="
docker ps | grep nginx

echo -e "\n=== Recent Errors ==="
docker exec nginx tail -20 /var/log/nginx/error.log | grep -v "notice"

echo -e "\n=== Request Stats (last 100) ==="
docker exec nginx tail -100 /var/log/nginx/access.log | \
  awk '{print $9}' | sort | uniq -c | sort -rn | head -10

echo -e "\n=== Upstream Health ==="
for service in oms risk gateway live-gateway ptrc authn; do
  response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/api/$service/health)
  echo "$service: $response"
done

echo -e "\n=== Container Stats ==="
docker stats nginx --no-stream
EOF

chmod +x scripts/monitor_nginx.sh
```

---

### Step 10: Performance Optimization

```bash
# Test Nginx performance
# Install Apache Bench (ab) or use wrk

# Test static file serving
ab -n 1000 -c 10 http://localhost/

# Test API proxy performance
ab -n 100 -c 10 http://localhost/api/gateway/health

# Expected:
# - Static files: < 10ms response time
# - API proxying: < 50ms overhead
```

**Performance Checklist**:
- [ ] Static files served quickly (< 10ms)
- [ ] API proxy overhead minimal (< 50ms)
- [ ] Gzip compression working
- [ ] Keep-alive connections active
- [ ] No connection errors under load

---

## 📋 TROUBLESHOOTING

### Common Issues and Solutions

**1. Nginx won't start**
```bash
# Check config syntax
docker exec nginx nginx -t

# Check for port conflicts
netstat -an | grep :80
```

**2. CORS errors**
```bash
# Verify CORS headers in response
curl -I -X OPTIONS http://localhost/api/oms/health \
  -H "Origin: http://localhost" \
  -H "Access-Control-Request-Method: GET"
```

**3. 502 Bad Gateway errors**
```bash
# Check backend services are running
docker ps | grep -E "oms|risk|gateway"

# Check Nginx can reach backends
docker exec nginx ping oms
```

**4. WebSocket connection fails**
```javascript
// Test WebSocket in browser console
const ws = new WebSocket('ws://localhost/ws');
ws.onopen = () => console.log('Connected');
ws.onerror = (e) => console.error('Error:', e);
```

---

## ✅ PROMPT 05 DELIVERABLES

### Files Created

- [ ] `config/nginx/nginx.conf` - Main Nginx configuration
- [ ] `config/nginx/Dockerfile` - Nginx Docker image
- [ ] `infrastructure/docker/docker-compose.frontend.yml` - Frontend compose file
- [ ] `frontend/.env.production` - Production environment
- [ ] `scripts/monitor_nginx.sh` - Monitoring script

### Services Configured

- [ ] Nginx container running
- [ ] All backend services proxied
- [ ] Frontend static files served
- [ ] WebSocket support configured
- [ ] CORS headers configured
- [ ] Rate limiting configured
- [ ] Health checks configured

### Testing Complete

- [ ] Frontend loads through Nginx
- [ ] All API routes working
- [ ] No CORS errors
- [ ] Authentication works
- [ ] Market data displays
- [ ] Orders can be submitted
- [ ] Performance acceptable

---

## 🚦 VALIDATION GATE

### Nginx Setup Complete?

**Check**:
- [ ] Nginx container running on port 80
- [ ] Frontend accessible at http://localhost
- [ ] All API calls go through /api/* routes
- [ ] No direct backend calls from frontend
- [ ] Authentication working
- [ ] No CORS errors
- [ ] Performance acceptable

**Decision**:
- ✅ ALL WORKING → Proceed to Prompt 06 (containerize frontend)
- ❌ ROUTING ISSUES → Fix Nginx configuration
- ❌ CORS ERRORS → Update CORS headers
- ❌ PERFORMANCE ISSUES → Optimize configuration

---

## 📊 PROMPT 05 COMPLETION CRITERIA

Prompt 05 complete when:

- [ ] Nginx reverse proxy configured and running
- [ ] Frontend served through Nginx
- [ ] All API routes properly proxied
- [ ] No CORS or routing errors
- [ ] WebSocket support working (if needed)
- [ ] Performance optimized
- [ ] Monitoring in place
- [ ] COMPLETION_TRACKER.md updated

**Next Prompt**: PHASE3_PROMPT06_BUILD_CONTAINERIZE_FRONTEND.md

---

**Prompt Status**: ⏸️ READY (after Prompt 04 complete)

**Estimated Time**: 4 hours

**Outcome**: Unified API gateway with Nginx serving frontend and proxying to backends
