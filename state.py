import json

import config


def load(today):
    """Hours already sent today, per alert type."""
    try:
        with open(config.STATE_FILE) as f:
            state = json.load(f)
    except (OSError, ValueError):
        return {}
    if state.get("date") != today:
        return {}  # new day, start over
    return state.get("sent", {})


def save(today, sent):
    with open(config.STATE_FILE, "w") as f:
        json.dump({"date": today, "sent": sent}, f)


def is_new(alert, sent):
    # new if some hour isn't next to one we already sent
    known = sent.get(alert["type"], [])
    for hour in range(alert["start"], alert["end"] + 1):
        if not any(abs(hour - h) <= 1 for h in known):
            return True
    return False


def remember(alerts, sent):
    for a in alerts:
        hours = set(sent.get(a["type"], []))
        hours.update(range(a["start"], a["end"] + 1))
        sent[a["type"]] = sorted(hours)
