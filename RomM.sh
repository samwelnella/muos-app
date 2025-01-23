#!/bin/bash

# Check if pip is installed
if ! command -v pip3 &> /dev/null
then
    python3 -m ensurepip --default-pip
fi

# Check if pillow is installed
if ! python3 -c "import PIL" &> /dev/null
then
    pip3 install pillow
fi

# Check if dotenv is installed
if ! python3 -c "import dotenv" &> /dev/null
then
    pip install python-dotenv
fi

ROOT_DIR=/mnt/mmc/MUOS/application/RomM
LOG_DIR=$ROOT_DIR/logs
mkdir -p $LOG_DIR

cd $ROOT_DIR

ENTRYPOINT="python3 main.py"

$ENTRYPOINT > "$LOG_DIR/$(date +'%Y-%m-%d_%H-%M-%S').log" 2>&1
