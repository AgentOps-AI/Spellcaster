import argparse


def main():
    parser = argparse.ArgumentParser(description="Scan a directory and optionally specify an LLM provider.")
    parser.add_argument('-d', '--directory', type=str, required=True, help='The directory to scan')
    parser.add_argument('-l', '--llm_provider', type=str, default='default_provider',
                        choices=['claude', 'sonnet', '3.5', 'gpt4o', 'gpt4', 'gpt3.5'],
                        help='The LLM provider to use (optional)')

    args = parser.parse_args()

    directory = args.directory
    llm_provider = args.llm_provider

    # ... existing code ...
    print(f"Scanning directory: {directory}")
    print(f"Using LLM provider: {llm_provider}")
    # ... existing code ...


if __name__ == "__main__":
    main()
