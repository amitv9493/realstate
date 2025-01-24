#!/bin/bash

handle_error() {
    echo "Error: $1"
    exit 1
}


git pull || handle_error "Failed to pull latest changes from the repository"

docker compose build django celeryworker celerybeat flower || handle_error "Failed to build Docker container"

docker compose up django celeryworker celerybeat flower || handle_error "Failed to start containers"

echo "Restarted Successfully"
exit 0
