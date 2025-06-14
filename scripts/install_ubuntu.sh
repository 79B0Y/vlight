#!/usr/bin/env bash
set -e

if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root" >&2
    exit 1
fi

INSTALL_DIR=/opt/vlight
VENV_DIR=$INSTALL_DIR/venv

apt-get update
apt-get install -y python3 python3-venv

mkdir -p "$INSTALL_DIR"
cp configuration.yaml "$INSTALL_DIR/"

python3 -m venv "$VENV_DIR"
"$VENV_DIR/bin/pip" install --upgrade pip
"$VENV_DIR/bin/pip" install .

cat >/etc/systemd/system/vlight.service <<SERVICE
[Unit]
Description=Vlight MQTT Simulation Service
After=network.target

[Service]
Type=simple
WorkingDirectory=$INSTALL_DIR
ExecStart=$VENV_DIR/bin/vlight -c $INSTALL_DIR/configuration.yaml
Restart=always

[Install]
WantedBy=multi-user.target
SERVICE

systemctl daemon-reload
systemctl enable vlight.service
systemctl start vlight.service

echo "Vlight installed and started"

