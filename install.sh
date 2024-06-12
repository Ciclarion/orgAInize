#!/bin/bash
# Function to check if a command exists
command_exists() {
  command -v "$1" &>/dev/null
}

echo "Checking for Docker installation..."
if command_exists docker; then
  echo "Docker is already installed."
else
  echo "Installing Docker..."
  sudo apt-get update
  sudo apt-get install -y ca-certificates curl
  sudo install -m 0755 -d /etc/apt/keyrings
  sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
  sudo chmod a+r /etc/apt/keyrings/docker.asc

  # Add the repository to Apt sources:
  echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
    $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
    sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
  sudo apt-get update

  sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
fi

echo "Installing NVIDIA Container Toolkit..."
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
&& curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit


echo "Configuring NVIDIA Container Toolkit..."
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker



echo "Building the TensorRT-LLM Docker container..."
docker build -t tensorrt-llm -f Dockerfile.tensorrt-llm .
echo "TensorRT-LLM Docker container built successfully."

echo "Running the TensorRT-LLM container to build the model..."
docker run --name tensorrt-llm-builder --privileged --runtime=nvidia --gpus all -it tensorrt-llm /build_model.sh
echo "Model built inside the TensorRT-LLM container."

echo "Cloning tensorrtllm_backend repository..."
# Cloner le dépôt tensorrtllm_backend
git clone https://github.com/triton-inference-server/tensorrtllm_backend.git
cd tensorrtllm_backend
mkdir triton_server
echo "Repository cloned and triton_server directory created."



echo "Copying the built model to the host..."
mkdir -p triton_server/tensorrt_llm/1/vigostral-7b-chat
docker cp tensorrt-llm-builder:/TensorRT-LLM/examples/llama/tmp/llama/7B/trt_engines/f16/1-gpu ./triton_server/tensorrt_llm/1
docker cp tensorrt-llm-builder:/TensorRT-LLM/examples/llama/vigostral-7b-chat/tokenizer_config.json ./triton_server/tensorrt_llm/1/vigostral-7b-chat/tokenizer_config.json
docker cp tensorrt-llm-builder:/TensorRT-LLM/examples/llama/vigostral-7b-chat/config.json ./triton_server/tensorrt_llm/1/vigostral-7b-chat/config.json
docker cp tensorrt-llm-builder:/TensorRT-LLM/examples/llama/vigostral-7b-chat/tokenizer.model ./triton_server/tensorrt_llm/1/vigostral-7b-chat/tokenizer.model
echo "Model copied to the host successfully."

echo "Copying Config models to triton_server..."
# Copier les modèles d'exemple dans le référentiel de modèles
cp -r ../triton_config/* triton_server/
echo "Config models copied."

cd ..
echo "Building the Triton Inference Server Docker container..."
docker build -t triton-inference-server -f Dockerfile.triton .
echo "Triton Inference Server Docker container built successfully."


echo "Building LangChain Server Docker container..."
# Build Chain-Server Docker container
docker build -t chain-server -f Dockerfile.chain-server .
echo "LangChain Server Docker container built successfully."

echo "Building the Webapp Django Docker container..."
# Build Webapp Docker container
docker build -t webapp -f Dockerfile.webapp .
echo "Webapp Django Docker container built successfully."

