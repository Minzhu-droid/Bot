"""
Quick Setup Wizard - Just run: python setup.py
Asks for your website link and login details and saves to config.json
"""
import json
from pathlib import Path
import getpass

BASE_DIR = Path(__file__).parent
CONFIG_PATH = BASE_DIR / "config.json"

print("="*60)
print("🤖 DASHBOARD BOT - QUICK SETUP")
print("="*60)
print("Just paste your website link and login details.")
print("This will be saved to config.json\n")

login_url = input("1. Website LOGIN link (e.g. https://example.com/login): ").strip()
if not login_url.startswith("http"):
    login_url = "https://" + login_url

dashboard_url = input("2. Dashboard link (after login) [press Enter if same as login]: ").strip()
if dashboard_url and not dashboard_url.startswith("http"):
    dashboard_url = "https://" + dashboard_url

username = input("3. Your Username / Email: ").strip()
password = getpass.getpass("4. Your Password (hidden while typing): ").strip()

print("\n--- Screenshot Times ---")
print("Default is twice a day: 09:00 and 21:00 (9am & 9pm)")
custom = input("Press Enter to keep default, or type times like 08:00,20:00: ").strip()
if custom:
    times = [t.strip() for t in custom.split(",")]
else:
    times = ["09:00", "21:00"]

# Load existing config to keep other settings
if CONFIG_PATH.exists():
    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)
else:
    config = {}

config.update({
    "login_url": login_url,
    "dashboard_url": dashboard_url,
    "username": username,
    "password": password,
    "times": times,
    "headless": True,
    "screenshot_full_page": True,
    "wait_after_login": 5,
    "username_selector": "",
    "password_selector": "",
    "login_button_selector": ""
})

with open(CONFIG_PATH, 'w') as f:
    json.dump(config, f, indent=2)

print("\n" + "="*60)
print("✅ CONFIG SAVED!")
print(f"📁 File: {CONFIG_PATH.absolute()}")
print(f"🔗 Login URL: {login_url}")
print(f"👤 Username: {username}")
print(f"⏰ Times: {', '.join(times)}")
print("="*60)
print("\nNext steps:")
print("  1. Test it: python bot.py --test   (you'll see the browser)")
print("  2. Run once: python bot.py --once")
print("  3. Run daily (twice a day): python bot.py")
print("\nKeep the window open for it to run twice daily!")
print("Tip: Use --debug if login fails to see what's happening")
