import os
import argparse
import agentops
from spellcaster.config import FILE_TYPES
from spellcaster.traverse_repo import get_file_paths
from spellcaster.grammar import check_grammar_with_claude, display_results
from spellcaster.github import clone_repository
import concurrent.futures
import tempfile
import shutil
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()


def main():
    agentops.init(os.environ.get("AGENTOPS_API_KEY"))

    parser = argparse.ArgumentParser(
        description="Scan a directory or GitHub repository and optionally specify an LLM provider."
    )
    parser.add_argument(
        "-d", "--directory", type=str, help="The directory to scan"
    )
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
        data_dir = Path.home() / "data" / "spellcaster_repos"
        data_dir.mkdir(parents=True, exist_ok=True)
        repo_name = args.url.split("/")[-1].replace(".git", "")
        directory = data_dir / repo_name
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
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(check_grammar_with_claude, file_path) for file_path in file_paths]
        for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
            result = future.result()
            results.append(result)
            print(f"Processed file {i}/{len(futures)}: {result['file_path']}")

    print("\nGrammar check results:")
    for result in results:
        display_results(result)

    print("Grammar check completed.")
    agentops.end_session('Success')


if __name__ == "__main__":
    main()
