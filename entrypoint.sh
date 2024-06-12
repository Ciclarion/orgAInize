#!/bin/bash

# Start the Triton Inference Server
echo "Starting Triton Inference Server..."
python3 /opt/scripts/launch_triton_server.py --model_repo /opt/tritonserver/triton_server --world_size 1

# If there are any other commands to run, you can add them here

# Prevent the container from exiting
tail -f /dev/null

