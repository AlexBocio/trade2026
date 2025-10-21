#!/bin/bash

echo "=== Nginx Status ==="
docker ps | grep nginx

echo -e "\n=== Recent Errors ==="
docker exec nginx tail -20 /var/log/nginx/error.log 2>/dev/null | grep -v "notice" || echo "No errors found"

echo -e "\n=== Request Stats (last 100) ==="
docker exec nginx tail -100 /var/log/nginx/access.log 2>/dev/null | \
  awk '{print $9}' | sort | uniq -c | sort -rn | head -10 || echo "No access logs yet"

echo -e "\n=== Upstream Health ==="
for service in oms risk gateway live-gateway ptrc auth; do
  response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/api/$service/health 2>/dev/null)
  if [ "$response" = "200" ]; then
    echo "$service: ✅ $response"
  else
    echo "$service: ❌ $response"
  fi
done

echo -e "\n=== Container Stats ==="
docker stats nginx --no-stream
