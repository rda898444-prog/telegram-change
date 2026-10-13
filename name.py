import os
import json
import asyncio
from telethon import TelegramClient, functions
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError

API_ID = int(os.environ['API_ID'])
API_HASH = os.environ['API_HASH']
SESSION = os.environ['TELEGRAM_SESSION']

STATE_FILE = 'name_state.json'
NAMES_FILE = 'name.txt'
MAX_LEN = 64  # حداکثر طول first_name در تلگرام


def read_names():
    """خوندن اسم‌ها از فایل، خط به خط"""
    with open(NAMES_FILE, 'r', encoding='utf-8') as f:
        lines = f.read().splitlines()
    return [line.strip() for line in lines if line.strip()]


def read_state():
    """خوندن ایندکس فعلی از فایل state"""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {"index": 0}


def save_state(state):
    """ذخیره ایندکس جدید"""
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


async def main():
    names = read_names()
    if not names:
        print("❌ فایل name.txt خالیه یا پیدا نشد.")
        return

    state = read_state()
    idx = state.get("index", 0) % len(names)
    raw_name = names[idx]

    # بریدن اسم اگه از ۶۴ کاراکتر بلندتره
    new_name = raw_name[:MAX_LEN]

    print(f"📚 تعداد اسم‌ها: {len(names)}")
    print(f"📍 ایندکس فعلی: {idx}")
    print(f"✏️ اسم جدید: {new_name}")
    if len(raw_name) > MAX_LEN:
        print(f"⚠️ اسم اصلی {len(raw_name)} کاراکتر بود، بریده شد.")

    async with TelegramClient(StringSession(SESSION), API_ID, API_HASH) as client:
        me = await client.get_me()
        print(f"✅ لاگین: {me.first_name}")

        if (me.first_name or "") == new_name:
            print("⏭ اسم یکیه، ولی ایندکس رو جلو می‌برم.")
        else:
            try:
                await client(
                    functions.account.UpdateProfileRequest(first_name=new_name)
                )
                print("✅ اسم با موفقیت آپدیت شد.")
            except FloodWaitError as e:
                print(f"⏳ FLOOD_WAIT: {e.seconds} ثانیه")
                return  # ایندکس جلو نمی‌ره
            except Exception as e:
                print(f"❌ خطا: {e}")
                return  # ایندکس جلو نمی‌ره

    # فقط بعد از موفقیت، ایندکس بره جلو
    state["index"] = (idx + 1) % len(names)
    save_state(state)
    print(f"📍 ایندکس بعدی: {state['index']}")


asyncio.run(main())
