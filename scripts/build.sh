#!/bin/bash

APPLICATION_DIR=mnt/mmc/MUOS/application
GLYPH_DIR=opt/muos/default/MUOS/theme/active/glyph/muxapp
FONTS_FIR=usr/share/fonts/romm
ZIP_BASE_NAME=romm_muOS_install
VERSION=$(grep -oP '(?<=version = ")[^"]*' .romm/__version__.py)
echo "Extracted version: $VERSION"

mkdir -p .dist
mkdir -p ".build/${APPLICATION_DIR}"
cp RomM.sh ".build/${APPLICATION_DIR}"
rsync -av --exclude='__pycache__' --exclude='fonts' --exclude='.env' .romm/ ".build/${APPLICATION_DIR}/.romm/"

mkdir -p ".build/${GLYPH_DIR}"
cp .romm/resources/romm.png ".build/${GLYPH_DIR}"

mkdir -p ".build/${FONTS_FIR}"
cp .romm/fonts/romm.ttf ".build/${FONTS_FIR}"

(cd .build && zip -r "../${ZIP_BASE_NAME}_${VERSION}.zip" *)
ls -lah  # Debug: Check if ZIP exists in the root
mv "${ZIP_BASE_NAME}_${VERSION}.zip" ".dist/${ZIP_BASE_NAME}_${VERSION}.zip"
ls -lah .dist  # Debug: Ensure the file was moved correctly
rm -rf .build
