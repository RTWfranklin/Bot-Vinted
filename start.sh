#!/bin/bash
apt-get update
apt-get install -y chromium chromium-driver

echo "==== PATH Chromium ===="
which chromium || which chromium-browser || which google-chrome
echo "==== PATH Chromedriver ===="
which chromedriver

python3 bot.py

