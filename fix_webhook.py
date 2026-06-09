#!/usr/bin/env python3
"""
Fix script: 
1. Checks n8n workflow nt2Pe4REE11JGxmz
2. Gets ngrok public URL
3. Activates the workflow
4. Sets Telegram webhook to point at n8n
"""

import urllib.request
import urllib.error
import json
import subprocess
import sys

N8N_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0ZWY2MDYwOC0yN2JmLTQ0MjUtODEzNi02MWYxNWRlMGJmZDUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzc0MzYyMTA0LCJleHAiOjE3NzY5MTY4MDB9.rics8_QWSNd82cWv_tWJbC6Kpa41nWv0ZMxIJoJGzHk"
BOT_TOKEN = "8711874086:AAG3vXsuGQuHc8VXbL-hiJI7YVGpg71j_AY"
WORKFLOW_ID = "nt2Pe4REE11JGxmz"
N8N_BASE = "http://localhost:5678"


def request(url, method="GET", data=None, headers=None):
    headers = headers or {}
    body = json.dumps(data).encode() if data else None
    if body:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return json.loads(e.read())
    except Exception as e:
        return {"error": str(e)}


# ── Step 1: Get workflow details ──────────────────────────────────────────────
print("\n── Step 1: Fetching workflow details from n8n ──")
wf = request(
    f"{N8N_BASE}/api/v1/workflows/{WORKFLOW_ID}",
    headers={"X-N8N-API-KEY": N8N_KEY}
)

if "error" in wf or "message" in wf:
    print(f"  ❌ Error: {wf}")
    sys.exit(1)

print(f"  ✅ Workflow: {wf.get('name')}")
print(f"  Active: {wf.get('active')}")

# Find the Telegram Trigger node webhook ID
webhook_id = None
for node in wf.get("nodes", []):
    if node.get("type") == "n8n-nodes-base.telegramTrigger":
        webhook_id = node.get("webhookId")
        print(f"  Telegram Trigger node: {node.get('name')}")
        print(f"  WebhookId: {webhook_id}")
        break

if not webhook_id:
    print("  ❌ No Telegram Trigger node found!")
    sys.exit(1)


# ── Step 2: Get ngrok public URL ──────────────────────────────────────────────
print("\n── Step 2: Getting ngrok public URL ──")
ngrok_resp = request("http://localhost:4040/api/tunnels")

if "tunnels" not in ngrok_resp or len(ngrok_resp["tunnels"]) == 0:
    print("  ❌ ngrok is not running! Starting it...")
    subprocess.Popen(
        ["ngrok", "http", "5678"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    import time; time.sleep(5)
    ngrok_resp = request("http://localhost:4040/api/tunnels")

ngrok_url = None
for t in ngrok_resp.get("tunnels", []):
    if t.get("proto") == "https":
        ngrok_url = t["public_url"]
        break
if not ngrok_url and ngrok_resp.get("tunnels"):
    ngrok_url = ngrok_resp["tunnels"][0]["public_url"]

if not ngrok_url:
    print(f"  ❌ Could not get ngrok URL: {ngrok_resp}")
    sys.exit(1)

print(f"  ✅ ngrok URL: {ngrok_url}")


# ── Step 3: Update n8n WEBHOOK_URL env and check ─────────────────────────────
print("\n── Step 3: Checking n8n WEBHOOK_URL ──")
env_path = "/Users/rameshinampudi/n8n/.n8n/.env"
with open(env_path, "r") as f:
    env_content = f.read()

current_webhook = ""
for line in env_content.splitlines():
    if line.startswith("WEBHOOK_URL="):
        current_webhook = line.split("=", 1)[1]

print(f"  Current WEBHOOK_URL: {current_webhook}")
if ngrok_url not in current_webhook:
    print(f"  ⚠️  WEBHOOK_URL mismatch — updating to {ngrok_url}/")
    new_env = "\n".join(
        f"WEBHOOK_URL={ngrok_url}/" if l.startswith("WEBHOOK_URL=") else l
        for l in env_content.splitlines()
    )
    with open(env_path, "w") as f:
        f.write(new_env)
    print("  ✅ .env updated — NOTE: restart n8n for this to take effect")
else:
    print("  ✅ WEBHOOK_URL already correct")


# ── Step 4: Activate workflow ─────────────────────────────────────────────────
print("\n── Step 4: Activating workflow ──")
if not wf.get("active"):
    activate_resp = request(
        f"{N8N_BASE}/api/v1/workflows/{WORKFLOW_ID}/activate",
        method="POST",
        headers={"X-N8N-API-KEY": N8N_KEY}
    )
    if activate_resp.get("active"):
        print("  ✅ Workflow activated!")
    else:
        print(f"  ❌ Activation failed: {activate_resp}")
else:
    print("  ✅ Workflow already active")


# ── Step 5: Build the n8n webhook URL ────────────────────────────────────────
# n8n webhook path for Telegram trigger: /webhook/<webhookId>
n8n_webhook_url = f"{ngrok_url}/webhook/{webhook_id}"
print(f"\n── Step 5: n8n webhook URL ──")
print(f"  {n8n_webhook_url}")


# ── Step 6: Discover the actual registered webhook path from n8n ──────────────
print("\n── Step 6: Discovering actual registered webhook URL from n8n ──")
# n8n registers the webhook at /webhook/<webhookId>/webhook for Telegram triggers
# Verify by probing both paths
import time

candidate_urls = [
    f"{ngrok_url}/webhook/{webhook_id}",
    f"{ngrok_url}/webhook/{webhook_id}/webhook",
]

actual_webhook_url = None
for url in candidate_urls:
    probe = request(url)
    # 404 = not registered, anything else means n8n is responding
    if isinstance(probe, dict) and "404" not in str(probe.get("message", "")):
        actual_webhook_url = url
        print(f"  ✅ Active webhook path: {url}")
        break
    else:
        print(f"  ✗ Not at: {url}")

if not actual_webhook_url:
    # Fall back to querying current Telegram webhook
    info = request(f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo")
    current = info.get("result", {}).get("url", "")
    if current:
        actual_webhook_url = current
        print(f"  ℹ️  Using existing Telegram webhook: {current}")
    else:
        # Default to the /webhook path
        actual_webhook_url = candidate_urls[1]
        print(f"  ℹ️  Defaulting to: {actual_webhook_url}")

# ── Step 7: Register Telegram webhook ────────────────────────────────────────
print("\n── Step 7: Setting Telegram webhook ──")
time.sleep(2)  # avoid rate limit
tg_set = request(
    f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook",
    method="POST",
    data={
        "url": actual_webhook_url,
        "allowed_updates": ["message", "callback_query"]
    }
)
print(f"  Telegram response: {tg_set}")

# ── Step 8: Verify ────────────────────────────────────────────────────────────
print("\n── Step 8: Verifying Telegram webhook ──")
time.sleep(1)
info = request(f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo")
result = info.get("result", {})
print(f"  Webhook URL    : {result.get('url')}")
print(f"  Pending updates: {result.get('pending_update_count')}")
print(f"  Last error     : {result.get('last_error_message', 'None')}")

if result.get("url") == actual_webhook_url:
    print("\n✅ ALL DONE! Telegram → ngrok → n8n pipeline is live.")
    print(f"   Webhook: {actual_webhook_url}")
    print("   Send a message to @Irmentor_bot and n8n will capture it.")
else:
    print(f"\n❌ Webhook URL mismatch. Set: {actual_webhook_url} | Got: {result.get('url')}")
