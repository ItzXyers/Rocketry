#!/bin/sh
# Idempotent: called from systemd/wlan0-ap-iface.service, which may re-run
# this on service restart, so every step tolerates already-done state.
set -e

if ! ip link show wlan0_ap >/dev/null 2>&1; then
    iw dev wlan0 interface add wlan0_ap type __ap
fi

ip link set wlan0_ap up

if ! ip addr show wlan0_ap | grep -q '192\.168\.50\.1/24'; then
    ip addr add 192.168.50.1/24 dev wlan0_ap
fi
