import argparse
import agentops
from spellcaster.config import FILE_TYPES, MAX_FILES, MODEL
from spellcaster.traverse_repo import get_file_paths
from spellcaster.grammar import check_grammar, display_results
from spellcaster.github import clone_repository
import concurrent.futures
import os
from pathlib import Path
from rich.console import Console

from dotenv import load_dotenv

load_dotenv()

console = Console()


def main():
    parser = argparse.ArgumentParser(
        description="Scan a directory or GitHub repository and optionally specify an LLM provider."
    )
    parser.add_argument("-d", "--directory",
                        type=str, help="The directory to scan")
    parser.add_argument("-u", "--url",
                        type=str, help="The GitHub repository URL to clone and scan")
    parser.add_argument("-l", "--llm_provider",
                        type=str,
                        default=MODEL,
                        choices=["claude", "sonnet", "3.5", "gpt4o", "gpt4", "gpt3.5"],
                        help="The LLM provider to use (optional)",
                        )
    parser.add_argument("-p", "--proper_nouns",
                        type=str,
                        default="* Llama3.1-70B \n * Cerebras \n * Cohere \n * OpenAI \n * AgentOps \n * Spellcaster",
                        help="A string of proper nouns to include in the prompt (optional)",
                        )
    parser.add_argument("-f", "--file_types",
                        nargs="+",
                        default=FILE_TYPES,
                        help="File types to scan (default: %(default)s)",
                        )
    parser.add_argument("-m", "--max_files",
                        type=int,
                        default=MAX_FILES,
                        help="Maximum number of files to scan (default: %(default)s)",
                        )

    args = parser.parse_args()
    path = ""
    if args.url:
        path = args.url
        current_dir = Path.cwd()
        repo_name = args.url.rstrip('/').split("/")[-1].replace(".git", "")
        org = args.url.rstrip('/').split("/")[-2]
        print(repo_name)
        directory = current_dir / "spellcaster" / "samples" / org / repo_name
        print(f"Using directory: {directory}")
        if directory.exists():
            print(f"Repository already exists at {directory}")
        else:
            print(f"Cloning repository from {args.url}...")
            directory.mkdir(parents=True, exist_ok=True)  # Ensure the directory is created
            clone_repository(args.url, str(directory))
            print(f"Repository cloned successfully to {directory}")
    elif args.directory:
        path = args.directory
        directory = args.directory
        print(f"Using existing directory: {directory}")
    else:
        parser.error("Either --directory or --url must be provided")

    llm_provider = args.llm_provider
    print(f"Using LLM provider: {llm_provider}")

    file_paths = get_file_paths(directory, args.file_types, args.max_files)
    print(f"Found {len(file_paths)} files to scan")

    print("Starting grammar check...")

    agentops.init(os.environ.get("AGENTOPS_API_KEY"), default_tags=["spellcaster", 'cursor', 'Cerebras', 'gpt4o'])
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(check_grammar, file_path,
                                   proper_nouns=args.proper_nouns,
                                   model=llm_provider)
                   for file_path in file_paths]
        for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
            result = future.result()
            results.append(result)
            print(f"Processed file {i}/{len(futures)}")

    print("\nGrammar check results:")

    total = 0
    for result in results:
        errors = display_results(result, result.file_path, args.url)
        total += errors

    console.print(f"[bold red]Total errors in the docs found: {total}[/bold red]")

    print("Grammar check completed.")
    agentops.end_session("Success")


if __name__ == "__main__":
    main()
