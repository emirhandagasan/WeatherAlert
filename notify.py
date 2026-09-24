import json
import urllib.request

import config

# ntfy wants priority as a number, 1 is lowest and 5 is urgent
PRIORITY = {"low": 2, "default": 3, "high": 4}


def send(title, body, priority):
    if not config.NTFY_TOPIC:
        raise Exception("NTFY_TOPIC is not set")

    data = {
        "topic": config.NTFY_TOPIC,
        "title": title,
        "message": body,
        "priority": PRIORITY[priority],
        "tags": ["warning"],
    }
    request = urllib.request.Request(
        config.NTFY_SERVER,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    urllib.request.urlopen(request, timeout=20)
