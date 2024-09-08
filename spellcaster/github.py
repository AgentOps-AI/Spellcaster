from git import Repo

def clone_repository(repo_url: str, target_directory: str) -> str:
    """
    Clone a GitHub repository to the specified directory.

    Args:
    repo_url (str): The URL of the GitHub repository to clone.
    target_directory (str): The directory where the repository should be cloned.

    Returns:
    str: The path to the cloned repository.
    """
    try:
        Repo.clone_from(repo_url, target_directory)
        return target_directory
    except Exception as e:
        print(f"Error cloning repository: {e}")
        return ""

if __name__ == "__main__":
    repo_url = "https://github.com/example/repo.git"
    target_dir = "/path/to/clone/directory"
    
    cloned_repo_path = clone_repository(repo_url, target_dir)
    if cloned_repo_path:
        project_dir = cloned_repo_path
        file_types = [".mdx", ".md"]  # Add or remove file extensions as needed

        file_paths = get_file_paths(project_dir, file_types)

        print(f"Found {len(file_paths)} files (max {MAX_FILES}):")
        for path in file_paths:
            print(path)