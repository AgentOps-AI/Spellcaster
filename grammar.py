import instructor
import os
from anthropic import Anthropic
from pydantic import BaseModel
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.text import Text

from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.box import ROUNDED


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

client = instructor.from_anthropic(Anthropic())
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

    Do not include correct sentences or punctuations or unchanged text in the error lists. 

    {text}
    """

def check_grammar_with_claude(file_path: str) -> Grammar:
    """Check grammar of the text in the provided file using Claude."""
    text = read_file(file_path)
    resp = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=8192,
        messages=[
            {
                "role": "user",
                "content": create_prompt(text),
            }
        ],
        response_model=Grammar,
    )
    
    return resp

def display_results(response: Grammar):
    """Display the grammar check results using Rich."""
    for category in ['spelling', 'punctuation', 'grammar']:
        table = Table(title=f"{category.capitalize()} Corrections", box=ROUNDED)
        table.add_column("Original", justify="left", style="bold red")
        table.add_column("Corrected", justify="left", style="bold green")
        table.add_column("Explanation", justify="left", style="italic")
        
        errors = getattr(response, category)
        for error in errors:
            # Only add the row if the original and corrected text are different
            if error.before != error.after:
                table.add_row(error.before, error.after, error.explanation)

        # Only print the table if it has rows
        if table.row_count > 0:
            console.print(table)
        else:
            console.print(f"No {category} errors found.")
    
    # Display corrected text
    console.print(Text("\nCorrected Text:\n", style="bold cyan"))
    console.print(Text(response.corrected, style="white"))

if __name__ == "__main__":
    file_path = "data/test.mdx"
    response = check_grammar_with_claude(file_path)
    
    # Print the results to the console
    display_results(response)
    
    # Write the corrected text to a file
    with open("data/response.txt", "w") as file:
        file.write(response.corrected)