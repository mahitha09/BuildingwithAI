# Making Your First LLM API Call — Conceptual Notes

## What is an LLM?

A Large Language Model (LLM) is a neural network trained on massive text datasets that can understand and generate human language. When you make an "LLM call," you're sending a text prompt to this model and receiving a generated text response back.

---

## The Anatomy of an LLM API Call

An LLM API call follows a simple request-response pattern over HTTP:

```
Your Application  →  HTTP POST Request  →  LLM Provider API  →  HTTP Response  →  Your Application
```

### Core Components

| Component | Description |
|-----------|-------------|
| **Endpoint** | The URL you send your request to (e.g., `https://api.openai.com/v1/chat/completions`) |
| **API Key** | Your authentication credential — proves you have access |
| **Model** | Which LLM you want to use (e.g., `gpt-4`, `claude-sonnet`, `llama-3`) |
| **Prompt / Messages** | The input text you send to the model |
| **Response** | The generated text the model returns |

---

## Step-by-Step: What Happens During Your First Call

### Step 1: Obtain an API Key

Before making any call, you need credentials from your LLM provider. This key is typically:
- Generated from the provider's dashboard/console
- A long alphanumeric string (e.g., `sk-abc123...xyz`)
- Treated as a secret — never hardcode it in source code or commit it to version control

### Environment Variables & `.env` Files

An **environment variable** is a `key=value` pair set on your computer (or server), readable from any program. Python reads them via `os.getenv`:

```python
import os

api_key = os.getenv("ANTHROPIC_API_KEY")
```

You could set them in your shell every time:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

But typing that for every project is annoying. The standard pattern is a `.env` file at the project root:

**.env** *(this file is git-ignored — never committed)*

```
ANTHROPIC_API_KEY=sk-ant-api03-abc123...
OPENAI_API_KEY=sk-...
```

**.gitignore**

```
.env
```

Then load it in Python with `python-dotenv`:

```bash
pip install python-dotenv
```

```python
from dotenv import load_dotenv
import os

load_dotenv()                                  # reads .env into the environment
api_key = os.getenv("ANTHROPIC_API_KEY")       # now this works
```

That's the whole pattern. Used in essentially every Python AI project.


### Step 2: Construct the Request

An LLM API request is an HTTP POST with a JSON body. The minimum required fields are:

JSON

```json
{
  "model": "gpt-4",
  "messages": [
    {
      "role": "user",
      "content": "What is the capital of France?"
    }
  ]
}
```

Python

```Python
{
    "model": "gpt-4",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is HTTP?"},
    ],
    "temperature": 0.7,
    "stream": False,
}
```
Notice the differences : true → True, false → False, null → None.

**Key concepts in the request:**

- **`model`** — Specifies which model processes your request. Different models have different capabilities, speeds, and costs.
- **`messages`** — An array of message objects representing the conversation. Each message has:
  - `role`: Who is speaking — `system`, `user`, or `assistant`
  - `content`: The actual text of the message

**Message Roles Explained:**

| Role | Purpose |
|------|---------|
| `system` | Sets the behavior/personality of the model. Processed first, acts as persistent instructions. |
| `user` | Your input — the question or task you want the model to handle. |
| `assistant` | The model's previous responses (used for multi-turn conversations). |

### Step 3: Set HTTP Headers

```
Authorization: Bearer sk-your-api-key-here
Content-Type: application/json
```

The `Authorization` header carries your API key. The `Content-Type` tells the server you're sending JSON.

### Step 4: Calling APIs in Python — the requests Library

### Why `requests`?

Python's standard library has `urllib`, but no one uses it for HTTP — it's painful. Everyone uses `requests`, the de-facto standard:

```bash
pip install requests
```

`requests` makes HTTP calls feel like function calls. One line per request.

---

### A Simple GET — Hello, Internet

Let's start with the simplest thing — a public API that doesn't require auth. The free [httpbin.org](https://httpbin.org) echoes whatever you send it, useful for learning.

```python
import requests

response = requests.get("https://httpbin.org/get")

print(response.status_code)    # 200
print(response.headers)        # {'Content-Type': 'application/json', ...}
print(response.text)           # raw JSON string
print(response.json())         # parsed into a Python dict
```

Read it carefully. Four things you almost always inspect on a response:

| Attribute | What it gives you |
|-----------|-------------------|
| `response.status_code` | The HTTP status code (200, 429, 500, ...) |
| `response.headers` | Response headers (a dict-like object) |
| `response.text` | The raw body as a string |
| `response.json()` | The body parsed as JSON (calls `json.loads` for you) |

---

### POST With a JSON Body

For LLM calls, you send POST requests with JSON bodies:

```python
import requests

response = requests.post(
    "https://httpbin.org/post",
    json={"hello": "world", "n": 42},   # ← `requests` JSON-serializes this for you
    headers={"X-Custom": "demo"},        # ← any extra headers
)

print(response.status_code)              # 200
print(response.json())
# {
#   "args": {},
#   "data": '{"hello": "world", "n": 42}',
#   "headers": {"X-Custom": "demo", "Content-Type": "application/json", ...},
#   ...
# }
```

The magic: passing `json=...` does three things at once:

1. Calls `json.dumps(...)` on your dict.
2. Sets the body to the resulting string.
3. Adds the header `Content-Type: application/json`.

That's why we love `requests`.

---

### Query Parameters — `params=`

For GET calls that need parameters in the URL query string, use `params=`:

```python
response = requests.get(
    "https://httpbin.org/get",
    params={"q": "agents", "limit": 10},
)

print(response.url)
# https://httpbin.org/get?q=agents&limit=10
```

`requests` does the URL-encoding for you (handles spaces, special characters, etc.).

---

### Timeouts — Always Set Them

Here's a thing junior code always forgets: `requests` will wait **forever** by default if the server stops responding. In production this means a stuck process. Always pass `timeout=`:

```python
response = requests.get("https://httpbin.org/delay/2", timeout=5)  # 5 sec max
```

If the server doesn't respond in time, you get a `requests.exceptions.Timeout` exception. We'll cover handling that properly in 19.3.

---

### A Tiny Utility Function — Setting the Pattern

For LLM work, you'll write the same shape of call over and over:

```python
import requests

def post_json(url: str, body: dict, headers: dict | None = None, timeout: int = 30) -> dict:
    response = requests.post(url, json=body, headers=headers or {}, timeout=timeout)
    response.raise_for_status()         # turns 4xx/5xx into exceptions
    return response.json()
```

`response.raise_for_status()` is a friend — it raises an exception on 4xx/5xx so you don't silently process a 401 as if it were valid.

We'll grow this tiny function into a full `LLMClient` class over the next two sessions. This is the seed of `v2_oop/llm_client.py`.

---

> 💡 **Key Idea:** `requests.get(url)` and `requests.post(url, json=body, headers=...)` cover ~90% of what you'll ever need. Always set a timeout. Always check `status_code` (or call `raise_for_status()`).

### Step 4: Send the Request

Your application sends the HTTP POST to the provider's endpoint. At this point:

1. The request hits the provider's API gateway
2. Authentication is validated (is your key valid? do you have quota?)
3. The request is routed to the specified model
4. The model processes your prompt through its neural network
5. Tokens are generated one by one (auto-regressively)
6. The complete response is assembled and returned

### Step 5: Receive and Parse the Response

A typical response looks like:

```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1716000000,
  "model": "gpt-4",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "The capital of France is Paris."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 14,
    "completion_tokens": 8,
    "total_tokens": 22
  }
}
```

**Key fields in the response:**

| Field | Meaning |
|-------|---------|
| `choices[0].message.content` | The model's actual text response |
| `finish_reason` | Why the model stopped: `stop` (natural end), `length` (hit token limit), `tool_calls` (wants to use a tool) |
| `usage.prompt_tokens` | How many tokens your input consumed |
| `usage.completion_tokens` | How many tokens the model generated |
| `usage.total_tokens` | Total tokens used (this is what you're billed for) |

---

## Key Concepts to Understand

### Tokens

LLMs don't process words — they process **tokens**. A token is roughly 3-4 characters or about 0.75 words in English.

- `"Hello"` = 1 token
- `"ChatGPT is great"` = 4 tokens
- Code and non-English text typically use more tokens per word

Tokens matter because:
- You're billed per token
- Models have a maximum context window (e.g., 4K, 8K, 128K tokens)
- Your prompt + response must fit within this window

### Temperature

Controls randomness in the output:
- `temperature: 0` — Deterministic, always picks the most likely next token
- `temperature: 0.7` — Balanced creativity (good default)
- `temperature: 1.0+` — More random, creative, but potentially less coherent

### Streaming vs Non-Streaming

- **Non-streaming** (default): You wait for the entire response, then receive it all at once
- **Streaming** (`stream: true`): Tokens are sent back as they're generated via Server-Sent Events (SSE), giving a "typing" effect

### Context Window

The model can only "see" what's in the messages array. It has no memory between separate API calls. If you want a multi-turn conversation, you must include the full conversation history in each request.

---

## Common Optional Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `temperature` | float (0-2) | Controls randomness. Lower = more focused. |
| `max_tokens` | integer | Maximum tokens to generate in the response. |
| `top_p` | float (0-1) | Nucleus sampling — alternative to temperature. |
| `stop` | string/array | Sequences where the model should stop generating. |
| `stream` | boolean | Whether to stream partial responses. |
| `n` | integer | Number of response alternatives to generate. |

---

## Error Handling

Common HTTP status codes you'll encounter:

| Code | Meaning | Action |
|------|---------|--------|
| `200` | Success | Parse the response |
| `401` | Invalid API key | Check your credentials |
| `429` | Rate limited | Wait and retry (use exponential backoff) |
| `500` | Server error | Retry after a short delay |
| `503` | Service overloaded | Retry with backoff |

---

## Cost Awareness

Every API call costs money based on token usage. Before building:
- Estimate your average prompt size and expected response length
- Check the provider's pricing page for per-token costs
- Set usage limits/budgets in your provider dashboard
- Use cheaper models for simple tasks, expensive models only where quality matters

---

## Security Checklist for Your First Call

- [ ] API key stored in environment variable or secrets manager, not in code
- [ ] API key not committed to version control (add to `.gitignore`)
- [ ] HTTPS used for all API calls (never HTTP)
- [ ] User input sanitized before including in prompts (prevent prompt injection)
- [ ] Response validated before using in your application

---

## What's Next After Your First Call?

1. **Multi-turn conversations** — Include conversation history in messages array
2. **System prompts** — Shape model behavior with system messages
3. **Function/Tool calling** — Let the model invoke your code
4. **RAG (Retrieval-Augmented Generation)** — Feed relevant documents into context
5. **Fine-tuning** — Train the model on your specific data
6. **Prompt engineering** — Optimize prompts for better, more consistent outputs


