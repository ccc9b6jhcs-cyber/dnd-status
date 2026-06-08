import asyncio
import json
import os
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

# Each entry: (emoji_name, emoji_id, animated)
EMOJIS = [
    ("steamhappy",      "1396965935172292670", False),
    ("YUM",             "1451972419697774746", False),
    ("tupu",            "1178280504705949736", True),
    ("MarioStar",       "1488285981072162958", True),
    ("WhatsHappening",  "1395815825654419526", True),
    ("Loading",         "1473061121119355076", True),
    ("Scared",          "1480820710334267402", False),
]

current_index = 0  # starts at steamhappy

def get_activities():
    name, emoji_id, animated = EMOJIS[current_index]
    return [
        {
            "type": 4,
            "name": "Custom Status",
            "state": "",
            "id": "custom",
            "emoji": {
                "name": name,
                "id": emoji_id,
                "animated": animated
            }
        },
        {
            "name": "Counter-Strike 2",
            "type": 0,
            "application_id": "730251758586601512",
            "id": "game"
        }
    ]

async def rotate_status(ws):
    global current_index
    while True:
        await asyncio.sleep(300)  # 5 minutes
        current_index = (current_index + 1) % len(EMOJIS)
        name, _, _ = EMOJIS[current_index]
        print(f"Rotating to: {name}")
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
            await ws.send(json.dumps(identify))

            while True:
                try:
                    msg = await ws.recv()
                    data = json.loads(msg)
                    if data.get("op") == 11:
                        pass
                except Exception as e:
                    print("Connection lost, reconnecting...", e)
                    break

    except Exception as e:
        print("Gateway error:", e)

async def main():
    while True:
        await discord_gateway()
        await asyncio.sleep(5)

asyncio.run(main())
