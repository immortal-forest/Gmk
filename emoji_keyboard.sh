#!/usr/bin/env sh

cd /opt/gtk-emoji-keyboard
source venv/bin/activate

python emoji_keyboard.py "$1" &
exit 0