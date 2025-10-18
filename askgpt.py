#!/usr/bin/env python3
"""
askgpt - A command line interface to ChatGPT

This script provides a CLI for interacting with OpenAI's language models.
It supports generating random questions or topic-specific questions,
then getting AI-powered answers. The script handles different model APIs
and provides fallback mechanisms for reliability.

Key features:
- Dynamic model discovery from OpenAI API
- Smart parameter handling for different model generations
- Fallback logic for unreliable models
- Debug mode for troubleshooting
- Configurable token limits and model selection

Author: Command-line interface for OpenAI ChatGPT
"""

import argparse
import logging
import os
import random
import sys
import time
from openai import OpenAI

# Logging configuration
def setup_logging(debug=False):
    """
    Configure logging for the application.
    
    Args:
        debug (bool): Whether to enable debug-level logging
    """
    log_level = logging.DEBUG if debug else logging.INFO
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Create logger for this module
    logger = logging.getLogger('askgpt')
    return logger

# Configuration constants
DEFAULT_MODEL = "gpt-5"  # Primary model to use by default
DEFAULT_MAX_TOKENS = 512  # Default token limit for both questions and answers

# Fallback model list used when API model discovery fails
# Ordered by preference, with most capable models first
FALLBACK_MODELS = [
    "gpt-5",
    "gpt-4o",
    "gpt-4o-mini", 
    "gpt-4-turbo",
    "gpt-4",
    "gpt-3.5-turbo"
]


def fetch_available_models():
    """
    Fetches the list of available models from the OpenAI API.
    
    This function dynamically discovers which models are currently available
    from OpenAI, allowing the script to stay up-to-date with new releases
    without manual updates.
    
    Returns:
        list: A list of model names (strings) available from the API.
              Returns empty list if the API call fails.
    
    Note:
        Requires OPENAI_API_KEY environment variable to be set.
        This call may take a moment to complete on first run.
    """
    logger = logging.getLogger('askgpt')
    logger.info("Fetching available models from OpenAI API")
    
    try:
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        models = client.models.list()
        # Extract just the model IDs from the API response objects
        model_names = [model.id for model in models]
        logger.info(f"Successfully fetched {len(model_names)} models from API")
        return model_names
    except Exception as e:
        logger.warning(f"Failed to fetch models from API: {e}")
        # Silently fail - caller will handle empty list appropriately
        print(f"Error fetching models: {e}")
        return []


def get_openai_client():
    """
    Initialize and return OpenAI client using API key from environment.
    
    This function creates a properly authenticated OpenAI client instance
    that can be used for API calls throughout the application.
    
    Returns:
        OpenAI: Authenticated OpenAI client instance
    
    Raises:
        SystemExit: If OPENAI_API_KEY environment variable is not set
    
    Environment Variables:
        OPENAI_API_KEY: Required. Your OpenAI API key for authentication.
    """
    logger = logging.getLogger('askgpt')
    logger.info("Initializing OpenAI client")
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        logger.error("OpenAI API key not found in environment variables")
        print("Error: OPENAI_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)
    
    logger.info("OpenAI client initialized successfully")
    return OpenAI(api_key=api_key)


def uses_max_completion_tokens(model):
    """
    Check if a model uses max_completion_tokens instead of max_tokens.
    
    OpenAI introduced new parameter naming conventions with newer models.
    This function determines which parameter name to use based on the model.
    
    Args:
        model (str): The model name to check
    
    Returns:
        bool: True if model uses max_completion_tokens, False for max_tokens
    
    Note:
        Newer model families (gpt-5, gpt-4o, o1, o3, o4, gpt-4.1) use the
        new parameter name. Legacy models use the original max_tokens parameter.
    """
    newer_model_prefixes = ['gpt-5', 'gpt-4o', 'o1', 'o3', 'o4', 'gpt-4.1']
    return any(model.startswith(prefix) for prefix in newer_model_prefixes)


def supports_custom_temperature(model):
    """
    Check if a model supports custom temperature values.
    
    Some newer OpenAI models only support the default temperature value (1.0)
    and will reject requests with custom temperature settings.
    
    Args:
        model (str): The model name to check
    
    Returns:
        bool: True if model supports custom temperature, False if restricted
    
    Note:
        Models like gpt-5 and the reasoning models (o1, o3, o4) are restricted
        to default temperature only. This prevents API errors when attempting
        to use creative temperature settings with these models.
    """
    # Models that only support default temperature (1.0)
    restricted_models = ['gpt-5', 'o1', 'o3', 'o4']
    return not any(model.startswith(prefix) for prefix in restricted_models)


def create_chat_completion(client, model, messages, max_tokens, temperature):
    """
    Create a chat completion with the appropriate parameters for the model.
    
    This function abstracts away the differences between model APIs by
    automatically selecting the correct parameter names and values based
    on the specific model being used.
    
    Args:
        client (OpenAI): Authenticated OpenAI client instance
        model (str): Model name to use for completion
        messages (list): List of message dictionaries for the conversation
        max_tokens (int): Maximum tokens to generate
        temperature (float): Creativity setting (ignored for restricted models)
    
    Returns:
        ChatCompletion: OpenAI API response object
    
    Note:
        This function handles the API parameter differences between model
        generations automatically:
        - Newer models use max_completion_tokens vs max_tokens
        - Some models don't support custom temperature values
    """
    # Prepare base parameters that all models support
    params = {
        'model': model,
        'messages': messages
    }
    
    # Add token limit parameter (API parameter name varies by model generation)
    if uses_max_completion_tokens(model):
        params['max_completion_tokens'] = max_tokens
    else:
        params['max_tokens'] = max_tokens
    
    # Add temperature parameter only if the model supports it
    # (Some newer models are restricted to default temperature)
    if supports_custom_temperature(model):
        params['temperature'] = temperature
    
    logger = logging.getLogger('askgpt')
    logger.info(f"Creating chat completion with model: {model}, max_tokens: {max_tokens}")
    
    start_time = time.time()
    try:
        response = client.chat.completions.create(**params)
        elapsed_time = time.time() - start_time
        logger.info(f"Chat completion successful in {elapsed_time:.2f}s")
        return response
    except Exception as e:
        elapsed_time = time.time() - start_time
        logger.error(f"Chat completion failed after {elapsed_time:.2f}s: {e}")
        raise


def generate_question(client, topic=None, model=DEFAULT_MODEL, max_tokens=DEFAULT_MAX_TOKENS, debug=False):
    """
    Generate a question, optionally about a specific topic.
    
    This function prompts the AI to create an interesting, thought-provoking
    question. It can generate random questions or focus on a specific topic.
    Includes fallback logic for unreliable models.
    
    Args:
        client (OpenAI): Authenticated OpenAI client instance
        topic (str, optional): Specific topic to generate question about.
                              If None, generates a random topic question.
        model (str): Model name to use for generation
        max_tokens (int): Maximum tokens for the generated question
        debug (bool): Whether to show debug output for troubleshooting
    
    Returns:
        tuple: (question_text, actual_model_used)
               question_text (str): The generated question
               actual_model_used (str): Model that successfully generated the response
    
    Note:
        Uses higher temperature (0.9) for creativity. If the specified model
        fails or returns empty content, automatically falls back to gpt-4o
        for reliability.
    """
    logger = logging.getLogger('askgpt')
    topic_info = f"about '{topic}'" if topic else "random topic"
    logger.info(f"Generating question {topic_info} using model: {model}")
    
    # Craft the prompt based on whether a topic was specified
    if topic:
        prompt = f"Generate an interesting and thought-provoking question about {topic}. Only provide the question, no answer."
    else:
        prompt = "Generate an interesting and thought-provoking question about any topic. Only provide the question, no answer."
    
    try:
        response = create_chat_completion(
            client=client,
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.9  # Higher temperature for more creativity
        )
        question = response.choices[0].message.content.strip()
        
        # Validate response quality - some models return empty or very short responses
        if not question or len(question) < 10:
            logger.warning(f"Model {model} returned short/empty question: '{question}'")
            if debug:
                print(f"Warning: Model {model} returned an empty or very short response", file=sys.stderr)
                print(f"Response received: '{question}'", file=sys.stderr)
            
            # If using default model and it fails, try fallback
            if model == DEFAULT_MODEL:
                logger.info("Attempting fallback to gpt-4o")
                if debug:
                    print("Trying with gpt-4o as fallback...", file=sys.stderr)
                return generate_question(client, topic, "gpt-4o", max_tokens, debug)
        
        logger.info(f"Question generated successfully (length: {len(question)} chars)")
        return question, model
    except Exception as e:
        logger.error(f"Error generating question with {model}: {e}")
        if debug:
            print(f"Error generating question with {model}: {e}", file=sys.stderr)
        
        # Try fallback models if current model fails
        for fallback_model in FALLBACK_MODELS:
            if fallback_model != model:  # Don't retry the same model
                try:
                    logger.info(f"Trying fallback model: {fallback_model}")
                    if debug:
                        print(f"Trying fallback model: {fallback_model}", file=sys.stderr)
                    return generate_question(client, topic, fallback_model, max_tokens, debug)
                except Exception as fallback_error:
                    logger.warning(f"Fallback model {fallback_model} failed: {fallback_error}")
                    if debug:
                        print(f"Fallback model {fallback_model} also failed: {fallback_error}", file=sys.stderr)
                    continue
        
        # If all models fail, return error message
        print(f"Error: All models failed to generate question. Last error: {e}", file=sys.stderr)
        sys.exit(1)


def get_answer(client, question, model=DEFAULT_MODEL, max_tokens=DEFAULT_MAX_TOKENS, debug=False):
    """
    Get an answer to the given question from the AI model.
    
    This function takes a question and prompts the AI to provide a comprehensive
    answer. Uses moderate temperature for balanced creativity and accuracy.
    Includes the same fallback logic as question generation.
    
    Args:
        client (OpenAI): Authenticated OpenAI client instance
        question (str): The question to answer
        model (str): Model name to use for generating the answer
        max_tokens (int): Maximum tokens for the generated answer
        debug (bool): Whether to show debug output for troubleshooting
    
    Returns:
        tuple: (answer_text, actual_model_used)
               answer_text (str): The generated answer
               actual_model_used (str): Model that successfully generated the response
    
    Note:
        Uses moderate temperature (0.7) for balanced accuracy and creativity.
        Automatically falls back to gpt-4o if the primary model fails.
    """
    logger = logging.getLogger('askgpt')
    logger.info(f"Getting answer using model: {model} (question length: {len(question)} chars)")
    
    try:
        response = create_chat_completion(
            client=client,
            model=model,
            messages=[{"role": "user", "content": question}],
            max_tokens=max_tokens,
            temperature=0.7  # Moderate temperature for balanced response
        )
        answer = response.choices[0].message.content.strip()
        
        # Validate response quality - check for empty or too short responses
        if not answer or len(answer) < 10:
            logger.warning(f"Model {model} returned short/empty answer: '{answer}'")
            if debug:
                print(f"Warning: Model {model} returned an empty or very short response", file=sys.stderr)
                print(f"Response received: '{answer}'", file=sys.stderr)
            
            # If using default model and it fails, try fallback
            if model == DEFAULT_MODEL:
                logger.info("Attempting fallback to gpt-4o for answer generation")
                if debug:
                    print("Trying with gpt-4o as fallback...", file=sys.stderr)
                return get_answer(client, question, "gpt-4o", max_tokens, debug)
        
        logger.info(f"Answer generated successfully (length: {len(answer)} chars)")
        return answer, model
    except Exception as e:
        logger.error(f"Error getting answer with {model}: {e}")
        if debug:
            print(f"Error getting answer with {model}: {e}", file=sys.stderr)
        
        # Try fallback models if current model fails
        for fallback_model in FALLBACK_MODELS:
            if fallback_model != model:  # Don't retry the same model
                try:
                    logger.info(f"Trying fallback model for answer: {fallback_model}")
                    if debug:
                        print(f"Trying fallback model: {fallback_model}", file=sys.stderr)
                    return get_answer(client, question, fallback_model, max_tokens, debug)
                except Exception as fallback_error:
                    logger.warning(f"Fallback model {fallback_model} failed for answer: {fallback_error}")
                    if debug:
                        print(f"Fallback model {fallback_model} also failed: {fallback_error}", file=sys.stderr)
                    continue
        
        # If all models fail, return error message
        logger.error(f"All models failed to generate answer. Last error: {e}")
        print(f"Error: All models failed to get answer. Last error: {e}", file=sys.stderr)
        sys.exit(1)


def print_usage(available_models=None):
    """
    Print comprehensive usage information and available models.
    
    Displays the command-line interface help text including all options,
    environment variable requirements, usage examples, and the current
    list of available models.
    
    Args:
        available_models (list, optional): List of available model names.
                                         If None, uses FALLBACK_MODELS.
    
    Note:
        This function is called when --help is specified or when the user
        needs guidance on proper script usage.
    """
    if available_models is None:
        available_models = FALLBACK_MODELS
    
    usage_text = f"""
Usage: python3 askgpt.py [OPTIONS]

askgpt - A command line interface to ChatGPT

Options:
  --random              Generate a random question and get its answer
  --topic "TOPIC"       Generate a question about a specific topic and get its answer
  --question "QUESTION" Ask a specific question directly to the model
  --model MODEL         Specify the OpenAI model to use (default: {DEFAULT_MODEL})
  --question-tokens N   Maximum tokens for question generation (default: {DEFAULT_MAX_TOKENS})
  --answer-tokens N     Maximum tokens for answer generation (default: {DEFAULT_MAX_TOKENS})
  --debug               Enable debug output showing warnings and fallback attempts
  --help, -h            Show this help message

Available Models:
"""
    for model in available_models:
        marker = " (default)" if model == DEFAULT_MODEL else ""
        usage_text += f"  - {model}{marker}\n"
    
    usage_text += """
Environment Variables:
  OPENAI_API_KEY        Your OpenAI API key (required)

Examples:
  python3 askgpt.py --random
  python3 askgpt.py --topic "artificial intelligence"
  python3 askgpt.py --question "What are the benefits of renewable energy?"
  python3 askgpt.py --topic "cooking" --model gpt-4o-mini
  python3 askgpt.py --random --question-tokens 256 --answer-tokens 1024
"""
    print(usage_text)


def main():
    """
    Main function to handle command line arguments and execute the appropriate action.
    
    This function orchestrates the entire program flow:
    1. Parse command line arguments
    2. Discover available models from OpenAI API
    3. Validate user input and configuration
    4. Generate questions and answers based on user preferences
    5. Handle errors and provide fallback mechanisms
    
    The function implements the core logic for both random question generation
    and topic-specific question generation, with comprehensive error handling
    and user feedback.
    
    Raises:
        SystemExit: On various error conditions (missing API key, invalid
                   arguments, API failures, etc.)
    """
    # Parse arguments first to check for debug mode
    parser = argparse.ArgumentParser(
        description="askgpt - A command line interface to ChatGPT",
        add_help=False  # We'll handle help manually to include model list
    )
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    # Add other arguments for initial parsing
    parser.add_argument('--random', action='store_true')
    parser.add_argument('--topic')
    parser.add_argument('--question')
    parser.add_argument('--model', default=DEFAULT_MODEL)
    parser.add_argument('--question-tokens', type=int, default=DEFAULT_MAX_TOKENS)
    parser.add_argument('--answer-tokens', type=int, default=DEFAULT_MAX_TOKENS)
    parser.add_argument('--help', '-h', action='store_true')
    
    # Parse args to get debug flag early
    args = parser.parse_args()
    
    # Set up logging based on debug flag
    logger = setup_logging(debug=args.debug)
    logger.info("=== askgpt session started ===")
    logger.info(f"Command line arguments: {' '.join(sys.argv[1:])}")
    
    # Seed random number generator for better randomness across sessions
    # This ensures different questions each time the script runs
    random.seed()
    
    # Configure argument parser with custom help handling
    parser = argparse.ArgumentParser(
        description="askgpt - A command line interface to ChatGPT",
        add_help=False  # Disable default help to provide custom help with model list
    )
    
    # Define command line arguments with comprehensive help text
    parser.add_argument('--random', action='store_true',
                       help='Generate a random question and get its answer')
    parser.add_argument('--topic', type=str,
                       help='Generate a question about a specific topic and get its answer')
    parser.add_argument('--question', type=str,
                       help='Ask a specific question directly to the model')
    parser.add_argument('--model', type=str, default=DEFAULT_MODEL,
                       help=f'Specify the OpenAI model to use (default: {DEFAULT_MODEL})')
    parser.add_argument('--question-tokens', type=int, default=DEFAULT_MAX_TOKENS,
                       help=f'Maximum tokens for question generation (default: {DEFAULT_MAX_TOKENS})')
    parser.add_argument('--answer-tokens', type=int, default=DEFAULT_MAX_TOKENS,
                       help=f'Maximum tokens for answer generation (default: {DEFAULT_MAX_TOKENS})')
    parser.add_argument('--help', '-h', action='store_true',
                       help='Show this help message')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug output showing warnings and fallback attempts')
    
    args = parser.parse_args()
    
    # Dynamically fetch available models from OpenAI API
    # This ensures we always have the latest model list
    available_models = fetch_available_models()
    if not available_models:
        # Only show warning in debug mode to keep output clean
        if args.debug:
            print("Warning: Could not fetch models from API, using fallback list", file=sys.stderr)
        available_models = FALLBACK_MODELS
    
    # Handle help request with current model list
    if args.help:
        print_usage(available_models)
        return
    
    # Validate that the requested model is available
    if args.model not in available_models:
        print(f"Error: Invalid model '{args.model}'. Available models:", file=sys.stderr)
        for model in available_models:
            print(f"  - {model}", file=sys.stderr)
        sys.exit(1)
    
    # Validate token count parameters
    if args.question_tokens <= 0 or args.answer_tokens <= 0:
        print("Error: Token counts must be positive integers", file=sys.stderr)
        sys.exit(1)
    
    # Ensure user specified one of the operation modes
    operation_count = sum([args.random, bool(args.topic), bool(args.question)])
    if operation_count == 0:
        print("Error: You must specify one of --random, --topic, or --question", file=sys.stderr)
        print("Use --help for usage information", file=sys.stderr)
        sys.exit(1)
    
    # Prevent conflicting operation modes
    if operation_count > 1:
        print("Error: Cannot specify multiple operation modes (--random, --topic, --question)", file=sys.stderr)
        sys.exit(1)
    
    # Initialize authenticated OpenAI client
    client = get_openai_client()
    
    try:
        # Determine the question to ask based on the operation mode
        if args.question:
            # === DIRECT QUESTION MODE ===
            # User provided the question directly, no generation needed
            logger.info("Using direct question mode")
            question = args.question
            question_model = "user-provided"
            print(f"Question: {question}")
        else:
            # === QUESTION GENERATION PHASE ===
            if args.random:
                # Generate a question on any random topic
                logger.info("Using random question generation mode")
            else:
                # Generate a question about a specific topic
                logger.info(f"Using topic-based question generation mode: '{args.topic}'")
            
            print("Generating question...")
            if args.random:
                # Generate a question on any random topic
                question, question_model = generate_question(
                    client, 
                    model=args.model, 
                    max_tokens=args.question_tokens, 
                    debug=args.debug
                )
            else:
                # Generate a question focused on the specified topic
                question, question_model = generate_question(
                    client, 
                    topic=args.topic, 
                    model=args.model, 
                    max_tokens=args.question_tokens, 
                    debug=args.debug
                )
            
            # Display the generated question with model attribution
            print(f"Question (via {question_model}): {question}")
        
        # === ANSWER GENERATION PHASE ===
        print("\nGenerating answer...")
        answer, answer_model = get_answer(
            client, 
            question, 
            model=args.model, 
            max_tokens=args.answer_tokens, 
            debug=args.debug
        )
        
        # Display the generated answer with model attribution
        print(f"Answer (via {answer_model}): {answer}")
        
        logger.info("=== askgpt session completed successfully ===")
        
    except KeyboardInterrupt:
        # Handle user interruption gracefully
        logger.info("Session cancelled by user")
        print("\nOperation cancelled by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        # Handle any unexpected errors with informative message
        logger.error(f"Unexpected error: {e}")
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    # Entry point - run main function when script is executed directly
    main()