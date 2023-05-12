#!/bin/bash

export DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/1002/bus"
export XDG_RUNTIME_DIR="/run/user/1002"


echo -n $(date)
echo -n " : "


if curl -s http://127.0.0.1:8002/parser/healthy | grep -q "$string"; then
    echo "server healthy, doing nothing"
else
    echo "server unhealthy, restarting"
    bash /home/arboratorgrew/arborator-parser/run_restart_prod.sh
fi