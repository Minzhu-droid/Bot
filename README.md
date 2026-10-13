# 🤖 Dashboard Screenshot Bot

**Automatically logs in to any website and takes pictures of your dashboard twice a day.**

You just put your web link + username + password → it does the rest.

---

### ✨ What it does
- ✅ Logs in for you automatically (auto-detects username/password fields)
- ✅ Takes full-page screenshot of dashboard
- ✅ Runs **twice daily** (e.g. 9:00 AM & 9:00 PM) - customizable
- ✅ Saves screenshots organized by date: `screenshots/2026-10-13/dashboard_09-00-00.png`
- ✅ Runs in background (headless)
- ✅ Works with ANY website

---

### 🚀 Quick Start (3 steps)

#### 1. Install
Open terminal / command prompt in this folder and run:

```bash
pip install -r requirements.txt
playwright install chromium
```

> On Windows you may need: `python -m pip install -r requirements.txt`

#### 2. Configure - Put Your Details
**EASY WAY:**
```bash
python setup.py
```
It will ask you:
- Website login link (`https://your-site.com/login`)
- Dashboard link (if different after login, or leave empty)
- Username / Email
- Password

**MANUAL WAY:** Edit `config.json` directly:
```json
{
  "login_url": "https://your-website.com/login",
  "dashboard_url": "https://your-website.com/dashboard",
  "username": "your@email.com",
  "password": "yourpassword",
  "times": ["09:00", "21:00"]
}
```

#### 3. Run

| Command | What it does |
|---------|--------------|
| `python bot.py --test` | **Test first!** Opens visible browser so you see login working |
| `python bot.py --once` | Takes 1 screenshot now and exits |
| `python bot.py` | **Normal mode** - Takes screenshot now, then waits and runs twice daily automatically. **Keep this window open!** |
| `python bot.py --debug` | Debug mode - shows browser if login fails |

---

### 📁 Where are my screenshots?

```
dashboard-bot/
├── screenshots/
│   ├── 2026-10-13/
│   │   ├── dashboard_09-00-00.png
│   │   └── dashboard_21-00-00.png
│   └── 2026-10-14/
│       └── dashboard_09-00-00.png
├── bot.log  <-- log file if something fails
└── bot.py
```

---

### ⚙️ Config Options (`config.json`)

| Field | Description |
|-------|-------------|
| `login_url` | **Required.** Login page URL |
| `dashboard_url` | Optional. If dashboard is at different URL after login, put it here. Otherwise leave `""` |
| `username` | Your username/email |
| `password` | Your password |
| `times` | Array of times. Default `["09:00","21:00"]` = 9am & 9pm. Change to `["08:00","18:00"]` etc. |
| `headless` | `true` = hidden background, `false` = show browser |
| `wait_after_login` | Seconds to wait after login before screenshot (increase to 8-10 if dashboard loads slow) |
| `username_selector` etc. | Leave empty. Only needed if auto-detect fails. Ask me for help! |

---

### 🔧 Troubleshooting

**1. Login fails / screenshot shows login page again**
- Run `python bot.py --debug` to see browser
- Website might have CAPTCHA or 2FA. Bot will save `DEBUG_*.png` so you can see error.
- If site has special selectors, tell me the website link and I can give you exact selectors to put in `config.json`:
  ```json
  "username_selector": "#email",
  "password_selector": "#password",
  "login_button_selector": "button[type='submit']"
  ```
  To find selectors: Right-click login field → Inspect → copy selector.

**2. How to find the correct selectors?**
- Open your login page in Chrome → Press F12 → Click arrow icon → Click username field → See highlighted HTML → copy `id` or `name`.

**3. Want to run even when PC is off / window closed?**
- **Windows:** Use Task Scheduler → Create Task → Run `python bot.py --once` twice daily
- **Mac/Linux:** Use `cron` → `crontab -e` → add `0 9,21 * * * /usr/bin/python3 /path/to/bot.py --once`
- **24/7 Cloud:** Deploy to a VPS or PythonAnywhere, run `python bot.py` with `nohup`

**4. `playwright not installed` error**
```bash
pip install playwright
playwright install chromium
# or
python -m playwright install chromium
```

---

### 🔒 Security
- Your `config.json` stays on YOUR computer only, never uploaded
- Add `config.json` to `.gitignore` if using git
- Bot uses real Chromium browser, handles cookies/sessions like a human

---

### 💬 Need Help?
Tell me:
1. Your website link
2. Screenshot of the login page (or `DEBUG_*.png` from screenshots folder)
3. I will give you the exact config to fix it!

---

**Made for you - Works with any dashboard, admin panel, trading site, etc.**
