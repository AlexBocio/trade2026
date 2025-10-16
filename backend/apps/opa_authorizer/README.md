# OPA Authorizer

Policy-based authorization service for trade2025 using Open Policy Agent (OPA).

## Overview

The OPA Authorizer enforces authorization policies using Rego, supporting both:
- **RBAC (Role-Based Access Control)** - Permissions mapped to roles
- **ABAC (Attribute-Based Access Control)** - Context-aware decisions (time, venue, limits)

## Architecture

```
Service (OMS/Gateway/Risk/Serving)
    ↓ HTTP POST
OPA Authorizer (port 8181)
    ↓ Evaluates
Policy (base.rego)
    ↓ Returns
Decision: {allow: bool, reason: string}
```

## Policies

### RBAC Roles

| Role | Permissions |
|------|-------------|
| `oms` | orders.create, orders.cancel, orders.replace, orders.read, positions.read, executions.read |
| `order_manager` | All oms permissions + risk.eval |
| `live_gateway` | broker.submit, broker.cancel, broker.query, marketdata.subscribe, fills.publish |
| `broker` | broker.submit, broker.cancel, broker.query |
| `serving` | inference.predict, models.read, features.read |
| `ml_inference` | All serving permissions + models.write |
| `risk` | risk.eval, limits.read, limits.update, positions.read, orders.read |
| `risk_manager` | All risk permissions + limits.override, orders.cancel |
| `trader` | orders.create, orders.cancel, orders.read, positions.read, executions.read, marketdata.subscribe |
| `human` | orders.read, positions.read, executions.read, marketdata.subscribe |

### ABAC Rules

1. **Trading Hours** - Equity orders on IBKR restricted to 9 AM - 4 PM ET
2. **Circuit Breaker** - Block all orders when `circuit_breaker_active=true`
3. **Canary Mode** - Limit new venues to 100 orders/day, $10k max notional
4. **Position Limits** - Block orders that would exceed position limits
5. **Account Allowlist** - Restrict demo/paper tenants to specific accounts
6. **Venue Allowlist** - Restrict demo/paper tenants to specific venues

## API

### Authorization Decision

**Endpoint:** `POST /v1/data/authz`

**Request:**
```json
{
  "input": {
    "sub": "srv:oms",
    "roles": ["oms", "order_manager"],
    "tenant": "prod",
    "action": "orders.create",
    "resource": "order:new",
    "context": {
      "venue": "IBKR",
      "asset_class": "equity",
      "now_hour": 14,
      "account_id": "prod-001",
      "position_size": 1500,
      "position_limit": 10000,
      "order_notional": 5000,
      "circuit_breaker_active": false
    }
  }
}
```

**Response (Allowed):**
```json
{
  "result": {
    "allow": true,
    "reason": "No matching allow rule",
    "rate_limit_key": "prod:srv:oms:orders.create",
    "audit_context": {
      "sub": "srv:oms",
      "action": "orders.create",
      "resource": "order:new",
      "tenant": "prod",
      "allow": true,
      "reason": "No matching allow rule",
      "timestamp": 1696512000000000000
    }
  }
}
```

**Response (Denied - Trading Hours):**
```json
{
  "result": {
    "allow": false,
    "reason": "Trading hours restriction",
    "rate_limit_key": "prod:srv:oms:orders.create",
    "audit_context": {...}
  }
}
```

**Response (Denied - No Permission):**
```json
{
  "result": {
    "allow": false,
    "reason": "Role [\"human\"] does not have permission for action 'orders.create'",
    "rate_limit_key": "prod:user:trader1",
    "audit_context": {...}
  }
}
```

## Usage

### Deploy Standalone

```bash
# Build image
cd apps/opa_authorizer
podman build -t localhost/opa:latest .

# Run OPA
podman run -d --name opa \
  -p 8181:8181 \
  localhost/opa:latest

# Check health
curl http://localhost:8181/health
```

### Test Policy

```bash
# Test allowed request
curl -X POST http://localhost:8181/v1/data/authz \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "sub": "srv:oms",
      "roles": ["oms"],
      "tenant": "prod",
      "action": "orders.create",
      "resource": "order:new",
      "context": {
        "venue": "CCXT",
        "asset_class": "crypto"
      }
    }
  }' | jq '.result.allow'
# Output: true

# Test denied request (wrong role)
curl -X POST http://localhost:8181/v1/data/authz \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "sub": "user:viewer",
      "roles": ["human"],
      "tenant": "prod",
      "action": "orders.create",
      "resource": "order:new",
      "context": {}
    }
  }' | jq '.result | {allow, reason}'
# Output: {"allow": false, "reason": "Role [\"human\"] does not have permission for action 'orders.create'"}

# Test denied request (trading hours)
curl -X POST http://localhost:8181/v1/data/authz \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "sub": "srv:oms",
      "roles": ["oms"],
      "tenant": "prod",
      "action": "orders.create",
      "resource": "order:new",
      "context": {
        "venue": "IBKR",
        "asset_class": "equity",
        "now_hour": 20
      }
    }
  }' | jq '.result | {allow, reason}'
# Output: {"allow": false, "reason": "Trading hours restriction"}
```

### Integration with Services

Using `security_lib`:

```python
from fastapi import FastAPI, Depends
from security_lib import (
    create_jwt_verifier,
    create_opa_client,
    get_principal,
    require_permission,
    SecurityPrincipal
)

app = FastAPI()

@app.on_event("startup")
async def startup():
    # Initialize JWT verifier
    create_jwt_verifier("http://authn:8114/.well-known/jwks.json")

    # Initialize OPA client
    create_opa_client("http://opa:8181")

# Simple permission check
@app.get("/positions", dependencies=[Depends(require_permission("positions.read"))])
async def list_positions(principal: SecurityPrincipal = Depends(get_principal)):
    return {"positions": [...]}

# Permission check with context
def get_order_context(request, symbol: str) -> dict:
    return {
        "venue": request.headers.get("X-Venue", "CCXT"),
        "asset_class": "crypto",
        "account_id": request.headers.get("X-Account-Id", "prod-001")
    }

@app.post("/orders",
          dependencies=[Depends(require_permission("orders.create", context_func=get_order_context))])
async def create_order(symbol: str, quantity: float):
    # Order creation logic
    return {"order_id": "12345"}
```

## Policy Development

### Adding New Roles

Edit `policy/base.rego`:

```rego
role_permissions := {
    "new_role": {
        "new.permission",
        "another.permission",
    },
    ...
}
```

### Adding ABAC Rules

```rego
# Check if user is internal employee
internal_user_ok if {
    startswith(input.sub, "user:")
    input.context.employee_id != ""
}

# Update main allow rule
allow if {
    has_role_permission
    internal_user_ok  # Add new check
    trading_hours_ok
    ...
}

# Add reason for denial
reason := "Internal users only" if {
    has_role_permission
    not internal_user_ok
}
```

### Testing Policies Locally

```bash
# Install OPA CLI
brew install opa  # or download from https://www.openpolicyagent.org/docs/latest/#1-download-opa

# Test policy with sample input
opa eval -d policy/base.rego \
  -i test_input.json \
  'data.authz.allow'

# Run OPA interactively (REPL)
opa run policy/base.rego

# Run policy tests (if you create test files)
opa test policy/
```

## Configuration

OPA runs with these settings:
- **Port:** 8181
- **Log Level:** info
- **Log Format:** json
- **Policy Path:** /policy

To customize, edit Dockerfile `CMD` arguments.

## Monitoring

### Health Check

```bash
curl http://localhost:8181/health
# Output: {}  (empty response = healthy)
```

### Metrics (Prometheus)

OPA exposes metrics at `/metrics`:

```bash
curl http://localhost:8181/metrics
```

Key metrics:
- `http_request_duration_seconds` - Request latency
- `opa_decision_count` - Number of policy decisions
- `opa_decision_duration_seconds` - Policy evaluation time

## Production Considerations

1. **Policy Updates** - Use OPA bundles for zero-downtime policy updates
2. **Caching** - Enable decision caching for read-heavy workloads
3. **Audit Logging** - Stream decision logs to centralized logging
4. **High Availability** - Run multiple OPA instances behind load balancer
5. **Performance** - OPA evaluates policies in microseconds, but network latency matters

## License

Apache-2.0 (OPA is Apache-2.0 licensed)
