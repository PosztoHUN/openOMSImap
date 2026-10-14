import time
from collections import defaultdict
from datetime import datetime

import requests

API_URL = "https://advise-plains-streams-auctions.trycloudflare.com/players"
CHANNEL_ID = "1559944538360123442"
BOT_TOKEN = "MTU1OTk0MTQwNjI2MzM0NTE5Mg.G_demM.gvlU9sfePmRHeB15tSl10JOa4Gdotk3Pv75C28"   # keep this file private, never share it
INTERVAL = 5 * 60

DISCORD_URL = f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages"
alerted = set()


def log(msg):
    print(f"[{datetime.now():%H:%M:%S}] {msg}", flush=True)


def get_players():
    r = requests.get(API_URL, timeout=15)
    r.raise_for_status()
    return r.json()


def send_message(text):
    r = requests.post(
        DISCORD_URL,
        headers={"Authorization": f"Bot {BOT_TOKEN}"},
        json={"content": text},
        timeout=15,
    )
    if not r.ok:
        log(f"Discord error {r.status_code}: {r.text}")
    r.raise_for_status()


def check():
    players = get_players()
    log(f"{len(players)} player(s) online")

    groups = defaultdict(list)
    for p in players:
        line = (p.get("line") or "").strip()
        tour = (p.get("tour") or "").strip()
        if p.get("on_foot") or not line or not tour:
            continue
        groups[(line, tour)].append(p)

    current = set()
    for (line, tour), plist in groups.items():
        if len(plist) >= 2:
            current.add((line, tour))
            if (line, tour) not in alerted:
                names = ", ".join(p["name"] for p in plist)
                send_message(f"⚠️ Same line and tour: line {line}, tour {tour}\nPlayers: {names}")
                log(f"Alert sent: {line} / {tour}")

    alerted.intersection_update(current)
    alerted.update(current)


if __name__ == "__main__":
    log("Bot started")
    try:
        send_message("✅ OMSI watcher started")
    except Exception as e:
        log(f"Startup message failed: {e}")

    while True:
        try:
            check()
        except Exception as e:
            log(f"Error: {e}")
        time.sleep(INTERVAL)