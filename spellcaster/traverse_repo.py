import os
from typing import List


class GitHubFileLocator:
    def __init__(self, project_directory: str, file_types: List[str]):
        self.project_directory = project_directory
        self.file_types = file_types

    def find_files(self) -> List[str]:
        """
        Scrape the project directory for specified file types and return their paths.
        """
        files_to_process = []
        allowed_extensions = set(ext.lower() for ext in self.file_types)

        for root, _, files in os.walk(self.project_directory):
            for file in files:
                file_extension = os.path.splitext(file)[1].lower()
                if file_extension in allowed_extensions:
                    files_to_process.append(os.path.join(root, file))

        return files_to_process


def get_file_paths(project_directory: str, file_types: List[str]) -> List[str]:
    """
    Main function to get file paths based on the file types.
    """
    locator = GitHubFileLocator(project_directory, file_types)
    return locator.find_files()


# Example usage:
if __name__ == "__main__":
    project_dir = "/Users/benedictneo/usf/msds692"

    # List of file types to include
    file_types = [".mdx", ".md"]  # Add or remove file extensions as needed

    file_paths = get_file_paths(project_dir, file_types)

    print(f"Found {len(file_paths)} files:")
    for path in file_paths:
        print(path)