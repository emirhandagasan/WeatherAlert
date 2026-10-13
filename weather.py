import json
import urllib.request

import config

# weather codes from open-meteo (WMO codes), mildest first
THUNDERSTORM = [95, 96, 99]
HAIL = [96, 99]
SNOW = [77, 71, 85, 73, 75, 86]
RAIN = [51, 53, 55, 56, 57, 61, 80, 63, 81, 66, 67, 65, 82]
CODES = {"thunderstorm": THUNDERSTORM, "hail": HAIL, "snow": SNOW, "rain": RAIN}

# order they show up in the message
ORDER = ["thunderstorm", "hail", "snow", "rain", "wind"]


def get_json(url):
    with urllib.request.urlopen(url, timeout=20) as response:
        return json.load(response)


def get_forecast():
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={config.LATITUDE}&longitude={config.LONGITUDE}"
        f"&timezone={config.TIMEZONE}&forecast_days=1"
    )
    forecast = get_json(
        url + "&hourly=weather_code,precipitation,precipitation_probability,wind_gusts_10m"
        "&daily=temperature_2m_max,temperature_2m_min"
    )

    # the other models are a bonus, carry on without them if this fails
    try:
        models = get_json(url + "&hourly=weather_code&models=" + ",".join(config.MODELS))
        forecast["models"] = models["hourly"]
    except Exception as e:
        print("Could not get the other models:", e)
        forecast["models"] = {}

    return forecast


def check_hour(code, rain_mm, rain_chance, gust):
    found = []

    if code in THUNDERSTORM:
        found.append("thunderstorm")
    if code in HAIL:
        found.append("hail")
    if code in SNOW:
        found.append("snow")

    if code in RAIN:
        found.append("rain")
    elif not found and rain_chance >= config.RAIN_CHANCE and rain_mm >= config.RAIN_AMOUNT:
        # code says cloudy but there is still a real chance of rain
        found.append("rain")

    if gust >= config.WIND_LIMIT:
        found.append("wind")

    return found


def check_models(models, i):
    """Rain or snow that enough of the other models agree on."""
    seen = {"rain": [], "snow": []}
    for model in config.MODELS:
        code = (models.get("weather_code_" + model) or [])[i:i + 1]
        if code and code[0] in RAIN + THUNDERSTORM:
            seen["rain"].append(code[0])
        elif code and code[0] in SNOW:
            seen["snow"].append(code[0])

    found = {}
    for t, codes in seen.items():
        if len(codes) >= config.MODEL_AGREE:
            # mildest code, thunderstorms count as plain rain here
            known = [c for c in codes if c in CODES[t]]
            found[t] = min(known, key=CODES[t].index) if known else None
    return found


def find_alerts(forecast, from_hour):
    """Goes through the hours and merges the bad ones into blocks like 16-18."""
    hourly = forecast["hourly"]
    models = forecast.get("models", {})
    alerts = []
    active = {}  # alerts that are still going on

    for i, time in enumerate(hourly["time"]):
        hour = int(time[11:13])  # "2026-09-24T16:00" -> 16
        if hour < from_hour:
            continue

        rain_mm = hourly["precipitation"][i] or 0
        rain_chance = hourly["precipitation_probability"][i] or 0
        gust = hourly["wind_gusts_10m"][i] or 0
        code = hourly["weather_code"][i]
        types = check_hour(code, rain_mm, rain_chance, gust)
        found = {t: code for t in types}

        # main forecast is dry, see what the other models say
        unsure = {}
        if not set(types) & CODES.keys():
            unsure = check_models(models, i)

        # close the ones that stopped (a 1 hour gap is fine)
        for t in list(active):
            if t not in found and t not in unsure and hour - active[t]["end"] > 1:
                alerts.append(active.pop(t))

        for t in list(found) + list(unsure):
            if t not in active:
                active[t] = {"type": t, "start": hour, "end": hour, "code": None, "model_code": None,
                             "unsure": True, "mm": 0, "chance": 0, "gust": 0}
            a = active[t]
            a["end"] = hour
            a["mm"] = max(a["mm"], rain_mm)
            a["chance"] = max(a["chance"], rain_chance)
            a["gust"] = max(a["gust"], gust)

            # keep the worst code of the block, the message is built from it
            key = "code" if t in found else "model_code"
            c = found.get(t, unsure.get(t))
            order = CODES.get(t, [])
            if c in order and (a[key] is None or order.index(c) > order.index(a[key])):
                a[key] = c
            if t in found:
                a["unsure"] = False

    alerts += active.values()

    # blocks that only the other models see
    for a in alerts:
        if a["unsure"]:
            a["code"] = a["model_code"]

    alerts.sort(key=lambda a: (ORDER.index(a["type"]), a["start"]))
    return alerts
