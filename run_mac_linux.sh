#!/bin/bash
pip install -r requirements.txt
playwright install chromium
python setup.py
python bot.py
