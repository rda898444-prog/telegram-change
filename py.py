import os
import asyncio
from datetime import datetime, timezone, timedelta
from telethon import TelegramClient, functions
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError

API_ID = int(os.environ['API_ID'])
API_HASH = os.environ['API_HASH']
SESSION = os.environ['TELEGRAM_SESSION']

async def main():
    async with TelegramClient(StringSession(SESSION), API_ID, API_HASH) as client:
        me = await client.get_me()
        print(f"✅ لاگین: {me.first_name}")
        
        # ساعت به وقت ایران
        iran = timezone(timedelta(hours=3, minutes=30))
        now = datetime.now(iran).strftime("%H:%M")
        
        new_bio = f"#!/bin/bash | bash: bio: not found | {now} 🐧"
        
        if (me.about or "") == new_bio:
            print("بیو تغییری نکرده.")
            return
        
        try:
            await client(functions.account.UpdateProfileRequest(about=new_bio))
            print(f"✅ بیو آپدیت شد: {new_bio}")
        except FloodWaitError as e:
            print(f"⏳ FLOOD_WAIT: {e.seconds} ثانیه")
        except Exception as e:
            print(f"❌ خطا: {e}")

asyncio.run(main())
