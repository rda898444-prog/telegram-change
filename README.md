Telegram Auto Updater — Setup Guide

Automatically update your Telegram profile (bio, name, and profile picture) using GitHub Actions and Telethon. No server required, completely free.

---

What It Does

This project uses GitHub Actions to run Python scripts on a schedule. It can update your Telegram bio with live time, rotate your first name through a list, and generate a neon-style system monitor image for your profile picture.

---

Prerequisites

You need a GitHub account, a Telegram account, and a way to run Python code (for generating a session string). On Android, you can use Pydroid 3. On desktop, any Python environment works.

---

Step 1: Create a GitHub Repository

Go to GitHub and click the "+" icon, then "New repository". Choose a name like telegram-auto-updater. Set visibility to Private (or Public for unlimited Actions minutes). Check "Add a README file" and click "Create repository".

---

Step 2: Get API ID and API Hash

Visit my.telegram.org. Enter your phone number with country code, then the confirmation code Telegram sends you. Click "API development tools". Fill the form with any app title and short name, set platform to Desktop, and leave URL and description empty. Click "Create application". You will see two values: api_id (a number) and api_hash (a string). Copy both and keep them safe.

---

Step 3: Generate a Session String

Since GitHub cannot use a .session file, you need a StringSession. Install Telethon in your Python environment:

```
pip install telethon
```

Create a new file and paste this code, replacing API_ID and API_HASH with your values:

```python
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

API_ID = 27734869
API_HASH = 'a6868f9bf0a8767f63cac86d954e95b7'

with TelegramClient(StringSession(), API_ID, API_HASH) as client:
    print(client.session.save())
```

Run the script. Enter your phone number and the Telegram confirmation code. If you have two-factor authentication enabled, enter your password. A long string starting with 1BV will be printed. Copy it fully. This string grants full access to your account, so never share it.

---

Step 4: Add GitHub Secrets

In your repository, go to Settings. In the left menu, click "Secrets and variables" then "Actions". Click "New repository secret" and add three secrets:

· Name: API_ID — Value: the number from my.telegram.org
· Name: API_HASH — Value: the string from my.telegram.org
· Name: TELEGRAM_SESSION — Value: the long string from Step 3

---

Step 5: Upload Project Files

Place these files in the root of your repository:

· .github/workflows/update_bio.yml
· py.py (bio script)
· name.py (name rotation script)
· main.py (profile picture generator)
· name.txt (one name per line)
· requirements.txt (Python dependencies)
· background.png (background image for main.py)
· Oxanium.ttf (font for main.py)

Your requirements.txt should contain:

```
telethon
Pillow
psutil
```

Example name.txt:

```
Ki
Ali
Reza
Sara
```

---

Step 6: Test the Workflow

Go to the Actions tab. From the left menu, click "Telegram Auto Updater (All-in-One)". Click "Run workflow" and confirm. After a few seconds, the workflow should turn green. Click the workflow run, then click any step to see logs. If everything works, your bio and name will update automatically.

---

Schedule

The bio script runs every 30 minutes. The name script runs every hour. The profile picture script runs every 3 hours at 07:00, 10:00, 13:00, 16:00, 19:00, and 22:00 Iran time. No scripts run between 00:00 and 06:59 Iran time.

---

Troubleshooting

If you see a FLOOD_WAIT error, Telegram is limiting frequent changes. The script handles it, but if it happens too often, increase the interval in update_bio.yml. If you see AuthKeyUnregistered, your session string is invalid or expired — regenerate it and update the secret. If workflows are stuck in "Queued", you have exceeded the free 2,000 minutes per month — make the repository Public. If you see AttributeError: 'User' object has no attribute 'about', use GetFullUserRequest to fetch the bio instead of me.about.

---

Security

Keep your repository Private, or ensure all sensitive data is stored in Secrets. Never hardcode your session string, API hash, or API ID in your scripts. If you suspect a leak, go to Telegram Settings → Devices and terminate unknown sessions, then delete the app on my.telegram.org and create a new one. Update your GitHub Secrets afterward.

---

GitHub Actions Quota

Private repositories have 2,000 free minutes per month. Public repositories have unlimited minutes. For hobby use, making the repository Public is recommended to avoid quota issues.

---

License

MIT — free to use, modify, and distribute. Built with Telethon and Pillow. If this project helped you, consider giving it a star on GitHub.
