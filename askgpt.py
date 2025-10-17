#!/usr/bin/env python3
"""
askgpt - A command line interface to ChatGPT

This script allows you to interact with OpenAI's language models in various ways:
- Generate random questions and get answers
- Ask questions about specific topics
- Customize model and token limits
"""

import argparse
import os
import random
import sys
from openai import OpenAI

DEFAULT_MODEL = "gpt-5"

# Fallback models in case API fetch fails
FALLBACK_MODELS = [
    "gpt-5",
    "gpt-4o",
    "gpt-4o-mini", 
    "gpt-4-turbo",
    "gpt-4",
    "gpt-3.5-turbo"
]


def fetch_available_models():
    """Fetches the list of available models from the OpenAI API."""
    try:
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        models = client.models.list()
        model_names = [model.id for model in models]
        return model_names
    except Exception as e:
        print(f"Error fetching models: {e}")
        return []
DEFAULT_MAX_TOKENS = 512


def get_openai_client():
    """Initialize and return OpenAI client using API key from environment."""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)
    
    return OpenAI(api_key=api_key)


def uses_max_completion_tokens(model):
    """Check if a model uses max_completion_tokens instead of max_tokens."""
    newer_model_prefixes = ['gpt-5', 'gpt-4o', 'o1', 'o3', 'o4', 'gpt-4.1']
    return any(model.startswith(prefix) for prefix in newer_model_prefixes)


def supports_custom_temperature(model):
    """Check if a model supports custom temperature values."""
    # Some newer models only support default temperature (1.0)
    restricted_models = ['gpt-5', 'o1', 'o3', 'o4']
    return not any(model.startswith(prefix) for prefix in restricted_models)


def create_chat_completion(client, model, messages, max_tokens, temperature):
    """Create a chat completion with the appropriate parameters for the model."""
    # Prepare base parameters
    params = {
        'model': model,
        'messages': messages
    }
    
    # Add token limit parameter (different for newer models)
    if uses_max_completion_tokens(model):
        params['max_completion_tokens'] = max_tokens
    else:
        params['max_tokens'] = max_tokens
    
    # Add temperature parameter only if supported
    if supports_custom_temperature(model):
        params['temperature'] = temperature
    
    return client.chat.completions.create(**params)


def generate_question(client, topic=None, model=DEFAULT_MODEL, max_tokens=DEFAULT_MAX_TOKENS, debug=False):
    """Generate a question, optionally about a specific topic."""
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
        
        # Check if the response is empty or too short
        if not question or len(question) < 10:
            if debug:
                print(f"Warning: Model {model} returned an empty or very short response", file=sys.stderr)
                print(f"Response received: '{question}'", file=sys.stderr)
            if model == DEFAULT_MODEL:
                if debug:
                    print("Trying with gpt-4o as fallback...", file=sys.stderr)
                return generate_question(client, topic, "gpt-4o", max_tokens, debug)
        
        return question, model
    except Exception as e:
        print(f"Error generating question: {e}", file=sys.stderr)
        sys.exit(1)


def get_answer(client, question, model=DEFAULT_MODEL, max_tokens=DEFAULT_MAX_TOKENS, debug=False):
    """Get an answer to the given question."""
    try:
        response = create_chat_completion(
            client=client,
            model=model,
            messages=[{"role": "user", "content": question}],
            max_tokens=max_tokens,
            temperature=0.7
        )
        answer = response.choices[0].message.content.strip()
        
        # Check if the response is empty or too short
        if not answer or len(answer) < 10:
            if debug:
                print(f"Warning: Model {model} returned an empty or very short response", file=sys.stderr)
                print(f"Response received: '{answer}'", file=sys.stderr)
            if model == DEFAULT_MODEL:
                if debug:
                    print("Trying with gpt-4o as fallback...", file=sys.stderr)
                return get_answer(client, question, "gpt-4o", max_tokens, debug)
        
        return answer, model
    except Exception as e:
        print(f"Error getting answer: {e}", file=sys.stderr)
        sys.exit(1)


def print_usage(available_models=None):
    """Print usage information and available models."""
    if available_models is None:
        available_models = FALLBACK_MODELS
    
    usage_text = f"""
Usage: python3 askgpt.py [OPTIONS]

askgpt - A command line interface to ChatGPT

Options:
  --random              Generate a random question and get its answer
  --topic "TOPIC"       Generate a question about a specific topic and get its answer
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
  python3 askgpt.py --topic "cooking" --model gpt-4o-mini
  python3 askgpt.py --random --question-tokens 256 --answer-tokens 1024
"""
    print(usage_text)


def main():
    """Main function to handle command line arguments and execute the appropriate action."""
    # Seed random number generator for better randomness
    random.seed()
    
    parser = argparse.ArgumentParser(
        description="askgpt - A command line interface to ChatGPT",
        add_help=False  # We'll handle help ourselves
    )
    
    parser.add_argument('--random', action='store_true',
                       help='Generate a random question and get its answer')
    parser.add_argument('--topic', type=str,
                       help='Generate a question about a specific topic and get its answer')
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
    
    # Fetch available models from OpenAI API
    available_models = fetch_available_models()
    if not available_models:
        if args.debug:
            print("Warning: Could not fetch models from API, using fallback list", file=sys.stderr)
        available_models = FALLBACK_MODELS
    
    # Handle help
    if args.help:
        print_usage(available_models)
        return
    
    # Validate model
    if args.model not in available_models:
        print(f"Error: Invalid model '{args.model}'. Available models:", file=sys.stderr)
        for model in available_models:
            print(f"  - {model}", file=sys.stderr)
        sys.exit(1)
    
    # Validate token counts
    if args.question_tokens <= 0 or args.answer_tokens <= 0:
        print("Error: Token counts must be positive integers", file=sys.stderr)
        sys.exit(1)
    
    # Check if either --random or --topic is specified
    if not args.random and not args.topic:
        print("Error: You must specify either --random or --topic", file=sys.stderr)
        print("Use --help for usage information", file=sys.stderr)
        sys.exit(1)
    
    # Both --random and --topic cannot be specified
    if args.random and args.topic:
        print("Error: Cannot specify both --random and --topic", file=sys.stderr)
        sys.exit(1)
    
    # Initialize OpenAI client
    client = get_openai_client()
    
    try:
        # Generate question
        print("Generating question...")
        if args.random:
            question, question_model = generate_question(client, model=args.model, max_tokens=args.question_tokens, debug=args.debug)
        else:
            question, question_model = generate_question(client, topic=args.topic, model=args.model, max_tokens=args.question_tokens, debug=args.debug)
        
        print(f"Question (via {question_model}): {question}")
        
        # Get answer
        print("\nGenerating answer...")
        answer, answer_model = get_answer(client, question, model=args.model, max_tokens=args.answer_tokens, debug=args.debug)
        
        print(f"Answer (via {answer_model}): {answer}")
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()