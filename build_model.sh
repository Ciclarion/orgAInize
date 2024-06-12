#!/bin/bash

echo "Cloning the Llama model repository..."
# Cloner le dépôt du modèle Llama
git clone https://huggingface.co/bofenghuang/vigostral-7b-chat
echo "Repository cloned successfully."

echo "Running checkpoint conversion..."
# Exécuter le script de conversion
python3 convert_checkpoint.py --model_dir ./vigostral-7b-chat \
                              --output_dir ./tllm_checkpoint_1gpu_f16 \
                              --dtype float16
echo "Checkpoint conversion completed."

echo "Building the TRT engine..."
# Construire le moteur TRT
trtllm-build --checkpoint_dir ./tllm_checkpoint_1gpu_f16 \
             --output_dir ./tmp/llama/7B/trt_engines/f16/1-gpu \
             --gpt_attention_plugin float16 \
             --gemm_plugin float16  \
             --remove_input_padding enable \
             --paged_kv_cache enable \
             --max_batch_size 16 \
             --context_fmha enable \
             --max_input_len 4096
echo "TRT engine built successfully."


