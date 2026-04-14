#!/usr/bin/env python3
"""Publish LeadPilot thread to Twitter"""
import sys
sys.path.insert(0, '/root/.openclaw/workspace/twitter')
from thread_publisher import TwitterThreadPublisher
import json

# Load thread
with open('/root/.openclaw/workspace/twitter/thread_leadpilot_week1.json') as f:
    thread_data = json.load(f)

tweets = [t['text'] for t in thread_data['tweets']]

print(f"Publishing {len(tweets)} tweets...")

publisher = TwitterThreadPublisher()
result = publisher.post_thread(tweets)

print(f"\nResult: {result}")

# Save published thread
with open('/root/.openclaw/workspace/twitter/published_tweets.json') as f:
    published = json.load(f)
published['last_thread'] = {
    'date': '2026-04-12',
    'topic': 'LeadPilot B2B Lead Generation',
    'tweets': len(tweets),
    'result': result
}
with open('/root/.openclaw/workspace/twitter/published_tweets.json', 'w') as f:
    json.dump(published, f, indent=2)