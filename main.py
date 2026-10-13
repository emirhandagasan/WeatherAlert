import sys
from datetime import datetime
from zoneinfo import ZoneInfo

import config
import messages
import notify
import state
import weather


def main():
    dry_run = "--dry-run" in sys.argv    # print instead of sending
    force = "--force" in sys.argv        # send even if the day is fine

    now = datetime.now(ZoneInfo(config.TIMEZONE))

    # at night, look at the day from the morning on and send it then
    from_hour = now.hour
    send_at = None
    if now.hour < config.FIRST_HOUR and not force:
        from_hour = config.FIRST_HOUR
        send_at = now.replace(hour=config.FIRST_HOUR, minute=0, second=0, microsecond=0)

    try:
        forecast = weather.get_forecast()
    except Exception as e:
        print("Could not get the forecast:", e)
        return 1

    alerts = weather.find_alerts(forecast, from_hour=from_hour)

    # only send what wasn't sent before
    today = now.strftime("%Y-%m-%d")
    sent = state.load(today)
    is_update = bool(sent)
    if not force:
        alerts = [a for a in alerts if state.is_new(a, sent)]

    high = forecast["daily"]["temperature_2m_max"][0]
    low = forecast["daily"]["temperature_2m_min"][0]

    if not alerts and not force:
        print("Nothing new to report.")
        return 0

    title, body, priority = messages.build_message(alerts, high, low, now, is_update)

    if dry_run:
        if send_at:
            print("Would be sent at", send_at.strftime("%H:%M"))
        print(f"[{priority}] {title}")
        print(body)
        return 0

    try:
        notify.send(title, body, priority, send_at)
    except Exception as e:
        print("Could not send the notification:", e)
        return 1

    state.remember(alerts, sent)
    state.save(today, sent)

    print("Sent:", title)
    return 0


if __name__ == "__main__":
    sys.exit(main())
