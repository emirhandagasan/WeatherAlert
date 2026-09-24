# WeatherAlert

I kept getting caught in the rain, so I wrote this. Every morning at 06:00 (Turkey time, UTC+3) it looks at the day's forecast for Istanbul and sends a push notification to my phone if there is rain, snow, hail, a thunderstorm or strong wind coming, with the hours. If the day looks fine it doesn't send anything.

It runs on GitHub Actions for free, gets the forecast from [Open-Meteo](https://open-meteo.com) and sends the notification with [ntfy](https://ntfy.sh). No API keys, no accounts, plain Python.

What a notification looks like:

```
Weather alert · Istanbul · 24 September
🌧️ Rain 16:00-18:00 (up to 2.4 mm/h, 80%)
💨 Strong wind 14:00-17:00 (gusts up to 65 km/h)
High 24°C / Low 17°C
```

Same thing in Turkish (see below for how to switch):

```
Hava durumu uyarısı · Istanbul · 24 Eylül
🌧️ Yağmur 16:00-18:00 (2.4 mm/sa'e kadar, %80)
💨 Kuvvetli rüzgar 14:00-17:00 (65 km/sa'e varan rüzgar)
En yüksek 24°C / En düşük 17°C
```

## Setting it up

1. Install the ntfy app on your phone and subscribe to a topic. Pick a name nobody would guess, something like `weather-alert-k3j9x2m4`. Anyone who knows the name can send you messages, so treat it like a password.
2. Push this repo to GitHub. Public or private, both work.
3. In the repo go to Settings > Secrets and variables > Actions and add a secret named `NTFY_TOPIC` with your topic name.
4. Go to Actions > Weather alert > Run workflow, tick the "force" box and run it. You should get a notification within a minute.

Done, it runs on its own from now on.

## Turkish messages

Same page as the secret, but the **Variables** tab. Add a variable named `LANGUAGE` with the value `tr`.

## Running it on your computer

```
python main.py --dry-run --force
```

`--dry-run` prints the message instead of sending it, `--force` sends even if there is nothing to report. To actually send from your computer set `NTFY_TOPIC` first:

```
NTFY_TOPIC=your-topic python main.py --force
```

## Changing the location

The defaults are Istanbul. You can either edit the values at the top of `config.py`, or leave the code alone and set environment variables, which is nicer because you don't have to touch the code.

These are the variables:

| Variable | Default | What it is |
| --- | --- | --- |
| `CITY_NAME` | `Istanbul` | Only used in the notification title |
| `LATITUDE` | `41.0082` | Coordinates of the place to check |
| `LONGITUDE` | `28.9784` | |
| `TIMEZONE` | `Europe/Istanbul` | Timezone of that place, in `Region/City` form |
| `LANGUAGE` | `en` | `en` or `tr` |

You can find the coordinates of any place on Google Maps by right clicking on it.

**On GitHub** (this is what matters, since that's where it runs): go to Settings > Secrets and variables > Actions, open the **Variables** tab, click "New repository variable" and add them one by one. For example, for Ankara:

```
CITY_NAME  = Ankara
LATITUDE   = 39.9334
LONGITUDE  = 32.8597
TIMEZONE   = Europe/Istanbul
```

The workflow already passes these to the script, nothing else to change. Variables you don't add just keep their defaults. Don't put `NTFY_TOPIC` here, that one goes under Secrets.

**On your computer**, put them in front of the command:

```
CITY_NAME=Ankara LATITUDE=39.9334 LONGITUDE=32.8597 python main.py --dry-run --force
```

## Changing other things

- Wind and rain limits are in `config.py`.
- The time it runs is the cron line in `.github/workflows/weather-alert.yml`. GitHub cron is in UTC and Turkey is UTC+3 all year (no daylight saving), so `55 2 * * *` means 05:55 Turkey time. It's set 5 minutes early because GitHub usually starts scheduled jobs a few minutes late, so in practice it lands around 06:00. For 07:00 you would write `55 3 * * *`.

## What counts as an alert

- Thunderstorm, hail or snow. These are sent as high priority so they make more noise on the phone.
- Rain, or at least a 60% chance of 0.5 mm/h or more.
- Wind gusts of 60 km/h or more.

Hours that already passed are skipped, so if you run it at noon you only get the afternoon.
