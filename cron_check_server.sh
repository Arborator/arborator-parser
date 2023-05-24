#!/bin/bash

export DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/1002/bus"
export XDG_RUNTIME_DIR="/run/user/1002"


echo -n $(date)
echo -n " : "

response=$(curl -o /dev/null -s -w "%{http_code}\n" http://127.0.0.1:8002/parser/healthy)

if [ "$response" -eq 502 ]
then
  echo "Server returned 502 Bad Gateway, restarting ..."
  bash /home/arboratorgrew/arborator-parser/run_restart_prod.sh
elif [ "$response" -eq 200 ] 
then
  echo "Server is healthy, doing nothing"
else
  echo "Server returned $response , restarting ..."
  bash /home/arboratorgrew/arborator-parser/run_restart_prod.sh
fi

