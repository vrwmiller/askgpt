# askgpt

A powerful and flexible command-line interface for OpenAI's ChatGPT that transforms how you interact with AI language models. askgpt provides three distinct modes of operation: generate thought-provoking random questions, explore specific topics through AI-generated questions, or ask direct questions — all with intelligent model selection, robust error handling, and comprehensive logging.

## Why askgpt?

**🎯 Focused Interaction**: Unlike web interfaces, askgpt is designed for focused, distraction-free AI conversations directly in your terminal.

**🔧 Developer-Friendly**: Built with automation in mind, featuring comprehensive logging, error handling, and scriptable operations.

**🚀 Intelligent Resilience**: Automatic model fallback ensures reliability even when primary models are unavailable or unresponsive.

**📊 Terminal-Optimized**: Smart text formatting prevents awkward word wrapping while preserving structured content like lists and code blocks.

**🔍 Exploration Tool**: Perfect for brainstorming, research, learning, and discovery through AI-generated questions on any topic.

## Features

- **Three Operation Modes**:
  - **Random Questions**: Generate unexpected, thought-provoking questions on any topic
  - **Topic Exploration**: Create focused questions about specific subjects you want to explore
  - **Direct Q&A**: Ask specific questions directly for immediate answers

- **Smart Model Handling**:
  - Dynamic model discovery from OpenAI's latest API
  - Automatic parameter adaptation for different model generations
  - Intelligent fallback chain through 6 different models for maximum reliability
  - Support for both legacy and cutting-edge models (gpt-3.5-turbo through gpt-5)

- **Professional Output**:
  - Terminal-aware text formatting that respects your screen width
  - Preserves structured content (lists, code blocks, formatting)
  - Clean, readable output without awkward line breaks

- **Comprehensive Logging**:
  - Event-focused logging that tracks operations without storing sensitive content
  - Debug mode for troubleshooting and development
  - Configurable log file locations with automatic directory creation

- **Robust Error Handling**:
  - Graceful degradation when models fail or return empty responses
  - Clear error messages and helpful troubleshooting information
  - Automatic retry logic with different models

## Project Structure

```text
askgpt/
├── askgpt.py           # Main application entry point
├── README.md           # Project documentation
├── LICENSE             # MIT license
├── requirements.txt    # Python dependencies
├── setup.cfg           # Pytest and tool configuration
├── .gitignore          # Git ignore patterns
├── config/             # Configuration files
│   └── .vscode/        # VS Code settings
├── scripts/            # Development utilities
│   └── run_tests.py    # Test runner script
├── tests/              # Test suite
│   ├── test_askgpt.py  # Main application tests
│   └── test_logging.py # Logging functionality tests
├── logs/               # Log files directory
│   └── askgpt.log      # Default log file location
└── docs/               # Documentation (future use)
```

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
- `--debug`: Enable debug output and console logging
- `--log-file [PATH]`: Specify log file path (default: logs/askgpt.log)
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

Specify a custom log file:

```bash
python3 askgpt.py --random --log-file ./logs/session.log
```

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)

## Event Logging

The application includes comprehensive event logging to track operations and troubleshoot issues.

### Log Levels

- **INFO**: Session events, mode selection, API interactions, and completion status
- **WARNING**: Short/empty responses, API failures, and fallback attempts  
- **ERROR**: Critical errors, authentication failures, and system issues

### Log Output

Event logging behavior depends on the command line options used:

- **Default**: No console output, automatic file logging to `logs/askgpt.log`
- **With `--debug`**: Console logging enabled (real-time output in terminal) + file logging
- **With `--log-file`**: File logging to specified path + no console output
- **With both**: Both console and file logging enabled

#### Console Logging

Console logging is only enabled when using the `--debug` flag. This prevents verbose event output from cluttering the terminal during normal usage.

#### File Logging  

File logging is always enabled and defaults to `logs/askgpt.log` in the logs directory. Use the `--log-file` option to specify a different path:

- **Default**: Events logged to `logs/askgpt.log`
- `--log-file path/to/file.log`: Events logged to specified path

Log files use append mode, so multiple sessions accumulate in the same file.

Example log output:

```text
2025-10-17 20:57:33 - askgpt - INFO - === askgpt session started ===
2025-10-17 20:57:33 - askgpt - INFO - Command line arguments: --random
2025-10-17 20:57:33 - askgpt - INFO - Using random question generation mode
2025-10-17 20:57:33 - askgpt - INFO - Generating question random topic using model: gpt-5
2025-10-17 20:57:34 - askgpt - INFO - Chat completion successful in 0.85s
2025-10-17 20:57:34 - askgpt - INFO - Question generated successfully (length: 67 chars)
2025-10-17 20:57:35 - askgpt - INFO - Answer generated successfully (length: 342 chars)
2025-10-17 20:57:35 - askgpt - INFO - === askgpt session completed successfully ===
```

### Privacy & Content Logging

The logging system focuses on **events, not content**:

- ✅ **Logged**: Operation types, model names, response times, error messages, token counts
- ❌ **Not Logged**: API keys, user questions, AI responses, or other sensitive content

### Debug Mode

Use `--debug` to enable verbose logging with additional details about warnings and fallback attempts.

## Requirements

- Python 3.6+
- OpenAI Python library
- Valid OpenAI API key

## Testing

The project includes a comprehensive unit test suite located in the `tests/` directory.

### Running Tests

Run all tests:

```bash
python3 -m pytest
```

Run tests with verbose output:

```bash
python3 -m pytest -v
```

Run tests with coverage:

```bash
python3 -m pytest --cov=askgpt --cov-report=term-missing
```

### Custom Test Runner

Use the custom test runner for additional options:

```bash
# Basic test run
python3 run_tests.py

# With coverage and verbose output
python3 run_tests.py --coverage --verbose

# Generate HTML coverage report
python3 run_tests.py --coverage --html-coverage
```

### Test Structure

- `tests/test_askgpt.py` - Main unit test suite with 14 tests covering:
  - Model compatibility functions
  - OpenAI API integration
  - Question generation logic
  - Answer generation logic
  - Configuration validation
  - Error handling and fallback mechanisms

The test suite achieves 39% code coverage on core functionality and includes proper mocking of OpenAI API calls for reliable testing.
