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
    from telethon.tl.functions.photos import UploadProfilePhotoRequest
    from telethon.errors import FloodWaitError
except ImportError:
    TelegramClient = None
    StringSession = None
    UploadProfilePhotoRequest = None
    FloodWaitError = None


# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

IMAGE_PATH = BASE_DIR / "background.png"
FONT_PATH = BASE_DIR / "Oxanium.ttf"
OUTPUT_PATH = BASE_DIR / "profile.png"


# =========================================================
# COLORS
# =========================================================

TEXT_COLOR = (215, 245, 255, 255)
GLOW_COLOR = (0, 155, 255, 230)
ARC_COLOR = (65, 210, 255, 255)


# =========================================================
# CHECK FILES
# =========================================================

def check_files():
    if not IMAGE_PATH.exists():
        raise FileNotFoundError(
            f"background.png not found:\n{IMAGE_PATH}"
        )

    if not FONT_PATH.exists():
        raise FileNotFoundError(
            f"Oxanium.ttf not found:\n{FONT_PATH}"
        )


# =========================================================
# FONT
# =========================================================

def load_font(size):
    return ImageFont.truetype(
        str(FONT_PATH),
        size
    )


# =========================================================
# CENTER TEXT
# =========================================================

def centered_x(draw, text, font_obj, center_x):

    bbox = draw.textbbox(
        (0, 0),
        text,
        font=font_obj
    )

    text_width = bbox[2] - bbox[0]

    return center_x - (text_width / 2)


# =========================================================
# GLOW TEXT
# =========================================================

def glow_text(
    image,
    position,
    text,
    font_obj,
    text_color=TEXT_COLOR,
    glow_color=GLOW_COLOR,
    blur=7
):

    glow_layer = Image.new(
        "RGBA",
        image.size,
        (0, 0, 0, 0)
    )

    glow_draw = ImageDraw.Draw(
        glow_layer
    )

    glow_draw.text(
        position,
        text,
        font=font_obj,
        fill=glow_color
    )

    glow_layer = glow_layer.filter(
        ImageFilter.GaussianBlur(blur)
    )

    image.alpha_composite(
        glow_layer
    )

    draw = ImageDraw.Draw(image)

    draw.text(
        position,
        text,
        font=font_obj,
        fill=text_color
    )


# =========================================================
# SAFE CPU
# =========================================================

def get_cpu():

    if psutil is None:
        return None

    try:
        value = psutil.cpu_percent(
            interval=0.4
        )

        return float(value)

    except (
        PermissionError,
        OSError
    ) as error:

        print(
            f"[!] CPU unavailable: {error}"
        )

        return None

    except Exception as error:

        print(
            f"[!] CPU error: {error}"
        )

        return None


# =========================================================
# SAFE RAM
# =========================================================

def get_ram():

    if psutil is None:
        return None

    try:

        memory = psutil.virtual_memory()

        return float(
            memory.percent
        )

    except (
        PermissionError,
        OSError
    ) as error:

        print(
            f"[!] RAM unavailable: {error}"
        )

        return None

    except Exception as error:

        print(
            f"[!] RAM error: {error}"
        )

        return None


# =========================================================
# SAFE UPTIME
# =========================================================

def get_uptime():

    if psutil is None:
        return None

    try:

        boot_time = psutil.boot_time()

        seconds = int(
            time.time() - boot_time
        )

        if seconds < 0:
            return None

        days = seconds // 86400

        hours = (
            seconds % 86400
        ) // 3600

        minutes = (
            seconds % 3600
        ) // 60

        if days > 0:

            return (
                f"{days}D "
                f"{hours:02d}H "
                f"{minutes:02d}M"
            )

        return (
            f"{hours:02d}H "
            f"{minutes:02d}M"
        )

    except (
        PermissionError,
        OSError
    ) as error:

        print(
            f"[!] Uptime unavailable: {error}"
        )

        return None

    except Exception as error:

        print(
            f"[!] Uptime error: {error}"
        )

        return None


# =========================================================
# PROGRESS RING
# =========================================================

def draw_progress_ring(
    image,
    center,
    radius,
    percent,
    width
):

    # اگر اطلاعات در دسترس نیست
    # حلقه خالی باقی می‌ماند

    if percent is None:
        return

    percent = max(
        0,
        min(100, percent)
    )

    start_angle = -90

    end_angle = (
        start_angle
        + (360 * percent / 100)
    )

    box = (
        center[0] - radius,
        center[1] - radius,
        center[0] + radius,
        center[1] + radius
    )


    # -------------------------
    # GLOW
    # -------------------------

    glow = Image.new(
        "RGBA",
        image.size,
        (0, 0, 0, 0)
    )

    glow_draw = ImageDraw.Draw(
        glow
    )

    glow_draw.arc(
        box,
        start=start_angle,
        end=end_angle,
        fill=GLOW_COLOR,
        width=width + 5
    )

    glow = glow.filter(
        ImageFilter.GaussianBlur(8)
    )

    image.alpha_composite(glow)


    # -------------------------
    # MAIN ARC
    # -------------------------

    draw = ImageDraw.Draw(image)

    draw.arc(
        box,
        start=start_angle,
        end=end_angle,
        fill=ARC_COLOR,
        width=width
    )


# =========================================================
# MAIN
# =========================================================

def main():

    print()
    print("=" * 45)
    print("       POWER OF LINUX")
    print("=" * 45)
    print()


    # -----------------------------------------------------
    # CHECK PROJECT
    # -----------------------------------------------------

    check_files()


    if psutil is None:

        print(
            "[!] psutil is not installed."
        )

        print(
            "[!] System information "
            "will show N/A."
        )

        print()


    # -----------------------------------------------------
    # TIME  (Iran timezone)
    # -----------------------------------------------------

    now = datetime.now(ZoneInfo("Asia/Tehran"))

    time_text = now.strftime(
        "%H:%M"
    )

    date_text = now.strftime(
        "%Y-%m-%d"
    )

    day_text = now.strftime(
        "%A"
    ).upper()


    # -----------------------------------------------------
    # SYSTEM INFORMATION
    # -----------------------------------------------------

    print(
        "Reading system information..."
    )

    cpu = get_cpu()
    ram = get_ram()
    uptime = get_uptime()


    # -----------------------------------------------------
    # DISPLAY VALUES
    # -----------------------------------------------------

    cpu_text = (
        f"{cpu:.0f}%"
        if cpu is not None
        else "N/A"
    )

    ram_text = (
        f"{ram:.0f}%"
        if ram is not None
        else "N/A"
    )

    uptime_text = (
        uptime
        if uptime is not None
        else "N/A"
    )


    print()
    print(f"TIME   : {time_text}")
    print(f"DATE   : {date_text}")
    print(f"DAY    : {day_text}")
    print()
    print(f"CPU    : {cpu_text}")
    print(f"RAM    : {ram_text}")
    print(f"UPTIME : {uptime_text}")
    print()


    # -----------------------------------------------------
    # OPEN BACKGROUND
    # -----------------------------------------------------

    print(
        "Loading background..."
    )

    image = Image.open(
        IMAGE_PATH
    ).convert("RGBA")

    W, H = image.size

    print(
        f"Resolution: {W}x{H}"
    )

    draw = ImageDraw.Draw(image)


    # =====================================================
    # CLOCK
    # =====================================================

    CLOCK_X = int(
        W * 0.658
    )

    CLOCK_Y = int(
        H * 0.358
    )


    # -----------------------------------------------------
    # TIME
    # -----------------------------------------------------

    time_font = load_font(
        int(H * 0.043)
    )

    time_x = centered_x(
        draw,
        time_text,
        time_font,
        CLOCK_X
    )

    time_y = int(
        CLOCK_Y - H * 0.045
    )

    glow_text(
        image,
        (time_x, time_y),
        time_text,
        time_font,
        blur=10
    )


    # -----------------------------------------------------
    # DATE
    # -----------------------------------------------------

    date_font = load_font(
        int(H * 0.017)
    )

    date_x = centered_x(
        draw,
        date_text,
        date_font,
        CLOCK_X
    )

    date_y = int(
        CLOCK_Y + H * 0.015
    )

    glow_text(
        image,
        (date_x, date_y),
        date_text,
        date_font,
        blur=5
    )


    # -----------------------------------------------------
    # DAY
    # -----------------------------------------------------

    day_font = load_font(
        int(H * 0.014)
    )

    day_x = centered_x(
        draw,
        day_text,
        day_font,
        CLOCK_X
    )

    day_y = int(
        CLOCK_Y + H * 0.045
    )

    glow_text(
        image,
        (day_x, day_y),
        day_text,
        day_font,
        blur=4
    )


    # =====================================================
    # CPU
    # =====================================================

    CPU_X = int(
        W * 0.796
    )

    CPU_Y = int(
        H * 0.361
    )

    CPU_RADIUS = int(
        W * 0.040
    )


    draw_progress_ring(
        image,
        (CPU_X, CPU_Y),
        CPU_RADIUS,
        cpu,
        width=max(
            4,
            int(W * 0.005)
        )
    )


    cpu_font = load_font(
        int(H * 0.020)
    )

    cpu_x = centered_x(
        draw,
        cpu_text,
        cpu_font,
        CPU_X
    )

    cpu_y = int(
        CPU_Y - H * 0.014
    )

    glow_text(
        image,
        (cpu_x, cpu_y),
        cpu_text,
        cpu_font,
        blur=6
    )


    # =====================================================
    # RAM
    # =====================================================

    RAM_X = int(
        W * 0.900
    )

    RAM_Y = int(
        H * 0.361
    )

    RAM_RADIUS = int(
        W * 0.040
    )


    draw_progress_ring(
        image,
        (RAM_X, RAM_Y),
        RAM_RADIUS,
        ram,
        width=max(
            4,
            int(W * 0.005)
        )
    )


    ram_font = load_font(
        int(H * 0.020)
    )

    ram_x = centered_x(
        draw,
        ram_text,
        ram_font,
        RAM_X
    )

    ram_y = int(
        RAM_Y - H * 0.014
    )

    glow_text(
        image,
        (ram_x, ram_y),
        ram_text,
        ram_font,
        blur=6
    )


    # =====================================================
    # UPTIME
    # =====================================================

    UPTIME_X = int(
        W * 0.827
    )

    UPTIME_Y = int(
        H * 0.462
    )


    uptime_font = load_font(
        int(H * 0.018)
    )

    uptime_x = centered_x(
        draw,
        uptime_text,
        uptime_font,
        UPTIME_X
    )

    glow_text(
        image,
        (
            uptime_x,
            UPTIME_Y
        ),
        uptime_text,
        uptime_font,
        blur=5
    )


    # =====================================================
    # SAVE
    # =====================================================

    print()
    print(
        "Saving profile..."
    )

    image.convert(
        "RGB"
    ).save(
        OUTPUT_PATH,
        quality=95,
        optimize=True
    )


    print()
    print(
        "✓ Profile created successfully!"
    )

    print(
        f"✓ {OUTPUT_PATH}"
    )

    print()


# =========================================================
# TELEGRAM PROFILE UPLOAD
# =========================================================

async def upload_profile_to_telegram():
    """Upload OUTPUT_PATH as the personal Telegram account profile photo.

    Required environment variables (GitHub Secrets):
      API_ID
      API_HASH
      TELEGRAM_SESSION
    """

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
        raise FileNotFoundError(f"Generated profile image not found: {OUTPUT_PATH}")

    print("Connecting to Telegram...")

    client = TelegramClient(StringSession(session), api_id, api_hash)

    try:
        await client.connect()

        if not await client.is_user_authorized():
            raise RuntimeError(
                "TELEGRAM_SESSION is not authorized. Generate a StringSession once "
                "and save it in GitHub Secrets."
            )

        uploaded = await client.upload_file(str(OUTPUT_PATH))
        await client(UploadProfilePhotoRequest(file=uploaded))

        me = await client.get_me()
        username = f"@{me.username}" if getattr(me, "username", None) else str(me.id)
        print(f"✓ Telegram profile photo updated: {username}")

    except FloodWaitError as e:
        print(f"⏳ FLOOD_WAIT: {e.seconds} seconds — skipping upload.")

    finally:
        await client.disconnect()


def update_telegram_profile():
    asyncio.run(upload_profile_to_telegram())


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    try:

        main()
        update_telegram_profile()

    except KeyboardInterrupt:

        print(
            "\nCancelled."
        )

    except Exception as error:

        print()
        print(
            "ERROR:"
        )

        print(error)