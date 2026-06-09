#!/usr/bin/env python3
"""
LA Excellence Mentorship Bot — Cloud Setup Assistant
=====================================================
This script uses Claude AI to guide you through deploying all 5 n8n workflows
to a new n8n Cloud account (or any n8n instance) completely automatically.

HOW TO RUN:
  1. Install requirements:
       pip install anthropic
  2. Set your Anthropic API key (get one free at https://console.anthropic.com):
       export ANTHROPIC_API_KEY="sk-ant-..."
  3. Run this script:
       python3 cloud_setup_assistant.py

The assistant will ask you questions and do all the setup work for you.
"""

import os
import sys
import json
import copy
import time
import urllib.request
import urllib.error
from pathlib import Path

# ── Check for anthropic package ──────────────────────────────────────────────
try:
    import anthropic
except ImportError:
    print("\n❌ Missing package: anthropic")
    print("   Run this first:  pip install anthropic")
    print("   Then re-run this script.\n")
    sys.exit(1)

# ── Config ────────────────────────────────────────────────────────────────────
SCRIPT_DIR      = Path(__file__).parent
WORKFLOWS_DIR   = SCRIPT_DIR / "n8n_workflows"
WORKFLOW_FILES  = [
    "01_morning_checkin.json",
    "02_afternoon_nudge.json",
    "03_night_checkin.json",
    "04_capture_replies.json",
    "05_weekly_summary.json",
]
# Activation order: 04 first (webhook listener), then the rest
ACTIVATION_ORDER = [
    "04_capture_replies.json",
    "01_morning_checkin.json",
    "02_afternoon_nudge.json",
    "03_night_checkin.json",
    "05_weekly_summary.json",
]

# Defaults that can be overridden by user
DEFAULTS = {
    "bot_token":  "8711874086:AAG3vXsuGQuHc8VXbL-hiJI7YVGpg71j_AY",
    "sheet_id":   "1w7hg-5sUBVQUr8fx12D0Tkeu1W8yey9JIAGv9vCOsWs",
}

# Allowed node keys for n8n API import
ALLOWED_NODE_KEYS = {
    "parameters", "id", "name", "type", "typeVersion",
    "position", "credentials", "webhookId", "continueOnFail",
    "retryOnFail", "maxTries", "waitBetweenTries",
    "notes", "notesInFlow", "disabled", "color",
}

# ── Helpers ───────────────────────────────────────────────────────────────────

def http(url, method="GET", data=None, headers=None, timeout=20):
    """Simple HTTP helper — returns (status_code, parsed_json)."""
    headers = dict(headers or {})
    body = json.dumps(data).encode() if data else None
    if body:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        try:
            resp = json.loads(e.read())
        except Exception:
            resp = {"message": str(e)}
        return e.code, resp
    except Exception as e:
        return 0, {"error": str(e)}


def strip_workflow(raw: dict) -> dict:
    """Remove non-standard keys before posting to n8n API."""
    wf = {
        "name":        raw.get("name", "Workflow"),
        "nodes":       [],
        "connections": raw.get("connections", {}),
        "settings":    {"executionOrder": "v1"},
    }
    for node in raw.get("nodes", []):
        clean = {k: v for k, v in node.items() if k in ALLOWED_NODE_KEYS}
        wf["nodes"].append(clean)
    return wf


def substitute_creds(wf: dict, gs_cred_id: str, gs_cred_name: str,
                     tg_cred_id: str, tg_cred_name: str) -> dict:
    """Replace credential IDs/names in all nodes with user's actual credentials."""
    wf = copy.deepcopy(wf)
    for node in wf.get("nodes", []):
        creds = node.get("credentials", {})
        if "googleSheetsOAuth2Api" in creds:
            creds["googleSheetsOAuth2Api"] = {"id": gs_cred_id, "name": gs_cred_name}
        if "telegramApi" in creds:
            creds["telegramApi"] = {"id": tg_cred_id, "name": tg_cred_name}
    return wf


def n8n_get(base_url: str, api_key: str, path: str):
    return http(f"{base_url.rstrip('/')}/api/v1{path}",
                headers={"X-N8N-API-KEY": api_key})


def n8n_post(base_url: str, api_key: str, path: str, data: dict):
    return http(f"{base_url.rstrip('/')}/api/v1{path}",
                method="POST", data=data,
                headers={"X-N8N-API-KEY": api_key})


def n8n_delete(base_url: str, api_key: str, path: str):
    return http(f"{base_url.rstrip('/')}/api/v1{path}",
                method="DELETE",
                headers={"X-N8N-API-KEY": api_key})


def print_banner():
    print("\n" + "="*60)
    print("  LA Excellence Mentorship Bot — Cloud Setup Assistant")
    print("  Powered by Claude AI")
    print("="*60 + "\n")


# ── Claude conversation engine ────────────────────────────────────────────────

class SetupAssistant:
    def __init__(self):
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            print("❌ ANTHROPIC_API_KEY environment variable not set.")
            print("   Get a free key at: https://console.anthropic.com")
            print("   Then run:  export ANTHROPIC_API_KEY='sk-ant-...'")
            sys.exit(1)
        self.client    = anthropic.Anthropic(api_key=api_key)
        self.messages  = []          # conversation history
        self.state     = {}          # collected values
        self.n8n_url   = ""
        self.n8n_key   = ""

    # ── Core chat method ──────────────────────────────────────────────────────

    def chat(self, user_input: str) -> str:
        """Send user_input to Claude, get reply."""
        self.messages.append({"role": "user", "content": user_input})
        response = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=self._system_prompt(),
            messages=self.messages,
        )
        reply = response.content[0].text
        self.messages.append({"role": "assistant", "content": reply})
        return reply

    def _system_prompt(self) -> str:
        return """You are a friendly, patient setup assistant helping a non-technical person
set up an n8n automation bot for a student mentorship program (LA Excellence IAS Academy).

Your job:
- Ask for information ONE STEP AT A TIME (never ask multiple things at once)
- Use simple language — no jargon
- Confirm each piece of information before moving to the next step
- When the user gives you something, repeat it back clearly
- If they seem confused, explain with a simple example
- Keep replies SHORT (2-4 lines max)
- Be encouraging and patient

Current collected info:
""" + json.dumps(self.state, indent=2)

    def ask(self, question: str) -> str:
        """Print a Claude question and get user input."""
        reply = self.chat(question)
        print(f"\n🤖  {reply}\n")
        return input("You: ").strip()

    def say(self, message: str):
        """Print an assistant message (no user input needed)."""
        reply = self.chat(message)
        print(f"\n🤖  {reply}\n")

    # ── Setup steps ───────────────────────────────────────────────────────────

    def run(self):
        print_banner()

        print("🤖  Hello! I'm here to set up the LA Excellence mentorship bot for you.")
        print("    I'll ask you a few questions and then do everything automatically.")
        print("    Press Ctrl+C at any time to stop.\n")

        try:
            self._collect_n8n_details()
            self._collect_credential_ids()
            self._deploy_workflows()
            self._activate_workflows()
            self._final_check()
        except KeyboardInterrupt:
            print("\n\n⚠️  Setup cancelled. You can run this script again to continue.")

    # ── Step 1: n8n Cloud details ─────────────────────────────────────────────

    def _collect_n8n_details(self):
        print("─"*50)
        print("STEP 1 OF 3 — Your n8n Cloud Details")
        print("─"*50)

        # n8n URL
        while True:
            url_input = self.ask(
                "First, I need your n8n Cloud URL. "
                "It should look like: https://yourname.app.n8n.cloud\n"
                "Do you have an n8n Cloud account yet? If yes, what is your instance URL? "
                "If no, go to https://n8n.io and sign up for a free trial first, then come back."
            )
            if not url_input:
                continue

            # Normalise URL
            url = url_input.strip().rstrip("/")
            if not url.startswith("http"):
                url = "https://" + url

            # Test connectivity
            print(f"\n   ⏳ Testing connection to {url} ...")
            status, resp = http(f"{url}/healthz", timeout=10)
            if status in (200, 404):
                self.n8n_url = url
                self.state["n8n_url"] = url
                reply = self.chat(f"User confirmed n8n URL: {url}. Acknowledge it and ask for their API key next.")
                print(f"\n🤖  {reply}\n")
                break
            else:
                reply = self.chat(
                    f"I tried connecting to {url} but got: status={status}, response={resp}. "
                    "Tell the user this doesn't seem to be a valid n8n URL and ask them to double-check it."
                )
                print(f"\n🤖  {reply}\n")

        # API key
        while True:
            key_input = input("You: ").strip()
            if not key_input:
                print("🤖  Please enter your API key.\n")
                continue

            # Test the API key
            print("\n   ⏳ Validating API key ...")
            status, resp = n8n_get(self.n8n_url, key_input, "/workflows?limit=5")
            if status == 200:
                self.n8n_key = key_input
                self.state["n8n_api_key"] = "✅ valid (hidden)"
                workflow_count = resp.get("count", 0)
                reply = self.chat(
                    f"API key is valid. Found {workflow_count} existing workflows. "
                    "Tell the user their n8n connection is confirmed and move to Step 2."
                )
                print(f"\n🤖  {reply}\n")
                break
            elif status == 401:
                reply = self.chat(
                    "The API key was rejected (401 Unauthorized). "
                    "Tell the user to check they copied the full key and try again."
                )
                print(f"\n🤖  {reply}\n")
            else:
                reply = self.chat(
                    f"API key test failed with status {status}: {resp}. "
                    "Tell the user something went wrong and ask them to try again."
                )
                print(f"\n🤖  {reply}\n")

    # ── Step 2: Credential IDs ────────────────────────────────────────────────

    def _collect_credential_ids(self):
        print("─"*50)
        print("STEP 2 OF 3 — Credentials")
        print("─"*50)

        # List existing credentials automatically
        print("\n   ⏳ Fetching credentials from your n8n account ...")
        status, resp = n8n_get(self.n8n_url, self.n8n_key, "/credentials")

        gs_cred_id = gs_cred_name = ""
        tg_cred_id = tg_cred_name = ""

        if status == 200:
            creds = resp.get("data", [])
            gs_creds = [c for c in creds if "google" in c.get("type", "").lower()]
            tg_creds = [c for c in creds if "telegram" in c.get("type", "").lower()]

            if gs_creds:
                gs_cred_id   = gs_creds[0]["id"]
                gs_cred_name = gs_creds[0]["name"]
                print(f"   ✅ Found Google Sheets credential: '{gs_cred_name}' (id: {gs_cred_id})")
            if tg_creds:
                tg_cred_id   = tg_creds[0]["id"]
                tg_cred_name = tg_creds[0]["name"]
                print(f"   ✅ Found Telegram credential: '{tg_cred_name}' (id: {tg_cred_id})")

        # Google Sheets credential
        if not gs_cred_id:
            reply = self.chat(
                "No Google Sheets credential found on this n8n account. "
                "Guide the user to create one manually:\n"
                "1. In n8n, go to Credentials → Add credential\n"
                "2. Search for 'Google Sheets OAuth2 API'\n"
                "3. Click 'Sign in with Google' and authorize\n"
                "4. Save it, then come back here and tell me the credential ID "
                "   (they can find it in the URL when they click the credential: /credentials/XXXXXX)\n"
                "Ask them to do this now and give you the credential ID."
            )
            print(f"\n🤖  {reply}\n")
            while True:
                val = input("You (paste Google Sheets credential ID): ").strip()
                if val:
                    gs_cred_id   = val
                    gs_cred_name = "Google Sheets account"
                    self.state["gs_cred_id"] = gs_cred_id
                    reply = self.chat(f"Got Google Sheets credential ID: {gs_cred_id}. Confirm and ask for name if known, else use 'Google Sheets account'.")
                    print(f"\n🤖  {reply}\n")
                    break

        # Telegram credential
        if not tg_cred_id:
            reply = self.chat(
                "No Telegram credential found. "
                "Guide the user to create one:\n"
                "1. In n8n, go to Credentials → Add credential\n"
                "2. Search for 'Telegram API'\n"
                f"3. Paste the bot token: 8711874086:AAG3vXsuGQuHc8VXbL-hiJI7YVGpg71j_AY\n"
                "4. Save it, then give me the credential ID from the URL."
            )
            print(f"\n🤖  {reply}\n")
            while True:
                val = input("You (paste Telegram credential ID): ").strip()
                if val:
                    tg_cred_id   = val
                    tg_cred_name = "Telegram account"
                    self.state["tg_cred_id"] = tg_cred_id
                    reply = self.chat(f"Got Telegram credential ID: {tg_cred_id}. Confirm and say we're ready to import workflows.")
                    print(f"\n🤖  {reply}\n")
                    break

        self.gs_cred_id   = gs_cred_id
        self.gs_cred_name = gs_cred_name
        self.tg_cred_id   = tg_cred_id
        self.tg_cred_name = tg_cred_name
        self.state.update({
            "gs_cred_id": gs_cred_id,
            "gs_cred_name": gs_cred_name,
            "tg_cred_id": tg_cred_id,
            "tg_cred_name": tg_cred_name,
        })

    # ── Step 3: Deploy workflows ──────────────────────────────────────────────

    def _deploy_workflows(self):
        print("─"*50)
        print("STEP 3 OF 3 — Importing Workflows")
        print("─"*50)

        reply = self.chat(
            "Tell the user we're now automatically importing all 5 workflows. "
            "They don't need to do anything — just wait."
        )
        print(f"\n🤖  {reply}\n")

        # First, list existing workflows to avoid duplicates
        print("   ⏳ Checking for existing workflows ...")
        status, resp = n8n_get(self.n8n_url, self.n8n_key, "/workflows?limit=100")
        existing_names = {}
        if status == 200:
            for wf in resp.get("data", []):
                existing_names[wf["name"]] = wf["id"]

        self.deployed_ids = {}  # name → id

        for filename in WORKFLOW_FILES:
            filepath = WORKFLOWS_DIR / filename
            if not filepath.exists():
                print(f"   ❌ File not found: {filepath}")
                continue

            with open(filepath) as f:
                raw = json.load(f)

            wf_name = raw.get("name", filename)
            print(f"\n   📄 Importing: {wf_name}")

            # Strip + substitute credentials
            clean = strip_workflow(raw)
            clean = substitute_creds(
                clean,
                self.gs_cred_id, self.gs_cred_name,
                self.tg_cred_id, self.tg_cred_name,
            )

            # Delete old version if exists
            if wf_name in existing_names:
                old_id = existing_names[wf_name]
                print(f"      ⏳ Removing old version (id: {old_id}) ...")
                del_status, _ = n8n_delete(self.n8n_url, self.n8n_key, f"/workflows/{old_id}")
                if del_status in (200, 204):
                    print(f"      ✅ Old version removed")
                else:
                    print(f"      ⚠️  Could not remove old version — will try to import anyway")

            # Import
            status, resp = n8n_post(self.n8n_url, self.n8n_key, "/workflows", clean)
            if status in (200, 201) and resp.get("id"):
                wf_id = resp["id"]
                self.deployed_ids[filename] = wf_id
                print(f"      ✅ Imported successfully (id: {wf_id})")
            else:
                print(f"      ❌ Import failed: {resp}")
                reply = self.chat(
                    f"Import of '{wf_name}' failed with: {resp}. "
                    "Tell the user there was a problem and ask if they want to continue with the rest."
                )
                print(f"\n🤖  {reply}\n")
                choice = input("Continue? (y/n): ").strip().lower()
                if choice != "y":
                    print("\n⚠️  Setup stopped. Re-run the script to try again.")
                    sys.exit(0)

            time.sleep(0.5)  # be nice to the API

        print(f"\n   ✅ All workflows imported: {len(self.deployed_ids)}/5")

    # ── Activate workflows ────────────────────────────────────────────────────

    def _activate_workflows(self):
        print("\n   ⏳ Activating workflows (04 first, then the rest) ...")

        # Build filename → id map
        name_to_file = {
            "04_capture_replies.json":  "04_capture_replies.json",
            "01_morning_checkin.json":  "01_morning_checkin.json",
            "02_afternoon_nudge.json":  "02_afternoon_nudge.json",
            "03_night_checkin.json":    "03_night_checkin.json",
            "05_weekly_summary.json":   "05_weekly_summary.json",
        }

        activated = []
        failed    = []

        for filename in ACTIVATION_ORDER:
            wf_id = self.deployed_ids.get(filename)
            if not wf_id:
                print(f"   ⚠️  {filename} — no ID (was it imported?), skipping")
                continue

            status, resp = n8n_post(
                self.n8n_url, self.n8n_key,
                f"/workflows/{wf_id}/activate", {}
            )
            if status == 200 and resp.get("active"):
                print(f"   ✅ Activated: {filename} (id: {wf_id})")
                activated.append(filename)
            else:
                print(f"   ❌ Could not activate {filename}: {resp}")
                failed.append(filename)

            time.sleep(0.3)

        self.state["activated"] = activated
        self.state["failed"]    = failed

        if failed:
            reply = self.chat(
                f"Activation succeeded for: {activated}. "
                f"Failed for: {failed}. Common reason: workflow 04 needs HTTPS webhook URL. "
                "n8n Cloud should handle this automatically. "
                "Tell the user which ones failed and suggest going to n8n, opening the workflow, "
                "and toggling it manually."
            )
            print(f"\n🤖  {reply}\n")
        else:
            reply = self.chat(
                "All 5 workflows activated successfully! "
                "Give the user a big congratulation and tell them the bot is now live. "
                "Remind them that messages will go out at 7 AM, 2 PM, and 9:30 PM IST daily."
            )
            print(f"\n🤖  {reply}\n")

    # ── Final verification ────────────────────────────────────────────────────

    def _final_check(self):
        print("─"*50)
        print("FINAL CHECK")
        print("─"*50)

        # Get final workflow list
        status, resp = n8n_get(self.n8n_url, self.n8n_key, "/workflows?limit=20")
        if status == 200:
            print("\n   Your n8n workflows:")
            for wf in resp.get("data", []):
                icon = "✅" if wf.get("active") else "⏸️ "
                print(f"   {icon} {wf['name']} (id: {wf['id']})")

        # Summary
        print("\n" + "="*60)
        print("  SETUP COMPLETE!")
        print("="*60)
        print(f"""
  Bot:        @Irmentor_bot
  n8n:        {self.n8n_url}
  Sheet:      https://docs.google.com/spreadsheets/d/{DEFAULTS['sheet_id']}/edit

  Schedule (IST):
    7:00 AM   — Morning check-in (slots target)
    2:00 PM   — Afternoon motivational nudge
    9:30 PM   — Night check-in (status + hours + productivity)
    Sunday    — Weekly summary report

  ⚠️  REMINDER:
  Make sure your Google Sheet has these columns in Student Registry:
    → Expected Next
    → Session Date
  (Add them if missing — the bot writes session state there)
""")

        reply = self.chat(
            "The setup is complete. Give the user final instructions: "
            "1. Remind them to add 'Expected Next' and 'Session Date' columns to their Student Registry tab "
            "if not already there. "
            "2. Tell them to send a message to @Irmentor_bot to test it right now. "
            "3. The bot won't respond unless Workflow 04 is active. "
            "Be warm and encouraging."
        )
        print(f"🤖  {reply}\n")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    assistant = SetupAssistant()
    assistant.run()
