#!/bin/bash

APPLICATION_DIR=mnt/mmc/MUOS/application
GLYPH_DIR=opt/muos/default/MUOS/theme/active/glyph/muxapp
FONTS_FIR=usr/share/fonts/romm
VERSION=$(grep -oP '(?<=version = ")[^"]*' .romm/__version__.py)

mkdir -p .dist
mkdir -p .build/${APPLICATION_DIR}
cp RomM.sh .build/${APPLICATION_DIR}
rsync -av --exclude='__pycache__' --exclude='fonts' --exclude='.env' .romm/ .build/${APPLICATION_DIR}/.romm/

mkdir -p .build/${GLYPH_DIR}
cp .romm/resources/romm.png .build/${GLYPH_DIR}

mkdir -p .build/${FONTS_FIR}
cp .romm/fonts/romm.ttf .build/${FONTS_FIR}

(cd .build && zip -r ../romm_archive_install_${VERSION}.zip *)
mv romm_archive_install_${VERSION}.zip .dist/romm_archive_install_${VERSION}.zip
rm -rf .build
