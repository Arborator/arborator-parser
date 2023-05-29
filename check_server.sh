#!/bin/bash
HEALTHY=$(curl --silent http://localhost:8002/parser/healthy | jq -r .healthy)


echo "Script started: $(date)"


if [ "$HEALTHY" != "true" ]
then
    echo "Server is not healthy, restarting..."
#    systemctl restart my-service
    systemctl --user restart arborator-parser.service
    systemctl --user restart arborator-parser-celery.service
else
    echo "Server is healthy, no action needed."
fi
