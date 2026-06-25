"""
Microsoft Teams integration via Incoming Webhook.

Setup:
  1. In Teams, open the channel where you want notifications.
  2. Click ... > Connectors > Incoming Webhook > Configure.
  3. Name it "PO Justification", copy the webhook URL.
  4. Add TEAMS_WEBHOOK_URL=<url> to your .env file.

Docs: https://learn.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook
"""

import json
import os
import urllib.error
import urllib.request
from typing import Optional


def send_to_teams(
    justification: dict[str, str],
    user_input: str = "",
    webhook_url: Optional[str] = None,
) -> None:
    """
    Post a PO justification card to a Teams channel.
    Raises RuntimeError on network failure, ValueError if webhook is not configured.
    """
    url = webhook_url or os.getenv("TEAMS_WEBHOOK_URL")
    if not url:
        raise ValueError(
            "TEAMS_WEBHOOK_URL is not configured. "
            "Add it to your .env file to enable Teams posting."
        )

    card = {
        "@type": "MessageCard",
        "@context": "https://schema.org/extensions",
        "themeColor": "003087",
        "summary": "PO Justification",
        "sections": [
            {
                "activityTitle": "**PO Justification**",
                "activitySubtitle": user_input[:120] + ("…" if len(user_input) > 120 else ""),
                "facts": [
                    {"name": "What", "value": justification["what"]},
                    {"name": "Why", "value": justification["why"]},
                    {"name": "Why Now", "value": justification["why_now"]},
                    {"name": "Why Good Value", "value": justification["why_good_value"]},
                ],
                "markdown": True,
            }
        ],
    }

    payload = json.dumps(card).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status != 200:
                raise RuntimeError(
                    f"Teams returned HTTP {resp.status}. Check your webhook URL."
                )
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Failed to reach Teams: {exc}") from exc
