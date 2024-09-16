🤗 Hugging Face Link: https://huggingface.co/spaces/tugbadokumaci/chatbot

# Chatbot Application with RAG and Gradio UI

## Overview

A chatbot application that integrates **Retrieval-Augmented Generation (RAG)** using **llama** and **OpenAI GPT-3.5 Turbo API**. The UI is built with **Gradio**, using **HTML** and **CSS**. The chatbot references five modules from HM University stored in the `data` folder, and user sessions are logged with a voting feature.

## Features

- **RAG with llama** to enhance responses
- **Session logging** with a voting feature
- **Gradio-based UI**, customizable via CSS

## Installation

### Prerequisites

- **Conda** must be installed.
- An **OpenAI API Key** is required.

### Setup

1. Clone the repository:
   ```bash
   git clone <repository_url>
    ```
    or download manually as zip
2. Create and activate the Conda environment:
   ```bash
    conda create --name chatbot python=3.11.9
    conda activate chatbot
3. Install the required dependencies:<br>
   Open the zip file
   ```bash
    pip install -r requirements.txt
4. Set your OpenAI API key:
   ```bash
    export OPENAI_API_KEY="your_openai_api_key"
    echo $OPENAI_API_KEY
### Usage

- Run the application. 
   ```bash
    python app.py
