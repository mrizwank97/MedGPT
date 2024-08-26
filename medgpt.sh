#!/bin/bash

# Get the latest Git commit hash (short version)
IMAGE_TAG=$(git rev-parse HEAD)

# Function to bring up Docker Compose
up() {
    echo "Using IMAGE_TAG: $IMAGE_TAG"
    export IMAGE_TAG
    docker compose up -d --build
}

# Function to bring down Docker Compose
down() {
    docker compose down
}

test(){
    echo "Using IMAGE_TAG: $IMAGE_TAG"
    export IMAGE_TAG
    docker compose -f docker-compose-test.yml run --rm web --build
    echo $?  
}

# Parse the command argument
case "$1" in
    up)
        up
        ;;
    down)
        down
        ;;
    test)
        test
        ;;
    *)
        echo "Usage: $0 {up|down|test}"
        exit 1
        ;;
esac

