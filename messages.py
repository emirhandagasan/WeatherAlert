import config

EMOJI = {
    "thunderstorm": "⛈️",
    "hail": "🧊",
    "snow": "🌨️",
    "rain": "🌧️",
    "wind": "💨",
}

TEXTS = {
    "en": {
        "title": "Weather alert",
        "thunderstorm": "Thunderstorm",
        "hail": "Hail",
        "snow": "Snow",
        "rain": "Rain",
        "wind": "Strong wind",
        "mm": "up to {} mm/h",
        "chance": "{}%",
        "gust": "gusts up to {} km/h",
        "temps": "High {}°C / Low {}°C",
        "nothing": "No weather alerts for today.",
        "months": ["January", "February", "March", "April", "May", "June", "July",
                   "August", "September", "October", "November", "December"],
    },
    "tr": {
        "title": "Hava durumu uyarısı",
        "thunderstorm": "Gök gürültülü fırtına",
        "hail": "Dolu",
        "snow": "Kar",
        "rain": "Yağmur",
        "wind": "Kuvvetli rüzgar",
        "mm": "{} mm/sa'e kadar",
        "chance": "%{}",
        "gust": "{} km/sa'e varan rüzgar",
        "temps": "En yüksek {}°C / En düşük {}°C",
        "nothing": "Bugün için hava uyarısı yok.",
        "months": ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz",
                   "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"],
    },
}


def text(key):
    lang = TEXTS.get(config.LANGUAGE, TEXTS["en"])
    return lang[key]


def hours(alert):
    if alert["start"] == alert["end"]:
        return f"{alert['start']:02d}:00"
    return f"{alert['start']:02d}:00-{alert['end']:02d}:00"


def alert_line(alert):
    line = f"{EMOJI[alert['type']]} {text(alert['type'])} {hours(alert)}"

    details = []
    if alert["type"] in ("rain", "snow", "thunderstorm") and alert["mm"] > 0:
        details.append(text("mm").format(round(alert["mm"], 1)))
        details.append(text("chance").format(alert["chance"]))
    if alert["type"] == "wind":
        details.append(text("gust").format(round(alert["gust"])))

    if details:
        line += " (" + ", ".join(details) + ")"
    return line


def build_message(alerts, high, low, date):
    month = text("months")[date.month - 1]
    title = f"{text('title')} · {config.CITY} · {date.day} {month}"

    if alerts:
        lines = [alert_line(a) for a in alerts]
        priority = "high" if any(a["type"] in ("thunderstorm", "hail", "snow") for a in alerts) else "default"
    else:
        lines = [text("nothing")]
        priority = "low"

    lines.append(text("temps").format(round(high), round(low)))
    return title, "\n".join(lines), priority
