# IBKR Gateway Setup Guide for Trade2026

## Prerequisites
- IB Gateway or TWS installed
- Valid IBKR account (live or paper trading)

---

## Step 1: Enable API Connections in IB Gateway

### Open IB Gateway Configuration
1. Launch **IB Gateway** (not TWS, unless you prefer TWS)
2. Log in with your credentials
3. Go to **File** → **Global Configuration** → **API** → **Settings**

### Configure API Settings
Enable these settings:

| Setting | Value | Why |
|---------|-------|-----|
| **Enable ActiveX and Socket Clients** | ✅ Checked | Allows external applications to connect |
| **Socket Port** | **4002** | Port for IB Gateway (4001 for TWS) |
| **Master API Client ID** | Leave empty or set to 0 | Allow any client ID |
| **Read-Only API** | ❌ Unchecked | Trade2026 needs write access for orders |
| **Download open orders on connection** | ✅ Checked | See existing orders |

### Add Trusted IP Addresses
**CRITICAL**: Add these IPs to allow Docker containers to connect:

```
127.0.0.1
192.168.65.254
192.168.65.0/24
```

**How to add**:
1. In API Settings, find **Trusted IP Addresses** section
2. Click **Add** or enter in the text field
3. Add all three addresses above
4. Click **OK** to save

---

## Step 2: Configure Socket Port

### IB Gateway Port Configuration
- **IB Gateway**: Port **4002** (default)
- **TWS (Trader Workstation)**: Port **4001**

If using TWS instead of Gateway, update Trade2026 config:
```yaml
# backend/apps/data_ingestion/config/config.yaml
ibkr:
  port: 4001  # Change from 4002 to 4001 for TWS
```

---

## Step 3: Test Connection from Windows Host

Before testing from Docker, verify IB Gateway API is accessible:

```powershell
# Test TCP connection
Test-NetConnection -ComputerName 127.0.0.1 -Port 4002
```

Expected output:
```
TcpTestSucceeded : True
```

---

## Step 4: Verify Trade2026 Connection

### Check Connection Status
```bash
# From project root
docker logs trade2026-data-ingestion --tail 30
```

**Success indicators**:
```
INFO - Connected to Valkey
INFO - Connected to QuestDB
INFO - Connecting to host.docker.internal:4002 with clientId 10...
INFO - Connected
INFO - Subscribed to 15 symbols
INFO - IBKR Adapter: CONNECTED
```

**Failure indicators**:
```
ERROR - API connection failed: ConnectionRefusedError
ERROR - API connection failed: TimeoutError
```

### Check Data Flow
```bash
# Verify data is being written to QuestDB
docker exec trade2026-questdb /app/bin/psql -d qdb -c "SELECT symbol, COUNT(*) as ticks, MAX(timestamp) as latest FROM market_data_l1 WHERE timestamp > now() - interval '5 minutes' GROUP BY symbol ORDER BY latest DESC LIMIT 10;"
```

---

## Step 5: Monitor Connection Status

### Via Health Endpoint
```bash
curl http://localhost:8500/health
```

Expected response when connected:
```json
{
  "status": "healthy",
  "ibkr_status": "connected",
  "ibkr_connected_at": "2025-10-23T20:45:30Z",
  "symbols_subscribed": 15,
  "last_tick_received": "2025-10-23T20:50:15Z"
}
```

### Via Website Dashboard
Navigate to: `http://localhost:5173/status`

You'll see:
- **IBKR Connection**: 🟢 Connected / 🔴 Disconnected
- **Last Tick**: timestamp
- **Symbols**: 15 subscribed

---

## Troubleshooting

### Problem: "Connection Refused"
**Cause**: IB Gateway not running or API not enabled

**Fix**:
1. Ensure IB Gateway is running
2. Check API → Settings → Enable ActiveX and Socket Clients is checked
3. Restart IB Gateway after changing settings

### Problem: "TimeoutError" (most common)
**Cause**: API enabled but trusted IPs not configured

**Fix**:
1. Go to API → Settings → Trusted IP Addresses
2. Add `192.168.65.254` and `192.168.65.0/24`
3. Click OK to save
4. Restart data-ingestion service: `docker-compose restart data-ingestion`

### Problem: "API Error 326: Unable to connect"
**Cause**: Too many active API connections

**Fix**:
1. IB allows only 32 simultaneous API connections
2. Close other applications using IBKR API
3. Set unique client_id in config.yaml (default: 10)

### Problem: "Market data not flowing"
**Cause**: Market data subscriptions not active

**Fix**:
1. Check your IBKR account has market data subscriptions
2. For paper trading, market data is delayed 15 minutes by default
3. Verify symbols in config.yaml are valid

---

## Configuration Reference

### Trade2026 IBKR Config
Location: `backend/apps/data_ingestion/config/config.yaml`

```yaml
ibkr:
  host: "host.docker.internal"  # Docker → Host networking
  port: 4002                     # IB Gateway (4001 for TWS)
  client_id: 10                  # Unique client ID
  reconnect_delay_seconds: 5     # Wait before reconnect
  max_reconnect_attempts: 999    # Infinite retries (set high)

  # Alert Configuration
  alert_on_disconnect: true
  alert_methods:
    - email                      # Send email alert
    - ui_notification            # Show on website
    - log                        # Log to console
```

---

## Alerts & Notifications

### Connection Loss Alert
When IBKR connection is lost, you'll receive:

1. **Console Log** (immediate):
   ```
   [ALERT] IBKR Connection Lost at 2025-10-23T21:00:00Z
   [INFO] Attempting reconnection... (attempt 1/999)
   ```

2. **Website Notification** (visible on dashboard):
   - Red banner: "⚠️ IBKR Connection Lost - Reconnecting..."
   - Status indicator changes from 🟢 to 🔴

3. **Health Endpoint** (for monitoring):
   ```json
   {
     "status": "degraded",
     "ibkr_status": "disconnected",
     "last_disconnected_at": "2025-10-23T21:00:00Z",
     "reconnection_attempts": 3
   }
   ```

### Connection Restored Alert
```
[ALERT] IBKR Connection Restored at 2025-10-23T21:05:30Z
[INFO] Resuming market data subscriptions...
```

---

## Production Checklist

Before deploying to production:

- [ ] IB Gateway API enabled
- [ ] Trusted IPs configured (192.168.65.0/24)
- [ ] Socket port verified (4002 for Gateway, 4001 for TWS)
- [ ] Read-Only API disabled (unchecked)
- [ ] Test connection from Docker (`docker logs trade2026-data-ingestion`)
- [ ] Verify data flow to QuestDB
- [ ] Test connection loss scenario (close Gateway, verify alerts)
- [ ] Configure IB Gateway auto-restart on disconnect
- [ ] Set up monitoring alerts (email, Slack, PagerDuty, etc.)

---

## Support

**Issue**: IBKR connection not working after following this guide
**Solution**: Check logs and create GitHub issue with:
1. `docker logs trade2026-data-ingestion --tail 100`
2. IB Gateway version
3. Trading mode (live/paper)
4. OS (Windows/Mac/Linux)

**GitHub Issues**: https://github.com/AlexBocio/trade2026/issues
