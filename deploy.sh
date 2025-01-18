#!/bin/bash

# Check if Redis is installed
if command -v redis-server &>/dev/null; then
    echo "Redis is installed."
else
    echo "Redis is not installed. Installing Redis..."
    sudo apt-get update
    sudo apt-get install redis-server -y
    sudo systemctl start redis-server
    sudo systemctl enable redis-server
fi

SERVICES=("marketcap_updater" "marketcap_server")
SOURCE_DIR=deployment/systemd
DESTINATION_DIR=/etc/systemd/system
WORKING_DIR=$(pwd)
USERNAME=$(whoami)

for SERVICE in "${SERVICES[@]}"; do
    SOURCE_FILE="$SOURCE_DIR/${SERVICE}.service"
    DESTINATION_FILE="$DESTINATION_DIR/${SERVICE}.service"

    sudo sed -e "s|%h%|$WORKING_DIR|g" -e "s|User=user|User=$USERNAME|g" "$SOURCE_FILE" | sudo tee "$DESTINATION_FILE" >/dev/null
    echo "${SERVICE}.service deployed"
done

sudo systemctl daemon-reload

for SERVICE in "${SERVICES[@]}"; do
    sudo systemctl enable "${SERVICE}.service"
    sudo systemctl start "${SERVICE}.service"
    echo "${SERVICE}.service started"
done
