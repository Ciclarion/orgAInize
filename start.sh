#!/bin/bash

# Start Triton Inference Server
if [ "$(docker ps -aq -f name=triton-inference-server)" ]; then
    echo "Starting existing Triton Inference Server container..."
    docker start triton-inference-server
else
    echo "Creating and starting new Triton Inference Server container..."
    docker run -d --name triton-inference-server --privileged --gpus all --network host --shm-size=2g --ulimit memlock=-1 --ulimit stack=67108864 triton-inference-server
fi

# Start Chain Server
if [ "$(docker ps -aq -f name=chain-server)" ]; then
    echo "Starting existing Chain Server container..."
    docker start chain-server
else
    echo "Creating and starting new Chain Server container..."
    docker run -d --name chain-server --network host chain-server
fi

# Start Django Webapp
if [ "$(docker ps -aq -f name=webapp)" ]; then
    echo "Starting existing Webapp container..."
    docker start webapp
else
    echo "Creating and starting new Webapp container..."
    docker run -d --name webapp --network host webapp
fi


