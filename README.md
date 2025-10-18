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
- `--debug`: Enable debug output and console logging
- `--log-file [PATH]`: Specify log file path (default: askgpt.log)
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

- **Default**: No console output, automatic file logging to `askgpt.log`
- **With `--debug`**: Console logging enabled (real-time output in terminal) + file logging
- **With `--log-file`**: File logging to specified path + no console output
- **With both**: Both console and file logging enabled

#### Console Logging

Console logging is only enabled when using the `--debug` flag. This prevents verbose event output from cluttering the terminal during normal usage.

#### File Logging  

File logging is always enabled and defaults to `askgpt.log` in the current directory. Use the `--log-file` option to specify a different path:

- **Default**: Events logged to `askgpt.log`
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
