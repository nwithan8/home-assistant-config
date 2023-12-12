#!/usr/bin/with-contenv bashio

FILE_NAME=$1
DEVICE_ID=$2
API_KEY=$3

RENDER_FILE="/render.webp"

# Render file
/usr/bin/pixlet/pixlet render "$FILE_NAME" -o "$RENDER_FILE"

# Push file
/usr/bin/pixlet/pixlet push --api-token "$API_KEY" "$DEVICE_ID" "$RENDER_FILE"
