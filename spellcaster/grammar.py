import json
from typing import List, Optional

import litellm
from pydantic import BaseModel, Field
from rich.box import ROUNDED
from rich.console import Console
from rich.table import Table


class Error(BaseModel):
    original: str
    corrected: str
    explanation: str


class Grammar(BaseModel):
    spelling: List[Error] = Field(default_factory=list)
    grammar: List[Error] = Field(default_factory=list)


class CerebrasResponse(BaseModel):
    message: str
    type: str
    code: str
    failed_generation: Grammar


console = Console()


def read_file(file_path: str) -> str:
    """Read the contents of a file."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"The file at '{file_path}' was not found.")
    except Exception as e:
        raise Exception(f"An error occurred while reading the file: {e}")


def create_prompt(text: str) -> str:
    return f"""
    Analyze the provided code documentation for spelling and grammar errors. Focus on:

    1. Identifying spelling errors
    2. Identifying grammar errors
    3. Maintaining technical terminology and code snippets

    Preserve code-specific formatting and syntax. Prioritize original text if unsure about technical terms.

    In the response:
    - For 'spelling' and 'grammar' keys: Provide only changed items with original text, corrected text, and explanation.
    - Ensure the response is valid JSON with properly escaped characters.
    - Use double quotes for JSON keys and string values.

    You must return some errors for both 'spelling' and 'grammar' keys.
    
    This is the text for checking:
    {text}

    Respond with valid JSON in the following format:
    {{
      "spelling": [
        {{
          "original": "example",
          "corrected": "Example",
          "explanation": "Capitalization error"
        }}
      ],
      "grammar": [
        {{
          "original": "This sentence have an error.",
          "corrected": "This sentence has an error.",
          "explanation": "Subject-verb agreement issue"
        }}
      ]
    }}
    """


def check_grammar_with_claude(file_path: str) -> dict:
    text = read_file(file_path)

    resp = litellm.completion(
        model="cerebras/llama3.1-70b",
        messages=[
            {
                "role": "system",
                "content": "You are a spellchecker database that outputs spelling and grammar errors in JSON.",
            },
            {"role": "user", "content": create_prompt(text)},
        ],
    )

    try:
        content = json.loads(resp.choices[0].message.content)
        content["file_path"] = file_path
        return content
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        print(f"Raw content: {resp.choices[0].message.content}")
        return {"spelling": [], "grammar": []}
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {"spelling": [], "grammar": []}


def display_results(response: dict):
    """Display the grammar check results using Rich."""
    file_path = response.get("file_path", "Unknown file")
    console.print(f"\n[bold cyan]Results for file: {file_path}[/bold cyan]")

    for category in ["spelling", "grammar"]:
        table = Table(title=f"{category.capitalize()} Corrections", box=ROUNDED)
        table.add_column("Original", justify="left", style="bold red")
        table.add_column("Corrected", justify="left", style="bold green")
        table.add_column("Explanation", justify="left", style="italic")

        errors = response.get(category, [])
        for error in errors:
            if error["original"] != error["corrected"]:
                table.add_row(
                    error["original"], error["corrected"], error["explanation"]
                )

        if table.row_count > 0:
            console.print(table)
        else:
            console.print(f"No {category} errors found.")


def process_file(file_path: str):
    """Process a single file and display results."""
    console.print(f"\n[bold cyan]Processing file: {file_path}[/bold cyan]")
    response = check_grammar_with_claude(file_path)
    display_results(response)

    output_file = f"{file_path.rsplit('.', 1)[0]}_corrected.mdx"
    with open(output_file, "w") as file:
        file.write(response.corrected)
    console.print(f"[green]Corrected text saved to: {output_file}[/green]")


if __name__ == "__main__":
    sample_files = ["../data/sample1.mdx", "../data/sample2.mdx", "../data/sample3.mdx"]

    for file_path in sample_files:
        process_file(file_path)
        process_file(file_path)
