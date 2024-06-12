# OrgAInize

## Overview

OrgAInize is a AI-powered project designed to streamline organization and productivity through advanced natural language processing capabilities. 

OrgAInize aims to empower companies with intelligent management of their documents and training materials. By running the AI locally, it ensures that information remains within the company, learning (or unlearning) through a RAG pipeline. Users can interact with a chatbot to query the content of these documents and automatically retrieve the documents upon request. The system supports different access levels, facilitating use across the entire organization at various scales.

This project was designed to address a real-world use case within a French engineering school, enabling administrative staff and teachers to train an AI that serves as a companion for students. It was crucial that students only access information intended for them, while allowing company staff to utilize the AI with more sensitive information.

## Features

- **Runs Locally**: Utilizes a lightweight LLM model (Vigostral 7B) and Nvidia TensorRT LLM, operating on a simple Ubuntu server equipped with an RTX3090 graphics card. This ensures that data never leaves the company premises.
- **User-Friendly RAG Pipeline**: Easily add or remove documents and training information from the AI's knowledge base at any time, ensuring up-to-date responses.
- **Interactive ChatBot**: Accurate and interactive chatbot with conversation history, specialized in the French language, enabling various scenarios such as automatic assignment correction, document queries, information synthesis from multiple sources, and more.
- **Document Retrieval**: Users can request the AI to find documents, saving time spent searching through the sometimes archaic organizational structures of the company's digital files.
- **Multi-Level User Access**: Defined access levels with two information tiers: "External" and "Internal". "Professional" users (teachers, administrative staff, etc.) can add and remove content from the AI's knowledge base and receive comprehensive responses from the chatbot. In contrast, "Student" users only have access to the chatbot, which will respond based on "External" information only. These access levels can be easily extended.


## Technologies Used

OrgAInize is built using several key technologies, each contributing to different components of the system:

1. **Nvidia TensorRT LLM**:
   - Converts the Vigostral-7B model into TensorRT format, optimizing its use on Nvidia GPUs, specifically the RTX3090.

2. **Nvidia Triton Inference Server**:
   - Provides a high-performance server for executing queries on the LLM model, ensuring efficient and scalable inference.

3. **Langchain**:
   - A framework for developing applications powered by large language models, enabling seamless integration and management of AI components.
   - Combined with FastAPI, it handles the entire RAG (Retrieval-Augmented Generation) pipeline, leveraging Chromadb for efficient storage and retrieval of embeddings.

4. **Django**:
   - Used for designing the web application, offering a robust framework for developing user interfaces and backend services.

## Requirements

- Unbutu (tested on 24.04)
- Good Nvidia GPU with capabilites to run CUDA 12.x (tested on RTX3090)
- Docker installed 

## Installation

The installation process is straightforward, facilitated by the design of a shell script and the deployment of Docker containers for each component (totaling 4 Docker containers). However, it's essential to note that the complete installation process take a lot of time as it will : 
-Set-up all dockers
-Download the model from HuggingFace
-Convert the model to TensorRT
-Config all the servers

To set up the project, follow these two easy steps:

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/yourusername/OrgAInize.git
    cd OrgAInize
    ```

2. **Run the Setup Script**:
    ```bash
    ./install.sh
    ```
Note : All the scripts are designed to work with Vigostral-7B model. If you want to use another one, you'll have to change the "git clone " line from Huggingface.

## Usage

To start the entire system you only need , execute the `start.sh` script:

```bash
./start.sh
```

This will initialize and run all necessary Docker containers for the web application, chain server, and Triton inference server. You will then be able to access the website on 127.0.0.1:8010 

To stop the services, use the stop.sh script:
```bash
./stop_server.sh
```
## Workflow

1. **User Interaction with WebApplication**: Users interact with the WebApplication to upload/manage documents or create/amange formations.

2. **Data Processing with Langchain-Server and ChromaDB**:
   - The WebApplication sends the documents and relevant metadata to the Langchain-server.
   - Langchain proceeds to embed and index the documents into ChromaDB, enabling efficient search and retrieval.

3. **Query Processing with Chatbot and LLM Model**:
   - When a user asks questions to the chatbot, the question and the chat history are sent to the Large Language Model (LLM) Model running on the Nvidia Triton Server Inference.
   - The LLM Model rephrases the question as a Standalone Question, eliminating the need for the chat history.
   - The Standalone Question is then used by Langchain-server to search for similar information within the indexed documents.
   - The relevant information is then sent to the Nvidia Triton Server, where our LLM model is running, to generate the final response.

4. **Response Delivery to User**: The generated answer is returned to the user from the Triton Server, providing a seamless user experience.


## Acknowledgements

- **NVIDIA**: We express our gratitude to NVIDIA for their invaluable contributions to the AI community, including the powerful [NVIDIA TensorRT LLM](https://github.com/NVIDIA/TensorRT-LLM) framework, which optimizes language models for deployment on NVIDIA GPUs, and the [NVIDIA Triton Inference Server](https://developer.nvidia.com/triton-inference-server), a high-performance server for model serving. We also acknowledge NVIDIA for providing extensive resources and support on the internet, which greatly contribute to the success of projects like ours.

- **Langchain**: We extend our appreciation to [Langchain](https://www.langchain.com/) for providing the robust framework that powers our language models and facilitates seamless integration and management of AI components.

- **Bofeng Huang**: Special thanks to Bofeng Huang for developing the Vigostral model. You can find more about Bofeng Huang's work on his [GitHub](https://github.com/bofenghuang/vigogne).

