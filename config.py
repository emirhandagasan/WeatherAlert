import os

# where to check the weather
# "or" instead of a default so an empty env var still falls back
LATITUDE = os.getenv("LATITUDE") or "41.0082"
LONGITUDE = os.getenv("LONGITUDE") or "28.9784"
CITY = os.getenv("CITY_NAME") or "Istanbul"
TIMEZONE = os.getenv("TIMEZONE") or "Europe/Istanbul"

# "en" or "tr"
LANGUAGE = os.getenv("LANGUAGE") or "en"

# ntfy settings, topic comes from a github secret
NTFY_SERVER = os.getenv("NTFY_SERVER") or "https://ntfy.sh"
NTFY_TOPIC = os.getenv("NTFY_TOPIC") or ""

# when does it count as an alert
WIND_LIMIT = 60      # km/h gusts
RAIN_CHANCE = 60     # percent
RAIN_AMOUNT = 0.5    # mm per hour
