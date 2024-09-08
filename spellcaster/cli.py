import argparse

from spellcaster.config import FILE_TYPES
from spellcaster.traverse_repo import get_file_paths


def main():
    parser = argparse.ArgumentParser(
        description="Scan a directory and optionally specify an LLM provider."
    )
    parser.add_argument(
        "-d", "--directory", type=str, required=True, help="The directory to scan"
    )
    parser.add_argument(
        "-l",
        "--llm_provider",
        type=str,
        default="default_provider",
        choices=["claude", "sonnet", "3.5", "gpt4o", "gpt4", "gpt3.5"],
        help="The LLM provider to use (optional)",
    )

    args = parser.parse_args()

    directory = args.directory
    llm_provider = args.llm_provider

    file_paths = get_file_paths(directory, FILE_TYPES)

    # ... existing code ...
    print(f"Scanning directory: {directory}")
    print(f"Using LLM provider: {llm_provider}")
    print(f"Found {len(file_paths)} files in the directory:")
    for path in file_paths:
        print(path)
    # ... existing code ...


if __name__ == "__main__":
    main()
