#!/usr/bin/env python3
"""Preview or send the deterministic WhatsInMenu message through Twilio.

The command is a dry run unless --send is explicitly supplied. Credentials are
read from environment variables and are never written to the repository.
"""
import argparse
import base64
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from generate_menu import build_daily_payload, format_whatsapp_message

IST = ZoneInfo("Asia/Kolkata")


def send_message(body):
    required = ["TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_WHATSAPP_FROM", "WHATSAPP_TO"]
    missing = [name for name in required if not os.environ.get(name)]
    if missing:
        raise SystemExit("Missing server environment values: " + ", ".join(missing))
    sid = os.environ["TWILIO_ACCOUNT_SID"]
    token = os.environ["TWILIO_AUTH_TOKEN"]
    sender = os.environ["TWILIO_WHATSAPP_FROM"]
    recipient = os.environ["WHATSAPP_TO"]
    data = urllib.parse.urlencode({
        "From": sender if sender.startswith("whatsapp:") else f"whatsapp:{sender}",
        "To": recipient if recipient.startswith("whatsapp:") else f"whatsapp:{recipient}",
        "Body": body,
    }).encode("utf-8")
    request = urllib.request.Request(
        f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json",
        data=data,
        method="POST",
    )
    request.add_header("Authorization", "Basic " + base64.b64encode(f"{sid}:{token}".encode()).decode())
    with urllib.request.urlopen(request, timeout=30) as response:
        print(f"WhatsApp message accepted ({response.status}).")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("date", nargs="?", default=datetime.now(IST).strftime("%Y-%m-%d"))
    parser.add_argument("--send", action="store_true", help="Actually submit the message to Twilio")
    args = parser.parse_args()
    message = format_whatsapp_message(build_daily_payload(args.date))
    if args.send:
        send_message(message)
    else:
        print(message)
        print("\nDry run only. Add --send after server credentials are configured.")


if __name__ == "__main__":
    main()
