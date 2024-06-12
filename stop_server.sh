#!/bin/bash

# Start Triton Inference Server
if [ "$(docker ps -aq -f name=triton-inference-server)" ]; then
    echo "Stopping existing Triton Inference Server container..."
    docker stop triton-inference-server
fi

# Start Chain Server
if [ "$(docker ps -aq -f name=chain-server)" ]; then
    echo "Stopping existing Chain Server container..."
    docker stop chain-server
fi

# Start Django Webapp
if [ "$(docker ps -aq -f name=webapp)" ]; then
    echo "Stopping existing Webapp container..."
    docker stop webapp
fi


