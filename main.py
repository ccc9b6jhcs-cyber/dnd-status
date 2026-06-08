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

activities = [
    {
        "name": "Counter-Strike 2",
        "type": 0,  # Playing
        "application_id": "730251758586601512",
        "id": "game"
    },
    {
        "name": "Spotify",
        "type": 2,  # Listening
        "id": "spotify",
        "details": "An Eater",
        "state": "Matt Martians",
        "assets": {
            "large_image": "spotify:ab67616d0000b2737a4a3c0e3a6f45f8c46e8b8f",
            "large_text": "Going Normal"
        },
        "party": {
            "id": "spotify:33YkiqLWsxzZdi8Z1AKyIk"
        },
        "sync_id": "33YkiqLWsxzZdi8Z1AKyIk",
        "flags": 48,
        "timestamps": {
            "start": 0,
            "end": 147000  # 2:27 in ms
        }
    }
]

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
                        "activities": activities,
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
