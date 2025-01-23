#!/bin/bash
# HELP: RomM muOS client to download roms directly from your RomM server
# ICON: romm

. /opt/muos/script/var/func.sh

echo app >/tmp/act_go

ROOT_DIR="$(GET_VAR "device" "storage/rom/mount")/MUOS/application/.romm"
LOG_DIR="${ROOT_DIR}/logs"
mkdir -p "${LOG_DIR}"

# Check if romm.png exists
if ! -f /opt/muos/default/MUOS/theme/active/glyph/muxapp/romm.png
then
    cp "${ROOT_DIR}/resources/romm.png" "/opt/muos/default/MUOS/theme/active/glyph/muxapp/romm.png"
fi

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


cd "${ROOT_DIR}" || exit

ENTRYPOINT="python3 main.py"

${ENTRYPOINT} > "${LOG_DIR}/$(date +'%Y-%m-%d_%H-%M-%S').log" 2>&1
