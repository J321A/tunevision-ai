#!/usr/bin/env python3
"""Test script to demonstrate chat with 3 sample inputs."""

import os
import sys
sys.path.insert(0, 'src')

from dotenv import load_dotenv
load_dotenv()

from chat_agent import create_music_chat_agent
from recommender import load_songs

# Load songs and create agent
songs = load_songs('data/songs.csv')
api_key = os.getenv('OPENAI_API_KEY', '')

if not api_key:
    print("❌ No OpenAI API key found in .env")
    sys.exit(1)

print(f"✅ Using OpenAI API key: {api_key[:20]}...")

agent = create_music_chat_agent(songs, api_key)

# Test 3 chat inputs
test_messages = [
    'I want upbeat pop music for working out',
    'Find me some chill lofi beats please',
    'Need intense rock songs for driving'
]

print('\n===== CHAT WITH AI RECOMMENDATIONS =====\n')
for i, msg in enumerate(test_messages, 1):
    print(f'INPUT {i}: {msg}')
    try:
        result = agent.process_message(msg)
        print(f'AI RESPONSE: {result["response"][:250]}...\n')
        if result['recommendations']:
            print(f'TOP RECOMMENDATIONS: {len(result["recommendations"])} song(s)')
            for j, song_rec in enumerate(result['recommendations'][:2], 1):
                song = song_rec['song']
                print(f'  {j}. {song["title"]} by {song["artist"]} ({song["genre"]}, {song["mood"]})')
    except Exception as e:
        print(f'Error: {str(e)[:200]}')
    print()

print('✅ Chat system demonstration complete!')
