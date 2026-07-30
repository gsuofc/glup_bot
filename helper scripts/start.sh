#!/bin/bash
set -e 

cd /home/user/glup_bot # or whatever you saved as

git pull

#sudo apt install python3-venv -y
#python3 -m venv glupenv

source glupenv/bin/activate # Change to whatever ENV is

if ! pip install -r requirements.txt; then
    echo "Dependency installation failed."
    exit 1
fi

exec python3 main.py