import config

EMOJI = {
    "thunderstorm": "⛈️",
    "hail": "🧊",
    "snow": "🌨️",
    "rain": "🌧️",
    "wind": "💨",
}

# below this chance the line says "possible"
LOW_CHANCE = 50

TEXTS = {
    "en": {
        "title": "Weather alert",
        "update": "Weather update",
        "range": "{what} {start}-{end}",
        "single": "{what} around {start}",
        "maybe": "{} possible",
        "thunderstorm": "thunderstorm",
        "snow": "snow",
        "rain": "rain",
        # WMO weather codes
        "codes": {
            51: "light drizzle",
            53: "moderate drizzle",
            55: "dense drizzle",
            56: "light freezing drizzle",
            57: "dense freezing drizzle",
            61: "light rain",
            63: "moderate rain",
            65: "heavy rain",
            66: "light freezing rain",
            67: "heavy freezing rain",
            71: "light snow",
            73: "moderate snow",
            75: "heavy snow",
            77: "snow grains",
            80: "light rain showers",
            81: "moderate rain showers",
            82: "violent rain showers",
            85: "light snow showers",
            86: "heavy snow showers",
            95: "thunderstorm",
        },
        "hail": {96: "hail", 99: "heavy hail"},
        # gust in km/h and up, Beaufort scale
        "wind": [(103, "violent storm"), (89, "storm"), (62, "gale"), (0, "strong wind")],
        "temps": "High {}°C / Low {}°C",
        "nothing": "No weather alerts for today.",
        "months": ["January", "February", "March", "April", "May", "June", "July",
                   "August", "September", "October", "November", "December"],
    },
    "tr": {
        "title": "Hava durumu uyarısı",
        "update": "Hava durumu güncellemesi",
        "range": "{start}-{end} arası {what}",
        "single": "{start} civarı {what}",
        "maybe": "{} olabilir",
        "thunderstorm": "gök gürültülü sağanak yağış",
        "snow": "kar yağışı",
        "rain": "yağmur",
        # WMO hava kodları
        "codes": {
            51: "hafif çisenti",
            53: "orta kuvvette çisenti",
            55: "yoğun çisenti",
            56: "hafif donan çisenti",
            57: "yoğun donan çisenti",
            61: "hafif yağmur",
            63: "orta kuvvette yağmur",
            65: "kuvvetli yağmur",
            66: "hafif donan yağmur",
            67: "kuvvetli donan yağmur",
            71: "hafif kar yağışı",
            73: "orta kuvvette kar yağışı",
            75: "yoğun kar yağışı",
            77: "kar taneleri",
            80: "hafif sağanak yağış",
            81: "orta kuvvette sağanak yağış",
            82: "şiddetli sağanak yağış",
            85: "hafif kar sağanağı",
            86: "kuvvetli kar sağanağı",
            95: "gök gürültülü sağanak yağış",
        },
        "hail": {96: "dolu", 99: "kuvvetli dolu"},
        # km/sa hamle ve üstü, Bofor ölçeği
        "wind": [(103, "tam fırtına"), (89, "kuvvetli fırtına"), (62, "fırtına"), (0, "kuvvetli rüzgar")],
        "temps": "En yüksek {}°C / En düşük {}°C",
        "nothing": "Bugün için hava uyarısı yok.",
        "months": ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz",
                   "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"],
    },
}


def text(key):
    lang = TEXTS.get(config.LANGUAGE, TEXTS["en"])
    return lang[key]


def describe(alert):
    """The alert in words, like "light rain"."""
    kind = alert["type"]

    if kind == "wind":
        for limit, name in text("wind"):
            if alert["gust"] >= limit:
                return name

    if kind == "hail":
        return text("hail")[alert["code"]]

    # 96 and 99 are thunderstorms too, the hail gets its own line
    if kind == "thunderstorm":
        what = text("thunderstorm")
    else:
        what = text("codes").get(alert["code"], text(kind))

    if alert.get("unsure") or alert["chance"] < LOW_CHANCE:
        what = text("maybe").format(what)
    return what


def alert_line(alert):
    if alert["start"] == alert["end"]:
        template = text("single")
    else:
        template = text("range")

    line = template.format(
        what=describe(alert),
        start=f"{alert['start']:02d}:00",
        end=f"{alert['end']:02d}:00",
    )
    return f"{EMOJI[alert['type']]} {line[0].upper()}{line[1:]}"


def build_message(alerts, high, low, date, is_update=False):
    month = text("months")[date.month - 1]
    name = text("update") if is_update and alerts else text("title")
    title = f"{name} · {config.CITY} · {date.day} {month}"

    if alerts:
        lines = [alert_line(a) for a in alerts]
        priority = "high" if any(a["type"] in ("thunderstorm", "hail", "snow") for a in alerts) else "default"
    else:
        lines = [text("nothing")]
        priority = "low"

    lines.append(text("temps").format(round(high), round(low)))
    return title, "\n".join(lines), priority
