#!/usr/bin/env python3
import json
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import http.client
import src.config

room_code = sys.argv[1]

url = src.config.API_ROOT_URL
params = {"type": "failed_election"}

print(url)

conn = http.client.HTTPConnection("localhost", 8000)
conn.request('POST', f"/api/games/{room_code}/trigger_notification", json.dumps(params))
response = conn.getresponse()

print(response.read())

