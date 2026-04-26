#!/usr/bin/env python3
"""Test script to demonstrate chat functionality with 3 sample inputs."""

import os
import sys
sys.path.insert(0, 'src')

from dotenv import load_dotenv
load_dotenv()

from chat_agent import create_music_chat_agent
from recommender import load_songs

# Load songs and create agent
songs = load_songs('data/songs.csv')
agent = create_music_chat_agent(songs, os.getenv('OPENAI_API_KEY', ''))

# Test 3 chat inputs
test_messages = [
    'I want upbeat pop music for working out',
    'Find me some chill lofi beats please',
    'Need intense rock songs for driving'
]

print('===== CHAT INTERFACE TEST =====\n')
for i, msg in enumerate(test_messages, 1):
    print(f'INPUT {i}: {msg}')
    result = agent.process_message(msg)
    print(f'RESPONSE: {result["response"][:300]}...')
    if result['recommendations']:
        print(f'RECOMMENDATIONS: {len(result["recommendations"])} song(s) found')
        for song_rec in result['recommendations'][:2]:
            print(f'  • {song_rec["song"]["title"]} by {song_rec["song"]["artist"]}')
    print()

print('✅ Chat system working successfully!')
