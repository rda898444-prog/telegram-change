from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import time
import os
import asyncio

try:
    import psutil
except ImportError:
    psutil = None

try:
    from telethon import TelegramClient
    from telethon.sessions import StringSession
    from telethon.tl.functions.photos import (
        UploadProfilePhotoRequest,
        DeletePhotosRequest,
    )
    from telethon.errors import FloodWaitError
except ImportError:
    TelegramClient = None
    StringSession = None
    UploadProfilePhotoRequest = None
    DeletePhotosRequest = None
    FloodWaitError = None

BASE_DIR = Path(__file__).resolve().parent
IMAGE_PATH = BASE_DIR / "background.png"
FONT_PATH = BASE_DIR / "Oxanium.ttf"
OUTPUT_PATH = BASE_DIR / "profile.png"

TEXT_COLOR = (215, 245, 255, 255)
GLOW_COLOR = (0, 155, 255, 230)
ARC_COLOR = (65, 210, 255, 255)

def check_files():
    if not IMAGE_PATH.exists():
        raise FileNotFoundError(f"background.png not found:\n{IMAGE_PATH}")
    if not FONT_PATH.exists():
        raise FileNotFoundError(f"Oxanium.ttf not found:\n{FONT_PATH}")

def load_font(size):
    return ImageFont.truetype(str(FONT_PATH), size)

def centered_x(draw, text, font_obj, center_x):
    bbox = draw.textbbox((0, 0), text, font=font_obj)
    return center_x - ((bbox[2] - bbox[0]) / 2)

def glow_text(image, position, text, font_obj,
              text_color=TEXT_COLOR, glow_color=GLOW_COLOR, blur=7):
    glow_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_layer)
    glow_draw.text(position, text, font=font_obj, fill=glow_color)
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(blur))
    image.alpha_composite(glow_layer)
    ImageDraw.Draw(image).text(position, text, font=font_obj, fill=text_color)

def get_cpu():
    if psutil is None:
        return None
    try:
        return float(psutil.cpu_percent(interval=0.4))
    except Exception as error:
        print(f"[!] CPU unavailable: {error}")
        return None

def get_ram():
    if psutil is None:
        return None
    try:
        return float(psutil.virtual_memory().percent)
    except Exception as error:
        print(f"[!] RAM unavailable: {error}")
        return None

def get_uptime():
    if psutil is None:
        return None
    try:
        seconds = int(time.time() - psutil.boot_time())
        if seconds < 0:
            return None
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        minutes = (seconds % 3600) // 60
        if days > 0:
            return f"{days}D {hours:02d}H {minutes:02d}M"
        return f"{hours:02d}H {minutes:02d}M"
    except Exception as error:
        print(f"[!] Uptime unavailable: {error}")
        return None

def draw_progress_ring(image, center, radius, percent, width):
    if percent is None:
        return
    percent = max(0, min(100, percent))
    start_angle = -90
    end_angle = start_angle + (360 * percent / 100)
    box = (
        center[0] - radius, center[1] - radius,
        center[0] + radius, center[1] + radius
    )
    glow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.arc(box, start=start_angle, end=end_angle,
           fill=GLOW_COLOR, width=width + 5)
    glow = glow.filter(ImageFilter.GaussianBlur(8))
    image.alpha_composite(glow)
    ImageDraw.Draw(image).arc(
        box, start=start_angle, end=end_angle,
        fill=ARC_COLOR, width=width
    )

def main():
    print("\n" + "=" * 45)
    print("       POWER OF LINUX")
    print("=" * 45 + "\n")

    check_files()

    now = datetime.now(ZoneInfo("Asia/Tehran"))
    time_text = now.strftime("%H:%M")
    date_text = now.strftime("%Y-%m-%d")
    day_text = now.strftime("%A").upper()

    print("Reading system information...")
    cpu = get_cpu()
    ram = get_ram()
    uptime = get_uptime()

    cpu_text = f"{cpu:.0f}%" if cpu is not None else "N/A"
    ram_text = f"{ram:.0f}%" if ram is not None else "N/A"
    uptime_text = uptime if uptime is not None else "N/A"

    print(f"\nTIME   : {time_text}")
    print(f"DATE   : {date_text}")
    print(f"DAY    : {day_text}")
    print(f"\nCPU    : {cpu_text}")
    print(f"RAM    : {ram_text}")
    print(f"UPTIME : {uptime_text}\n")

    print("Loading background...")
    image = Image.open(IMAGE_PATH).convert("RGBA")
    W, H = image.size
    print(f"Resolution: {W}x{H}")
    draw = ImageDraw.Draw(image)

    CLOCK_X, CLOCK_Y = int(W * 0.658), int(H * 0.358)

    time_font = load_font(int(H * 0.043))
    time_x = centered_x(draw, time_text, time_font, CLOCK_X)
    glow_text(image, (time_x, int(CLOCK_Y - H * 0.045)),
              time_text, time_font, blur=10)

    date_font = load_font(int(H * 0.017))
    date_x = centered_x(draw, date_text, date_font, CLOCK_X)
    glow_text(image, (date_x, int(CLOCK_Y + H * 0.015)),
              date_text, date_font, blur=5)

    day_font = load_font(int(H * 0.014))
    day_x = centered_x(draw, day_text, day_font, CLOCK_X)
    glow_text(image, (day_x, int(CLOCK_Y + H * 0.045)),
              day_text, day_font, blur=4)

    CPU_X, CPU_Y = int(W * 0.796), int(H * 0.361)
    CPU_RADIUS = int(W * 0.040)
    draw_progress_ring(image, (CPU_X, CPU_Y), CPU_RADIUS, cpu,
                       width=max(4, int(W * 0.005)))
    cpu_font = load_font(int(H * 0.020))
    cpu_x = centered_x(draw, cpu_text, cpu_font, CPU_X)
    glow_text(image, (cpu_x, int(CPU_Y - H * 0.014)),
              cpu_text, cpu_font, blur=6)

    RAM_X, RAM_Y = int(W * 0.900), int(H * 0.361)
    RAM_RADIUS = int(W * 0.040)
    draw_progress_ring(image, (RAM_X, RAM_Y), RAM_RADIUS, ram,
                       width=max(4, int(W * 0.005)))
    ram_font = load_font(int(H * 0.020))
    ram_x = centered_x(draw, ram_text, ram_font, RAM_X)
    glow_text(image, (ram_x, int(RAM_Y - H * 0.014)),
              ram_text, ram_font, blur=6)

    UPTIME_X, UPTIME_Y = int(W * 0.827), int(H * 0.462)
    uptime_font = load_font(int(H * 0.018))
    uptime_x = centered_x(draw, uptime_text, uptime_font, UPTIME_X)
    glow_text(image, (uptime_x, UPTIME_Y),
              uptime_text, uptime_font, blur=5)

    print("\nSaving profile...")
    image.convert("RGB").save(OUTPUT_PATH, quality=95, optimize=True)
    print(f"\n✓ Profile created successfully!\n✓ {OUTPUT_PATH}\n")

async def upload_profile_to_telegram():
    if TelegramClient is None:
        raise RuntimeError(
            "Telethon is not installed. Install it with: pip install telethon"
        )

    api_id = os.getenv("API_ID", "").strip()
    api_hash = os.getenv("API_HASH", "").strip()
    session = os.getenv("TELEGRAM_SESSION", "").strip()

    missing = [
        name for name, value in (
            ("API_ID", api_id),
            ("API_HASH", api_hash),
            ("TELEGRAM_SESSION", session),
        ) if not value
    ]
    if missing:
        raise RuntimeError(
            "Missing Telegram environment variable(s): " + ", ".join(missing)
        )

    try:
        api_id = int(api_id)
    except ValueError as exc:
        raise RuntimeError("API_ID must be an integer.") from exc

    if not OUTPUT_PATH.exists():
        raise FileNotFoundError(
            f"Generated profile image not found: {OUTPUT_PATH}"
        )

    print("\n" + "=" * 45)
    print("       TELEGRAM UPDATE")
    print("=" * 45 + "\n")
    print("Connecting to Telegram...")

    client = TelegramClient(StringSession(session), api_id, api_hash)

    try:
        await client.connect()

        if not await client.is_user_authorized():
            raise RuntimeError(
                "TELEGRAM_SESSION is not authorized. "
                "Generate a StringSession and save it in GitHub Secrets."
            )

        me = await client.get_me()
        username = (
            f"@{me.username}"
            if getattr(me, "username", None)
            else str(me.id)
        )
        print(f"✓ Connected: {username}")

        print("\nChecking current profile photo...")
        old_photos = await client.get_profile_photos("me", limit=1)
        old_photo = old_photos[0] if old_photos else None

        if old_photo is not None:
            print("✓ Current profile photo found.")
            print("\nDeleting old profile photo...")
            await client(DeletePhotosRequest(id=[old_photo]))
            print("✓ Old profile photo deleted.")
        else:
            print("No current profile photo found.")

        print("\nUploading new profile photo...")
        uploaded = await client.upload_file(str(OUTPUT_PATH))
        await client(UploadProfilePhotoRequest(file=uploaded))
        print("✓ New profile photo uploaded.")

        print("\n" + "=" * 45)
        print(" TELEGRAM PROFILE UPDATED SUCCESSFULLY")
        print("=" * 45)
        print(f"\nAccount: {username}")
        print(f"Image: {OUTPUT_PATH.name}\n")

    except FloodWaitError as error:
        print("\nTelegram FLOOD_WAIT")
        print(f"Wait required: {error.seconds} seconds")
        print("Profile update skipped.")

    finally:
        await client.disconnect()
        print("Telegram disconnected.")

def update_telegram_profile():
    asyncio.run(upload_profile_to_telegram())

if __name__ == "__main__":
    try:
        main()
        update_telegram_profile()
    except KeyboardInterrupt:
        print("\nCancelled.")
    except Exception as error:
        print("\n" + "=" * 45)
        print("ERROR")
        print("=" * 45 + "\n")
        print(error)
        print()
