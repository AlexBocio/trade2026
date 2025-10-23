#!/bin/bash
# Generate self-signed certificates for development
# Phase 15.6: CPGS v1.0 - TLS for Traefik

set -e

CERT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DAYS=365  # 1 year validity

echo "==================================="
echo "Generating Development Certificates"
echo "==================================="
echo "Directory: $CERT_DIR"
echo

# ========================================
# 1. Generate CA (Certificate Authority)
# ========================================
echo "[1/4] Generating CA private key..."
openssl genrsa -out "$CERT_DIR/ca.key" 4096

echo "[1/4] Generating CA certificate..."
openssl req -x509 -new -nodes \
  -key "$CERT_DIR/ca.key" \
  -sha256 \
  -days $DAYS \
  -out "$CERT_DIR/ca.crt" \
  -subj "/C=US/ST=NY/L=NewYork/O=Trade2025/OU=DevCA/CN=Trade2025 Dev CA"

echo "✓ CA certificate created: ca.crt"

# ========================================
# 2. Generate Wildcard Certificate
# ========================================
echo
echo "[2/4] Generating wildcard private key..."
openssl genrsa -out "$CERT_DIR/dev-wildcard.key" 2048

echo "[2/4] Generating wildcard CSR..."
openssl req -new \
  -key "$CERT_DIR/dev-wildcard.key" \
  -out "$CERT_DIR/dev-wildcard.csr" \
  -subj "/C=US/ST=NY/L=NewYork/O=Trade2025/OU=Dev/CN=*.local"

# Create SAN config
cat > "$CERT_DIR/wildcard.ext" <<EOF
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
subjectAltName = @alt_names

[alt_names]
DNS.1 = *.local
DNS.2 = localhost
DNS.3 = *.trade2025.local
DNS.4 = trade2025.local
IP.1 = 127.0.0.1
IP.2 = ::1
EOF

echo "[2/4] Signing wildcard certificate with CA..."
openssl x509 -req \
  -in "$CERT_DIR/dev-wildcard.csr" \
  -CA "$CERT_DIR/ca.crt" \
  -CAkey "$CERT_DIR/ca.key" \
  -CAcreateserial \
  -out "$CERT_DIR/dev-wildcard.crt" \
  -days $DAYS \
  -sha256 \
  -extfile "$CERT_DIR/wildcard.ext"

echo "✓ Wildcard certificate created: dev-wildcard.crt"

# ========================================
# 3. Generate Traefik Client Certificate (for mTLS)
# ========================================
echo
echo "[3/4] Generating Traefik client certificate..."
openssl genrsa -out "$CERT_DIR/traefik-client.key" 2048

openssl req -new \
  -key "$CERT_DIR/traefik-client.key" \
  -out "$CERT_DIR/traefik-client.csr" \
  -subj "/C=US/ST=NY/L=NewYork/O=Trade2025/OU=Traefik/CN=traefik.local"

cat > "$CERT_DIR/client.ext" <<EOF
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature, keyEncipherment
extendedKeyUsage = clientAuth
subjectAltName = DNS:traefik.local
EOF

openssl x509 -req \
  -in "$CERT_DIR/traefik-client.csr" \
  -CA "$CERT_DIR/ca.crt" \
  -CAkey "$CERT_DIR/ca.key" \
  -CAcreateserial \
  -out "$CERT_DIR/traefik-client.crt" \
  -days $DAYS \
  -sha256 \
  -extfile "$CERT_DIR/client.ext"

echo "✓ Traefik client certificate created: traefik-client.crt"

# ========================================
# 4. Cleanup
# ========================================
echo
echo "[4/4] Cleaning up temporary files..."
rm -f "$CERT_DIR"/*.csr "$CERT_DIR"/*.ext "$CERT_DIR"/*.srl

# ========================================
# 5. Set Permissions
# ========================================
echo "[4/4] Setting permissions..."
chmod 600 "$CERT_DIR"/*.key
chmod 644 "$CERT_DIR"/*.crt

# ========================================
# Summary
# ========================================
echo
echo "==================================="
echo "Certificate Generation Complete"
echo "==================================="
echo
echo "Files created:"
echo "  CA:                 ca.crt, ca.key"
echo "  Wildcard (Traefik): dev-wildcard.crt, dev-wildcard.key"
echo "  Client (mTLS):      traefik-client.crt, traefik-client.key"
echo
echo "Validity: $DAYS days"
echo
echo "To trust the CA in your browser:"
echo "  - Chrome/Edge: Settings → Security → Manage certificates → Authorities → Import ca.crt"
echo "  - Firefox: Settings → Privacy & Security → Certificates → View Certificates → Authorities → Import ca.crt"
echo "  - macOS: Keychain Access → System → Import ca.crt → Trust → Always Trust"
echo "  - Linux: sudo cp ca.crt /usr/local/share/ca-certificates/ && sudo update-ca-certificates"
echo
echo "Access services via:"
echo "  https://superset.local"
echo "  https://traefik.local/dashboard/"
echo "  https://grafana.local"
echo
echo "NOTE: Add entries to /etc/hosts:"
echo "  127.0.0.1  superset.local traefik.local grafana.local serving.local"
echo
