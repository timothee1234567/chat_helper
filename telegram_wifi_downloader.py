"""
Telegram Wi-Fi Downloader
==========================
Watches a specific Telegram bot chat for incoming files and downloads them
automatically, but ONLY while your PC is connected to a specific Wi-Fi
network (so you never burn mobile data / hotspot data).

Any file that arrives while you're off that Wi-Fi is queued and downloaded
the next time you reconnect.

------------------------------------------------------------------
SETUP (one-time)
------------------------------------------------------------------
1. Install dependencies:
       pip install telethon

2. Get your own api_id / api_hash (free, takes 2 minutes):
       - Go to https://my.telegram.org -> log in with your phone number
       - Click "API development tools"
       - Create an app (any name/platform is fine)
       - Copy the "api_id" and "api_hash" values into CONFIG below

3. Fill in CONFIG below:
       - TARGET_SSID: the exact name of your home/office Wi-Fi network
       - BOT_USERNAME: the bot's @username (e.g. "somefilebot")
       - DOWNLOAD_DIR: where files should be saved

4. First run will ask for your phone number + login code (Telegram sends
   it via SMS/app) and, if enabled, your 2FA password. After that it saves
   a session file (telegram_wifi.session) so you won't be asked again.

5. Run it:
       python telegram_wifi_downloader.py

   Leave it running in the background. To run it silently on Windows
   without a console window, use "pythonw.exe telegram_wifi_downloader.py"
   or set it up as a Scheduled Task that runs at logon.
------------------------------------------------------------------
"""

import asyncio
import json
import subprocess
import os
from pathlib import Path

from telethon import TelegramClient, events

# ------------------------------------------------------------------
# CONFIG - edit these values
# ------------------------------------------------------------------
API_ID = 1234567                     # <-- from my.telegram.org
API_HASH = "your_api_hash_here"      # <-- from my.telegram.org
BOT_USERNAME = "somefilebot"         # <-- the bot you download files from (no @)
TARGET_SSID = "MyHomeWiFi"           # <-- exact Wi-Fi network name to allow downloads on
DOWNLOAD_DIR = Path.home() / "Downloads" / "TelegramBotFiles"
CHECK_INTERVAL_SECONDS = 20          # how often to poll Wi-Fi status
QUEUE_FILE = Path(__file__).parent / "download_queue.json"
SESSION_NAME = str(Path(__file__).parent / "telegram_wifi")
# ------------------------------------------------------------------

DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)


def get_current_ssid() -> str | None:
    """Return the SSID of the currently connected Wi-Fi network on Windows, or None."""
    try:
        output = subprocess.check_output(
            ["netsh", "wlan", "show", "interfaces"],
            text=True, stderr=subprocess.DEVNULL
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None

    for line in output.splitlines():
        line = line.strip()
        if line.startswith("SSID") and not line.startswith("BSSID"):
            # line looks like: "SSID                   : MyHomeWiFi"
            parts = line.split(":", 1)
            if len(parts) == 2:
                return parts[1].strip()
    return None


def is_on_target_wifi() -> bool:
    return get_current_ssid() == TARGET_SSID


def load_queue() -> list[int]:
    if QUEUE_FILE.exists():
        try:
            return json.loads(QUEUE_FILE.read_text())
        except json.JSONDecodeError:
            return []
    return []


def save_queue(queue: list[int]) -> None:
    QUEUE_FILE.write_text(json.dumps(queue))


async def main():
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await client.start()
    print("Logged in to Telegram.")

    bot_entity = await client.get_entity(BOT_USERNAME)
    queue = load_queue()

    @client.on(events.NewMessage(from_users=bot_entity))
    async def handler(event):
        if event.message.file:
            queue.append(event.message.id)
            save_queue(queue)
            print(f"Queued message {event.message.id} (file: "
                  f"{event.message.file.name or 'unnamed'})")

    async def wifi_watcher():
        while True:
            if queue and is_on_target_wifi():
                print(f"On '{TARGET_SSID}' - downloading {len(queue)} queued file(s)...")
                still_pending = []
                for msg_id in queue:
                    try:
                        msg = await client.get_messages(bot_entity, ids=msg_id)
                        if msg and msg.file:
                            path = await msg.download_media(file=str(DOWNLOAD_DIR) + os.sep)
                            print(f"  Downloaded: {path}")
                        else:
                            print(f"  Message {msg_id} no longer has a file, skipping.")
                    except Exception as e:
                        print(f"  Failed to download message {msg_id}: {e}")
                        still_pending.append(msg_id)
                queue.clear()
                queue.extend(still_pending)
                save_queue(queue)
            await asyncio.sleep(CHECK_INTERVAL_SECONDS)

    print(f"Watching @{BOT_USERNAME} for files. Will only download while on "
          f"Wi-Fi '{TARGET_SSID}'. Currently connected to: {get_current_ssid()!r}")

    await asyncio.gather(client.run_until_disconnected(), wifi_watcher())


if __name__ == "__main__":
    asyncio.run(main())
