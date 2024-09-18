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
