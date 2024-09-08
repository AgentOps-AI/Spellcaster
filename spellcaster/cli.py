import argparse

from spellcaster.config import FILE_TYPES
from spellcaster.traverse_repo import get_file_paths

from spellcaster.grammar_check import check_grammar_with_claude, display_results
import concurrent.futures

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

    print(f"Scanning directory: {directory}")
    print(f"Using LLM provider: {llm_provider}")
    print(f"Found {len(file_paths)} files in the directory:")

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(check_grammar_with_claude, file_path) for file_path in file_paths]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())

    for result in results:
        display_results(result)

if __name__ == "__main__":
    main()
