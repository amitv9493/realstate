#!/bin/bash

handle_error() {
    echo "Error: $1"
    exit 1
}


git pull || handle_error "Failed to pull latest changes from the repository"

docker compose build django traefik celeryworker celerybeat redis nginx flower || handle_error "Failed to build Docker container"

docker compose up django traefik celeryworker celerybeat redis nginx flower || handle_error "Failed to start containers"

echo "Deployed Successfully"
exit 0
