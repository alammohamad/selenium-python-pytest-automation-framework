import os
import requests


def send_slack_message(message):
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")

    if not webhook_url:
        print("Slack notification skipped: SLACK_WEBHOOK_URL is not set.")
        return

    try:
        response = requests.post(
            webhook_url,
            json={"text": message},
            timeout=10
        )

        if response.status_code == 200:
            print("Slack notification sent successfully.")
        else:
            print(
                f"Slack notification failed: "
                f"{response.status_code} - {response.text}"
            )

    except Exception as exc:
        print(f"Slack notification error: {exc}")