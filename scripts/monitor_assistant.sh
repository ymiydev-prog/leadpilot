#!/bin/bash
# Monitor LeadPilot chat and bot activity

BOT_TOKEN="8278104837:AAF8Lo9Gm-qTaGMPYMQ1hr-9GHw51cU-qXs"
CHAT_ID="1058105434"

echo "=== LeadPilot Monitor $(date) ==="
echo ""

# Check webhook status
echo "📡 Webhook Status:"
curl -s "https://api.telegram.org/bot${BOT_TOKEN}/getWebhookInfo" | python3 -c "import sys,json; d=json.load(sys.stdin); print('URL:', d['result']['url']); print('Pending:', d['result']['pending_update_count'])"

echo ""
echo "📊 API Health:"
curl -s http://localhost:8083/api/plans | python3 -c "import sys,json; d=json.load(sys.stdin); print('Plans OK' if d.get('plans') else 'ERROR')" 2>/dev/null || echo "API Down"

echo ""
echo "💬 Recent Messages (getUpdates):"
curl -s "https://api.telegram.org/bot${BOT_TOKEN}/getUpdates?limit=5" | python3 -c "
import sys,json
d=json.load(sys.stdin)
updates = d.get('result', [])
if updates:
    for u in updates[-3:]:
        msg = u.get('message', {})
        text = msg.get('text', '')
        name = msg.get('from', {}).get('first_name', 'Unknown')
        chat_id = msg.get('chat', {}).get('id', '')
        print(f'  [{chat_id}] {name}: {text[:50]}')
else:
    print('  No recent messages')
" 2>/dev/null

echo ""
echo "=== Done ==="
