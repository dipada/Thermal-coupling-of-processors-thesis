#!/bin/bash

# List of all active service
active_services=$(service --status-all | grep + | awk '{print $4}')

# Stop all services
for service in $active_services
do
    sudo service "$service" stop
done

echo "All services stopped"
