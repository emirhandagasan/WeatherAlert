import sys
from datetime import datetime
from zoneinfo import ZoneInfo

import config
import messages
import notify
import weather


def main():
    dry_run = "--dry-run" in sys.argv    # print instead of sending
    force = "--force" in sys.argv        # send even if the day is fine

    now = datetime.now(ZoneInfo(config.TIMEZONE))

    try:
        forecast = weather.get_forecast()
    except Exception as e:
        print("Could not get the forecast:", e)
        return 1

    alerts = weather.find_alerts(forecast, from_hour=now.hour)
    high = forecast["daily"]["temperature_2m_max"][0]
    low = forecast["daily"]["temperature_2m_min"][0]

    if not alerts and not force:
        print("Nothing to report today.")
        return 0

    title, body, priority = messages.build_message(alerts, high, low, now)

    if dry_run:
        print(f"[{priority}] {title}")
        print(body)
        return 0

    try:
        notify.send(title, body, priority)
    except Exception as e:
        print("Could not send the notification:", e)
        return 1

    print("Sent:", title)
    return 0


if __name__ == "__main__":
    sys.exit(main())
