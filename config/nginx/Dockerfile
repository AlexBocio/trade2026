FROM nginx:alpine

# Option 2B Architecture: Static files only (Traefik handles API routing)
LABEL com.trade2026.version="2.0-traefik"
LABEL com.trade2026.description="Frontend static file server (nginx internal)"

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy simplified nginx config (static files only, no API proxying)
COPY nginx-static-only.conf /etc/nginx/nginx.conf

# Create directory for frontend files
RUN mkdir -p /usr/share/nginx/html

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost/health || exit 1

# Expose port (internal only - Traefik routes externally)
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
