#!/bin/bash
apt-get update
apt-get install -y chromium chromium-driver
pip install --upgrade pip
pip install -r requirements.txt
python3 bot.py
