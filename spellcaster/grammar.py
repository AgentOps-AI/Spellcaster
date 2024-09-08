import json
from pydantic import BaseModel
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.text import Text

from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.box import ROUNDED
from groq import Groq
import os

load_dotenv()

class Error(BaseModel):
    before: str
    after: str
    explanation: str

class Grammar(BaseModel):
    spelling: list[Error]
    punctuation: list[Error]
    grammar: list[Error]
    corrected: str

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

console = Console()

def read_file(file_path: str) -> str:
    """Read the contents of a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"The file at '{file_path}' was not found.")
    except Exception as e:
        raise Exception(f"An error occurred while reading the file: {e}")
    

def create_prompt(text: str) -> str:
    return f"""
    Rewrite the provided code documentation to be clear and grammatically correct while preserving technical accuracy. Focus on:

    1. Correcting spelling, punctuation, and grammar errors
    2. Maintaining technical terminology and code snippets
    3. Ensuring consistent tense, voice, and formatting
    4. Clarifying function descriptions, parameters, and return values
    5. Proper use of capitalization, acronyms, and abbreviations
    6. Improving clarity and conciseness

    Preserve code-specific formatting and syntax. Prioritize original text if unsure about technical terms.

    In the response:
    - For 'spelling', 'punctuation', and 'grammar' keys: Provide only changed items with original text, corrected text, and explanation.
    - For 'corrected' key: Provide the full corrected text with all errors addressed.
    
    {text}
    """

def check_grammar_with_claude(file_path: str) -> Grammar:
    """Check grammar of the text in the provided file using Claude."""
    text = read_file(file_path)

    resp = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        max_tokens=8000,
        messages=[
             {
                "role": "system",
                "content": "You are a spellchecker database that outputs grammars errors and corrected text in JSON.\n"
                f" The JSON object must use the schema: {json.dumps(Grammar.model_json_schema(), indent=2)}",
            },
            {
                "role": "user",
                "content": create_prompt(text),
            }
        ],
        response_format={"type": "json_object"},
    )

    return Grammar.model_validate_json(resp.choices[0].message.content)

def display_results(response: Grammar):
    """Display the grammar check results using Rich."""
    for category in ['spelling', 'punctuation', 'grammar']:
        table = Table(title=f"{category.capitalize()} Corrections", box=ROUNDED)
        table.add_column("Original", justify="left", style="bold red")
        table.add_column("Corrected", justify="left", style="bold green")
        table.add_column("Explanation", justify="left", style="italic")
        
        errors = getattr(response, category)
        for error in errors:
            if error.before != error.after:
                table.add_row(error.before, error.after, error.explanation)

        if table.row_count > 0:
            console.print(table)
        else:
            console.print(f"No {category} errors found.")
    
    console.print(Text("\nCorrected Text:\n", style="bold cyan"))
    console.print(Text(response.corrected, style="white"))

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