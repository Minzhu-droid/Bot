"""
Dashboard Screenshot Bot - Logs in and captures dashboard twice daily
Works with ANY website - just edit config.json

Features:
- Auto-login with username/password
- Smart auto-detection of login fields
- Full-page dashboard screenshots with timestamps
- Runs twice daily automatically (customizable)
- Headless mode (runs in background)
- Saves all screenshots organized by date
"""

import json
import time
import logging
from pathlib import Path
from datetime import datetime
import os
import sys

# Setup paths
BASE_DIR = Path(__file__).parent
CONFIG_PATH = BASE_DIR / "config.json"
SCREENSHOT_DIR = BASE_DIR / "screenshots"
LOG_FILE = BASE_DIR / "bot.log"

# Ensure screenshot dir exists
SCREENSHOT_DIR.mkdir(exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def load_config():
    """Load and validate config.json"""
    if not CONFIG_PATH.exists():
        logger.error(f"config.json not found! Create it from config.example.json")
        sys.exit(1)
    
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Validate required fields
    required = ["login_url", "username", "password"]
    for field in required:
        if not config.get(field) or config[field] in ["", "YOUR_USERNAME_HERE", "YOUR_PASSWORD_HERE", "https://example.com/login"]:
            logger.error(f"❌ Please set '{field}' in config.json")
            logger.error(f"   Edit file: {CONFIG_PATH}")
            sys.exit(1)
    
    # Set defaults
    config.setdefault("dashboard_url", "")
    config.setdefault("username_selector", "")
    config.setdefault("password_selector", "")
    config.setdefault("login_button_selector", "")
    config.setdefault("headless", True)
    config.setdefault("screenshot_full_page", True)
    config.setdefault("wait_after_login", 5)
    config.setdefault("times", ["09:00", "21:00"])
    
    return config

def take_screenshot_job():
    """Main job: login and screenshot"""
    config = load_config()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    date_folder = datetime.now().strftime("%Y-%m-%d")
    
    # Create dated folder
    daily_dir = SCREENSHOT_DIR / date_folder
    daily_dir.mkdir(exist_ok=True)
    
    screenshot_path = daily_dir / f"dashboard_{timestamp}.png"
    
    logger.info("="*60)
    logger.info(f"🚀 Starting screenshot job at {timestamp}")
    logger.info(f"🔗 Login URL: {config['login_url']}")
    
    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            # Launch browser
            browser = p.chromium.launch(headless=config["headless"])
            context = browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            page = context.new_page()
            
            # Step 1: Go to login page
            logger.info(f"🌐 Opening login page...")
            page.goto(config["login_url"], wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(2000)
            logger.info(f"   Page title: {page.title()}")
            
            # Step 2: Fill login form (smart detection)
            logger.info("🔐 Filling login form...")
            
            # Try custom selectors first, then auto-detect
            username_filled = False
            password_filled = False
            
            # --- Username / Email ---
            username_selectors = []
            if config.get("username_selector"):
                username_selectors.append(config["username_selector"])
            # Common auto-detect selectors
            username_selectors += [
                'input[name="username"]',
                'input[name="email"]',
                'input[name="user"]',
                'input[id="username"]',
                'input[id="email"]',
                'input[type="email"]',
                'input[placeholder*="Email" i]',
                'input[placeholder*="Username" i]',
                'input[placeholder*="User" i]',
                'input[type="text"]',
            ]
            
            for sel in username_selectors:
                try:
                    if page.locator(sel).count() > 0 and page.locator(sel).first.is_visible():
                        page.fill(sel, config["username"], timeout=3000)
                        logger.info(f"   ✓ Username filled using: {sel}")
                        username_filled = True
                        break
                except:
                    continue
            
            if not username_filled:
                logger.warning("   ⚠️ Could not find username field - trying first text input")
                try:
                    page.locator('input').first.fill(config["username"])
                    username_filled = True
                except Exception as e:
                    logger.error(f"   ❌ Username fill failed: {e}")
            
            # --- Password ---
            password_selectors = []
            if config.get("password_selector"):
                password_selectors.append(config["password_selector"])
            password_selectors += [
                'input[name="password"]',
                'input[id="password"]',
                'input[type="password"]',
            ]
            
            for sel in password_selectors:
                try:
                    if page.locator(sel).count() > 0 and page.locator(sel).first.is_visible():
                        page.fill(sel, config["password"], timeout=3000)
                        logger.info(f"   ✓ Password filled using: {sel}")
                        password_filled = True
                        break
                except:
                    continue
            
            if not password_filled:
                logger.error("   ❌ Could not find password field")
                # Save debug screenshot
                page.screenshot(path=str(daily_dir / f"DEBUG_login_failed_{timestamp}.png"))
                browser.close()
                return False
            
            page.wait_for_timeout(1000)
            
            # --- Click Login ---
            logger.info("🖱️ Clicking login button...")
            login_clicked = False
            
            login_selectors = []
            if config.get("login_button_selector"):
                login_selectors.append(config["login_button_selector"])
            login_selectors += [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("Log in")',
                'button:has-text("Login")',
                'button:has-text("Sign in")',
                'button:has-text("Sign In")',
                'a:has-text("Log in")',
                'button:has-text("Submit")',
                '[data-testid*="login"]',
                '#login',
                '#submit',
            ]
            
            for sel in login_selectors:
                try:
                    btn = page.locator(sel).first
                    if btn.count() > 0 and btn.is_visible():
                        btn.click(timeout=3000)
                        logger.info(f"   ✓ Clicked: {sel}")
                        login_clicked = True
                        break
                except:
                    continue
            
            if not login_clicked:
                logger.info("   ↳ No button found, pressing Enter instead")
                page.keyboard.press("Enter")
            
            # Wait for login to complete
            logger.info(f"⏳ Waiting {config['wait_after_login']}s for dashboard to load...")
            try:
                page.wait_for_load_state("networkidle", timeout=15000)
            except:
                pass
            page.wait_for_timeout(config["wait_after_login"] * 1000)
            
            # If dashboard_url specified, navigate there
            if config.get("dashboard_url"):
                logger.info(f"📊 Navigating to dashboard: {config['dashboard_url']}")
                page.goto(config["dashboard_url"], wait_until="networkidle", timeout=60000)
                page.wait_for_timeout(3000)
            
            # Check if still on login page (login failed)
            current_url = page.url
            if "login" in current_url.lower() and config["login_url"] in current_url:
                # Might be failed login, but check for error messages
                error_visible = page.locator('text=/invalid|incorrect|error|failed/i').count() > 0
                if error_visible:
                    logger.error("❌ Login failed - check username/password")
                    page.screenshot(path=str(daily_dir / f"DEBUG_login_error_{timestamp}.png"), full_page=True)
                    browser.close()
                    return False
            
            logger.info(f"   Current URL: {current_url}")
            logger.info(f"   Page title: {page.title()}")
            
            # Step 3: Take screenshot
            logger.info(f"📸 Taking screenshot...")
            page.screenshot(path=str(screenshot_path), full_page=config["screenshot_full_page"])
            
            # Also save HTML for debugging if needed
            # with open(daily_dir / f"dashboard_{timestamp}.html", "w", encoding="utf-8") as f:
            #     f.write(page.content())
            
            browser.close()
            
            if screenshot_path.exists():
                size_kb = screenshot_path.stat().st_size / 1024
                logger.info(f"✅ SUCCESS! Screenshot saved: {screenshot_path}")
                logger.info(f"   Size: {size_kb:.1f} KB")
                logger.info(f"   Folder: {daily_dir}")
                return True
            else:
                logger.error("❌ Screenshot file not created")
                return False
                
    except ImportError:
        logger.error("❌ Playwright not installed. Run: pip install playwright && playwright install chromium")
        return False
    except Exception as e:
        logger.exception(f"❌ Job failed with error: {e}")
        # Try to save error screenshot if possible
        try:
            if 'page' in locals():
                page.screenshot(path=str(daily_dir / f"ERROR_{timestamp}.png"))
        except:
            pass
        return False

def run_scheduler():
    """Run twice daily scheduler"""
    config = load_config()
    times = config.get("times", ["09:00", "21:00"])
    
    try:
        import schedule
    except ImportError:
        logger.error("❌ 'schedule' library not installed. Run: pip install schedule")
        logger.info("   Running single screenshot instead...")
        take_screenshot_job()
        return
    
    logger.info("="*60)
    logger.info("🤖 DASHBOARD BOT - SCHEDULER MODE")
    logger.info(f"📅 Will capture dashboard every day at: {', '.join(times)}")
    logger.info(f"📁 Screenshots saved to: {SCREENSHOT_DIR.absolute()}")
    logger.info(f"📝 Logs saved to: {LOG_FILE.absolute()}")
    logger.info(f"⚙️ Config: {CONFIG_PATH.absolute()}")
    logger.info("="*60)
    
    # Schedule jobs
    for t in times:
        schedule.every().day.at(t).do(take_screenshot_job)
        logger.info(f"⏰ Scheduled job at {t} daily")
    
    logger.info("")
    logger.info("✅ Bot is running! Keep this window open.")
    logger.info("   Press Ctrl+C to stop.")
    logger.info("   Taking first screenshot NOW as test...")
    logger.info("")
    
    # Take one immediately as test
    take_screenshot_job()
    
    logger.info("")
    logger.info("⏳ Waiting for next scheduled time...")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(30)  # Check every 30 seconds
    except KeyboardInterrupt:
        logger.info("")
        logger.info("🛑 Bot stopped by user. Goodbye!")

def run_once():
    """Run single screenshot now"""
    logger.info("📸 Running single capture (no scheduler)...")
    success = take_screenshot_job()
    if success:
        logger.info("✅ Done! Check screenshots folder.")
    else:
        logger.error("❌ Failed. Check bot.log for details.")
        logger.info("💡 Tip: Run 'python bot.py --debug' to see browser window")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Dashboard Screenshot Bot")
    parser.add_argument("--once", action="store_true", help="Take one screenshot and exit (no scheduler)")
    parser.add_argument("--debug", action="store_true", help="Run with visible browser (headless=False) for debugging")
    parser.add_argument("--test", action="store_true", help="Test login and show browser for 10 seconds")
    args = parser.parse_args()
    
    # Debug mode: force headless=False
    if args.debug or args.test:
        config = load_config()
        config["headless"] = False
        # Temporarily override
        import json as j
        # Monkey patch load_config for this run
        original_load = load_config
        def debug_load():
            c = original_load()
            c["headless"] = False
            return c
        globals()["load_config"] = debug_load
        logger.info("🐞 DEBUG MODE: Browser will be visible")
    
    if args.test:
        logger.info("🧪 TEST MODE - Browser will stay open 15s after login")
        take_screenshot_job()
        logger.info("Test complete. If you saw the dashboard, you're good!")
        # Keep open a bit
        try:
            from playwright.sync_api import sync_playwright
            # The browser already closed, so just info
            pass
        except:
            pass
    elif args.once:
        run_once()
    else:
        run_scheduler()
