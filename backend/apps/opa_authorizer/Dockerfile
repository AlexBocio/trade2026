# OPA Authorizer - Policy-based authorization
FROM openpolicyagent/opa:0.62.0

LABEL maintainer="trade2025"
LABEL description="OPA authorization service for trade2025"

# Copy policies
COPY policy /policy

# Expose OPA API port
EXPOSE 8181

# Run OPA server with policy bundle
CMD ["run", \
     "--server", \
     "--addr", "0.0.0.0:8181", \
     "--log-level", "info", \
     "--log-format", "json", \
     "/policy"]
