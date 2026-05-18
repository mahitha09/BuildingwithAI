# Quick Reference Card

## HTTP Method Cheat Sheet

```
GET    → read (no body)            → list models, search
POST   → create / action            → send chat, upload file
PUT    → replace whole resource     → update full record
PATCH  → modify part                → change one field
DELETE → remove resource            → delete file
```

## Status Code Categories

```
2xx → success     | 200 OK
4xx → your fault  | 400, 401, 403, 404, 429
5xx → their fault | 500, 502, 503, 504
```

## JSON ↔ Python

```python
import json

body = json.dumps({"a": 1})        # dict  → JSON string
data = json.loads('{"a": 1}')      # JSON  → dict
```

## `requests` Basics

```python
import requests

requests.get(url, params={...}, headers={...}, timeout=30)
requests.post(url, json={...}, headers={...}, timeout=30)

response.status_code        # int
response.headers            # dict-like
response.text               # raw string
response.json()             # parsed dict / list
response.raise_for_status() # raises on 4xx/5xx
```

## Secrets

```bash
# .env file (git-ignored):
#    ANTHROPIC_API_KEY=sk-ant-...
#    OPENAI_API_KEY=sk-...
```

```python
from dotenv import load_dotenv
import os

load_dotenv()
key = os.getenv("ANTHROPIC_API_KEY")
```

## LLM Call Template

```python
import requests, os
from dotenv import load_dotenv

load_dotenv()

url = "https://api.anthropic.com/v1/messages"
headers = {
    "x-api-key": os.getenv("ANTHROPIC_API_KEY"),
    "anthropic-version": "2023-06-01",
    "content-type": "application/json",
}
body = {
    "model": "claude-3-5-sonnet-20241022",
    "max_tokens": 1024,
    "messages": [{"role": "user", "content": "Hello!"}],
}

r = requests.post(url, headers=headers, json=body, timeout=30)
r.raise_for_status()
print(r.json()["content"][0]["text"])
```
