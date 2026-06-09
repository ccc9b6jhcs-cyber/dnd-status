import asyncio
import json
import os
import time
import requests
import websockets

TOKEN = os.environ.get("DISCORD_TOKEN")
if not TOKEN:
    print("Error: DISCORD_TOKEN environment variable not set!")
    exit(1)

STATUS = "dnd"

headers = {"Authorization": TOKEN}

r = requests.get("https://discord.com/api/v10/users/@me", headers=headers)
if r.status_code != 200:
    print("Invalid token!")
    exit()

user = r.json()
print(f"Logged in as {user['username']} ({user['id']})!")

QUOTES = [
    "success starts with showing up",
    "small progress is still progress",
    "dream big work hard stay focused",
    "every day is a new chance to improve",
    "believe in yourself and keep going",
    "great things take time",
    "turn obstacles into opportunities",
    "consistency creates success",
    "your effort today builds your future",
    "keep moving forward no matter how slow",
]

current_index = 0
game_start = int(time.time() * 1000)

def get_activities():
    activities = [
        {
            "type": 4,
            "name": "Custom Status",
            "state": QUOTES[current_index],
            "id": "custom",
            "emoji": None
        },
        {
            "type": 0,
            "name": "Counter-Strike 2",
            "application_id": 1513850875632812114,
            "id": "game",
            "assets": {
                "large_image": "cs2",
                "large_text": "Counter-Strike 2"
            },
            "timestamps": {
                "start": game_start
            }
        }
    ]
    print(f"[DEBUG] Activities payload: {json.dumps(activities, indent=2)}")
    return activities

async def rotate_status(ws):
    global current_index
    while True:
        await asyncio.sleep(3600)
        current_index = (current_index + 1) % len(QUOTES)
        print(f"[ROTATE] Switching to: {QUOTES[current_index]}")
        update = {
            "op": 3,
            "d": {
                "status": STATUS,
                "afk": False,
                "activities": get_activities(),
                "since": 0
            }
        }
        await ws.send(json.dumps(update))

async def discord_gateway():
    uri = "wss://gateway.discord.gg/?v=10&encoding=json"

    try:
        async with websockets.connect(uri, max_size=10 * 1024 * 1024) as ws:
            hello = json.loads(await ws.recv())
            heartbeat_interval = hello["d"]["heartbeat_interval"]
            print(f"[GATEWAY] Connected, heartbeat: {heartbeat_interval}ms")

            async def heartbeat():
                while True:
                    await asyncio.sleep(heartbeat_interval / 1000)
                    await ws.send(json.dumps({"op": 1, "d": None}))

            asyncio.create_task(heartbeat())
            asyncio.create_task(rotate_status(ws))

            identify = {
                "op": 2,
                "d": {
                    "token": TOKEN,
                    "intents": 0,
                    "properties": {
                        "os": "windows",
                        "browser": "chrome",
                        "device": "pc"
                    },
                    "presence": {
                        "status": STATUS,
                        "afk": False,
                        "activities": get_activities(),
                        "since": 0
                    }
                }
            }
            print("[GATEWAY] Sending identify...")
            await ws.send(json.dumps(identify))

            while True:
                try:
                    msg = await ws.recv()
                    data = json.loads(msg)
                    op = data.get("op")
                    t = data.get("t")

                    if op == 11:
                        pass  # heartbeat ack, ignore
                    elif op == 0:
                        print(f"[EVENT] {t}")
                        if t == "READY":
                            print(f"[READY] Session ID: {data['d'].get('session_id')}")
                            print(f"[READY] Presence sent: {json.dumps(data['d'].get('user', {}))}")
                    elif op == 9:
                        print(f"[ERROR] Invalid session: {data}")
                    else:
                        print(f"[GATEWAY] op={op} data={json.dumps(data)[:300]}")

                except Exception as e:
                    print(f"[ERROR] Connection lost: {e}")
                    break

    except Exception as e:
        print(f"[ERROR] Gateway error: {e}")

async def main():
    while True:
        await discord_gateway()
        await asyncio.sleep(5)

asyncio.run(main())
