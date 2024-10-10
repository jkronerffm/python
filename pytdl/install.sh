#!/bin/bash
wget https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -O ~/.local/bin/yt-dlp
chmod a+rx ~/.local/bin/yt-dlp  # Make executable

python3 -m venv ./venv
source ./venv/bin/activate
python3 -m pip install pytube
python3 -m pip install pyqt5
python3 -m pip install pillow
python3 -m pip install requests
