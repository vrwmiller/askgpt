# askgpt

A command line interface to ChatGPT that generates random questions and provides answers using OpenAI's language models.

## Features

- Generate random questions and get AI-powered answers
- Ask questions about specific topics
- Customize which OpenAI model to use
- Control token limits for both questions and answers
- Seeded randomization to prevent repetitive questions

## Installation

1. Clone this repository
2. Install dependencies:

   ```bash
   python3 -m venv venv && source venv/bin/activate
   python3 -m pip install --upgrade pip
   pip3 install -r requirements.txt
   ```

3. Set your OpenAI API key as an environment variable:

   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

## Usage

```bash
python3 askgpt.py [OPTIONS]
```

### Options

- `--random`: Generate a random question and get its answer
- `--topic "TOPIC"`: Generate a question about a specific topic and get its answer
- `--question "QUESTION"`: Ask a specific question directly to the model
- `--model MODEL`: Specify the OpenAI model to use (default: gpt-5)
- `--question-tokens N`: Maximum tokens for question generation (default: 512)
- `--answer-tokens N`: Maximum tokens for answer generation (default: 512)
- `--debug`: Enable debug output showing warnings and fallback attempts
- `--help`, `-h`: Show help message

### Available Models

The script dynamically fetches available models from the OpenAI API. Common models include:

- gpt-5 (default)
- gpt-4o
- gpt-4o-mini
- gpt-4-turbo
- gpt-4
- gpt-3.5-turbo

Note: The actual list of available models is fetched from the OpenAI API when you run the script.

### Examples

Generate a random question and answer:

```bash
python3 askgpt.py --random
```

Ask about a specific topic:

```bash
python3 askgpt.py --topic "artificial intelligence"
```

Ask a direct question:

```bash
python3 askgpt.py --question "What are the benefits of renewable energy?"
```

Use a different model:

```bash
python3 askgpt.py --topic "cooking" --model gpt-4o-mini
```

Customize token limits:

```bash
python3 askgpt.py --random --question-tokens 256 --answer-tokens 1024
```

Enable debug output to see warnings and fallback attempts:

```bash
python3 askgpt.py --random --debug
```

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)

## Requirements

- Python 3.6+
- OpenAI Python library
- Valid OpenAI API key
