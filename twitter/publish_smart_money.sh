#!/bin/bash
cd /root/.openclaw/workspace/twitter
python3 -c "
import json, sys, os
sys.path.insert(0, '.')
from client import TwitterClient

# Leer thread aprobado
with open('approval_pending.json') as f:
    data = json.load(f)

if data.get('status') == 'approved':
    client = TwitterClient()
    tweets = data['tweets']
    
    print(f'Publicando thread de {len(tweets)} tweets...')
    print(f'Tema: {data.get(\"topic\", \"N/A\")}')
    print()
    
    prev_id = None
    for i, tweet_text in enumerate(tweets, 1):
        result = client.post_tweet(tweet_text, in_reply_to_tweet_id=prev_id)
        if result.get('id'):
            print(f'✅ Tweet {i}/{len(tweets)} publicado: {result[\"id\"]}')
            prev_id = result['id']
        else:
            print(f'❌ Tweet {i} fallido: {result}')
            break
    
    if prev_id:
        print(f'\n🎉 Thread completo: https://twitter.com/yhas1984/status/{prev_id}')
        # Marcar como publicado
        data['published'] = True
        with open('approval_pending.json', 'w') as f:
            json.dump(data, f, indent=2)
    else:
        print('\n⚠️ No se pudo publicar el thread')
else:
    print('Thread no aprobado')
" 2>&1