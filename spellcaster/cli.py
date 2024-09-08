import argparse
import concurrent.futures
import os
import shutil
import tempfile
from pathlib import Path

import agentops
from dotenv import load_dotenv

from spellcaster.config import FILE_TYPES
from spellcaster.github import clone_repository
from spellcaster.grammar import check_grammar_with_claude, display_results
from spellcaster.traverse_repo import get_file_paths

load_dotenv()


def main():
    parser = argparse.ArgumentParser(
        description="Scan a directory or GitHub repository and optionally specify an LLM provider."
    )
    parser.add_argument("-d", "--directory", type=str, help="The directory to scan")
    parser.add_argument(
        "-u", "--url", type=str, help="The GitHub repository URL to clone and scan"
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

    if args.url:
        current_dir = Path.cwd()
        repo_name = args.url.split("/")[-1].replace(".git", "")
        directory = current_dir / "spellcaster" / "samples" / repo_name
        if directory.exists():
            print(f"Repository already exists at {directory}")
        else:
            print(f"Cloning repository from {args.url}...")
            clone_repository(args.url, str(directory))
            print(f"Repository cloned successfully to {directory}")
    elif args.directory:
        directory = args.directory
        print(f"Using existing directory: {directory}")
    else:
        parser.error("Either --directory or --url must be provided")

    llm_provider = args.llm_provider
    print(f"Using LLM provider: {llm_provider}")

    print(f"Scanning files in: {directory}")
    file_paths = get_file_paths(directory, FILE_TYPES)
    print(f"Found {len(file_paths)} files to scan")

    print("Starting grammar check...")

    agentops.init(os.environ.get("AGENTOPS_API_KEY"), tags=["spellcaster", 'agentops', 'Cerebras', 'Llama3.1-70B'])
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        futures = [
            executor.submit(check_grammar_with_claude, file_path)
            for file_path in file_paths[:10]
        ]
        for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
            result = future.result()
            results.append(result)
            print(f"Processed file {i}/{len(futures)}")

    print("\nGrammar check results:")
    for result in results:
        display_results(result)

    print("Grammar check completed.")
    agentops.end_session("Success")


if __name__ == "__main__":
    main()
if __name__ == "__main__":
    main()
