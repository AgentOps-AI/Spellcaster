# Spellcaster

**Spellcaster** is an open-source tool that leverages AI agents to enhance the quality of your codebase by scanning repositories for grammar, spelling, and code example errors in documentation files. It reads through your repository and identifies potential issues, helping you fix them with ease.

## Features

- **Grammar and Spelling Checks**: Spellcaster reviews your documentation and comments to ensure they are clear, correct, and professional.
- **Code Example Validation**: It checks embedded code snippets in documentation for syntax errors and inconsistencies.
- **Comprehensive File Scanning**: Spellcaster reads across multiple file formats (Markdown, plain text, etc.) to detect issues.
- **Automated Fixes**: After identifying problems, Spellcaster offers suggestions and can even apply fixes automatically.

## Getting Started

### Prerequisites

- Python 3.8 or later
- OpenAI API Key (optional)
- Claude API key (optional)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/areibman/spellcaster.git
   ```

2. Navigate to the project directory:
   ```bash
   cd spellcaster
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Usage

To run Spellcaster on your repository:

1. In your terminal, run the following command:
   ```bash
   python spellcaster.py <path-to-your-repo>
   ```

2. Spellcaster will analyze the repository and output any detected issues, along with suggestions for fixing them.

### Configuration

You can customize Spellcaster’s behavior by adjusting the `config.yaml` file:

- Set file types to scan (e.g., `.md`, `.txt`, `.py`).
- Define directories to include/exclude in the scan.
- Enable/disable automatic fixes.

## Contributing

We welcome contributions! If you’d like to help improve Spellcaster:

1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature-branch
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add your feature"
   ```
4. Push to the branch:
   ```bash
   git push origin feature-branch
   ```
5. Open a pull request.

## Roadmap

- Add support for more programming languages.
- Expand error-checking to include more types of code validations.
- Create a plugin for popular IDEs.
- Improve suggestions for complex grammatical errors.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Feel free to adjust this according to your preferences!
