@echo off
echo Installing requirements...
pip install -r requirements.txt
playwright install chromium
echo.
echo Running setup...
python setup.py
echo.
echo Starting bot (twice daily)...
python bot.py
pause
