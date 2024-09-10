# Spellcaster

<p align="center">
  <img src="assets/spellcasterlogo.png" alt="Spellcaster Logo" width="300"/>
</p>

_AI-powered documentation and code quality enhancement for your repositories._

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/release/python-3100/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Spellcaster is an open-source tool that leverages AI agents to enhance the quality of your codebase by scanning repositories for grammar, spelling, and code example errors in documentation files. It reads through your repository and identifies potential issues, helping you fix them with ease.

## Features

* Grammar and Spelling Checks: Spellcaster reviews your documentation and comments to ensure they are clear, correct, and professional.
* Comprehensive File Scanning: Spellcaster reads across multiple file formats (Markdown, plain text, etc.) to detect issues.

## Installation

1. Install package:

   ```bash
   pip install spellcaster
   ```

2. Set up environment variables:

   Create a `.env` file in your project root and add the following variables:

   ```
   AGENTOPS_API_KEY=your_agentops_api_key
   ANTHROPIC_API_KEY=your_anthropic_api_key
   OPENAI_API_KEY=your_openai_api_key
   GROQ_API_KEY=your_groq_api_key
   ```

Spellcaster uses AgentOps for cost and latency tracking. You can sign up for an API key [here](https://app.agentops.ai/).

Replace `your_*_api_key` with your actual API keys for each service. The model can be selected in `config.py`. Spellcaster uses LiteLLM.

### Usage

To run Spellcaster on a directory:

1. In your terminal, run the following command:

   ```bash
   spellcaster --url <path-to-your-repo-on-github>
   ```

2. Spellcaster will analyze the directory and output any detected issues, along with suggestions for fixing them.

### Configuration

You can customize Spellcaster's behavior by adjusting the `config.py` file:

- `FILE_TYPES`: A list of file extensions to scan. By default, it includes `.mdx` and `.md` files. You can add or remove file extensions as needed.
- `MAX_FILES`: The maximum number of files to scan. By default, it's set to 500. You can change this number to suit your needs.
