# Copilot Instructions

## Project Overview
This repository contains source code used to evaluate and test GitHub, GitHub Copilot, and OpenAI capabilities for code generation, natural language processing, and AI-assisted development.

## Project Conventions
- Python scripts use the `.py` extension and follow a 4 whitespace indentation style.
- Emojis aren't used in code files, documentation, or comments.
- Code is commented using docstrings and inline comments where necessary.
- The project uses a `requirements.txt` file to manage Python dependencies.
- The main script for user interaction is `askgpt.py`.

## Key Workflows
* Run locally:
    ```bash
    python3 -m venv venv && source venv/bin/activate
    pip3 install -r requirements.txt
    python3 -m pip install --upgrade pip
    ```