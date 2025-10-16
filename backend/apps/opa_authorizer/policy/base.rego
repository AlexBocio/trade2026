package authz

import future.keywords.in
import future.keywords.if

# Default deny - explicit allow required
default allow := false
default reason := "No matching allow rule"

# ============================================
# RBAC: Role-Based Permissions
# ============================================

role_permissions := {
	"oms": {
		"orders.create",
		"orders.cancel",
		"orders.replace",
		"orders.read",
		"positions.read",
		"executions.read",
	},
	"order_manager": {
		"orders.create",
		"orders.cancel",
		"orders.replace",
		"orders.read",
		"positions.read",
		"executions.read",
		"risk.eval",
	},
	"live_gateway": {
		"broker.submit",
		"broker.cancel",
		"broker.query",
		"marketdata.subscribe",
		"fills.publish",
	},
	"broker": {
		"broker.submit",
		"broker.cancel",
		"broker.query",
	},
	"serving": {
		"inference.predict",
		"models.read",
		"features.read",
	},
	"ml_inference": {
		"inference.predict",
		"models.read",
		"models.write",
		"features.read",
	},
	"risk": {
		"risk.eval",
		"limits.read",
		"limits.update",
		"positions.read",
		"orders.read",
	},
	"risk_manager": {
		"risk.eval",
		"limits.read",
		"limits.update",
		"limits.override",
		"positions.read",
		"orders.read",
		"orders.cancel",
	},
	"trader": {
		"orders.create",
		"orders.cancel",
		"orders.read",
		"positions.read",
		"executions.read",
		"marketdata.subscribe",
	},
	"human": {
		"orders.read",
		"positions.read",
		"executions.read",
		"marketdata.subscribe",
	},
}

# Check if any of the principal's roles has permission for the action
has_role_permission if {
	some role in input.roles
	input.action in role_permissions[role]
}

# ============================================
# ABAC: Attribute-Based Access Control
# ============================================

# Trading hours check (example: US equity market)
trading_hours_ok if {
	# Skip check if not equity or not IBKR
	not input.context.asset_class == "equity"
}

trading_hours_ok if {
	not input.context.venue == "IBKR"
}

trading_hours_ok if {
	input.context.asset_class == "equity"
	input.context.venue == "IBKR"

	# Parse hour from context (should be Unix timestamp)
	# For demo, assume context.now_hour is provided in ET
	hour := input.context.now_hour

	# Market hours: 9:30 AM - 4:00 PM ET
	# For simplicity, 9-16 (would need to handle 9:30 start properly)
	hour >= 9
	hour < 16

	# TODO: Add holiday calendar check
	# not is_market_holiday(input.context.date)
}

# Circuit breaker check
circuit_breaker_ok if {
	not input.context.circuit_breaker_active
}

circuit_breaker_ok if {
	not input.context.circuit_breaker_active == true
}

# Canary mode: limit order volume for new venues
canary_ok if {
	# No canary restrictions if venue not in canary list
	not input.context.venue in {"NEW_CRYPTO_EXCHANGE", "NEW_FOREX_VENUE"}
}

canary_ok if {
	input.context.venue in {"NEW_CRYPTO_EXCHANGE", "NEW_FOREX_VENUE"}

	# Max 100 orders per day during canary
	input.context.daily_order_count < 100

	# Max $10k notional per order
	input.context.order_notional < 10000
}

# Position limit check
position_limit_ok if {
	not input.action == "orders.create"
}

position_limit_ok if {
	input.action == "orders.create"

	# Check if position limit would be exceeded
	input.context.position_size < input.context.position_limit
}

# Account allowlist (tenant-level access control)
account_allowed if {
	# If no account restrictions for tenant, allow
	not input.tenant in tenant_account_restrictions
}

account_allowed if {
	input.tenant in tenant_account_restrictions
	input.context.account_id in tenant_account_restrictions[input.tenant]
}

tenant_account_restrictions := {
	"demo": {"demo-001", "demo-002"},
	"paper": {"paper-001", "paper-002", "paper-003"},
	# Production tenant has access to all accounts
}

# Venue allowlist (per tenant)
venue_allowed if {
	not input.tenant in tenant_venue_restrictions
}

venue_allowed if {
	input.tenant in tenant_venue_restrictions
	input.context.venue in tenant_venue_restrictions[input.tenant]
}

tenant_venue_restrictions := {
	"demo": {"SIMULATED", "PAPER"},
	"paper": {"PAPER", "CCXT"},
	# Production tenant has access to all venues
}

# ============================================
# Main Allow Rule
# ============================================

allow if {
	# Must have role permission
	has_role_permission

	# Must pass ABAC checks
	trading_hours_ok
	circuit_breaker_ok
	canary_ok
	position_limit_ok
	account_allowed
	venue_allowed
}

# Set reason for denial
reason := msg if {
	not has_role_permission
	msg := sprintf("Role %v does not have permission for action '%s'", [input.roles, input.action])
}

reason := "Trading hours restriction" if {
	has_role_permission
	not trading_hours_ok
}

reason := "Circuit breaker active" if {
	has_role_permission
	trading_hours_ok
	not circuit_breaker_ok
}

reason := "Canary mode restrictions" if {
	has_role_permission
	trading_hours_ok
	circuit_breaker_ok
	not canary_ok
}

reason := "Position limit would be exceeded" if {
	has_role_permission
	trading_hours_ok
	circuit_breaker_ok
	canary_ok
	not position_limit_ok
}

reason := sprintf("Account '%s' not allowed for tenant '%s'", [input.context.account_id, input.tenant]) if {
	has_role_permission
	trading_hours_ok
	circuit_breaker_ok
	canary_ok
	position_limit_ok
	not account_allowed
}

reason := sprintf("Venue '%s' not allowed for tenant '%s'", [input.context.venue, input.tenant]) if {
	has_role_permission
	trading_hours_ok
	circuit_breaker_ok
	canary_ok
	position_limit_ok
	account_allowed
	not venue_allowed
}

# ============================================
# Rate Limit Key Generation
# ============================================

rate_limit_key := key if {
	# For write operations, rate limit by (tenant, subject, action)
	input.action in {"orders.create", "orders.cancel", "orders.replace"}
	key := sprintf("%s:%s:%s", [input.tenant, input.sub, input.action])
}

rate_limit_key := key if {
	# For read operations, rate limit by (tenant, subject)
	not input.action in {"orders.create", "orders.cancel", "orders.replace"}
	key := sprintf("%s:%s", [input.tenant, input.sub])
}

# ============================================
# Audit Context (for logging)
# ============================================

audit_context := {
	"sub": input.sub,
	"action": input.action,
	"resource": input.resource,
	"tenant": input.tenant,
	"allow": allow,
	"reason": reason,
	"timestamp": time.now_ns(),
}
