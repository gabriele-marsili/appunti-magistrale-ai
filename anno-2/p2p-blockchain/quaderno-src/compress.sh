#!/bin/bash
# uso: compress.sh input.pdf output.pdf
gs -q -sDEVICE=pdfwrite -dCompatibilityLevel=1.5 -dPDFSETTINGS=/ebook -dDetectDuplicateImages=true \
 -dDownsampleColorImages=true -dColorImageResolution=100 -dColorImageDownsampleThreshold=1.2 \
 -dDownsampleGrayImages=true -dGrayImageResolution=100 -dNOPAUSE -dBATCH -sOutputFile="$2" "$1" 2>/dev/null
o=$(stat -c%s "$1"); if [ ! -s "$2" ] || [ $(stat -c%s "$2") -gt $o ]; then cp "$1" "$2"; fi
