#!/bin/bash
# Startup script for Rainbow Weather Clock
# Place in startup applications or run at boot

cd /home/tony/random/ubuntu-mastery/clock
python3 clock_v8_rainbow_weather.py &

echo "Rainbow Weather Clock started at $(date)"