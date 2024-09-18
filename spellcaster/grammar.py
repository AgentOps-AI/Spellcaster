import json
from pydantic import BaseModel
from rich.console import Console
from rich.table import Table
from rich.box import ROUNDED
import litellm
from agentops import record_action
from agentops import ErrorEvent, record, ActionEvent


class Error(BaseModel):
    before: str
    after: str
    explanation: str


class Grammar(BaseModel):
    spelling: list[Error]
    punctuation: list[Error]
    grammar: list[Error]
    file_path: str


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


def create_prompt(text: str, proper_nouns: str) -> str:
    return f"""
    Rewrite the provided code documentation to be clear and grammatically correct while preserving technical accuracy. Focus on:

    1. Correcting spelling, punctuation, and grammar errors
    2. Maintaining technical terminology and code snippets
    3. Ensuring consistent tense, voice, and formatting
    4. Clarifying function descriptions, parameters, and return values
    5. Proper use of capitalization, acronyms, and abbreviations
    6. Improving clarity and conciseness
    7. Respect markdown and MDX conventions such as underscores, asterisks, backticks, code blocks, and links. A lot of text is going to be formatted with backticks, underscores, and asterisks because it's code documentation. For example, you might see the `Events`, and the backticks should stay there because it's markdown formatting. Make sure you respect markdown formatting.
    8. Documentation will frequently include proper nouns and acronyms. Ensure that they are correctly spelled and capitalized.
    
    Here's a list of proper nouns you may encounter:
    {proper_nouns}

    Preserve code-specific formatting and syntax. Prioritize original text if unsure about technical terms.

    Make sure when you show the before vs after text, include a larger phrase or sentence. This makes it easier to understand the context of what is correct.

    In the response:
    - For 'spelling', 'punctuation', and 'grammar' keys: Provide only changed items with original text, corrected text, and explanation.
    
    Ensure that the original text is actually referenced from the given text below:

    {text}
    """


@record_action("check_grammar")
def check_grammar(file_path: str, proper_nouns: str, model: str) -> Grammar:
    """Check grammar of the text in the provided file using Claude."""
    text = read_file(file_path)

    resp = litellm.completion(
        model=model,
        # response_format={"type": "json_object"},
        num_retries=5,
        messages=[
            {
                "role": "system",
                "content": "You are a spellchecker database that outputs grammars errors and corrected text in JSON.\n"
                f" The JSON object must use the schema: {json.dumps(Grammar.model_json_schema(), indent=2)}\n"
                "It is strictly imperative that you return as JSON. DO NOT return any other characters other than valid JSON as your response."
            },
            {
                "role": "user",
                "content": create_prompt(text, proper_nouns)
            }
        ]
    )

    try:
        text_response = resp.choices[0].message.content
        resp = Grammar.model_validate_json(text_response)

        # Double check reasoning
        validated_response = validate_reasoning(resp.json(), model=model)

        if validated_response is False:
            print("The reasoning was incorrect. Returning the original text.")

            return Grammar(spelling=[], punctuation=[], grammar=[], file_path=file_path)

        resp.file_path = file_path

        return resp
    except Exception as e:
        console.print(f"[bold yellow]Warning: No corrections found or unable to format LLM response.[/bold yellow]")
        action_event = ActionEvent()
        record(ErrorEvent(exception=e, trigger_event=action_event))
        return Grammar(spelling=[], punctuation=[], grammar=[], file_path=file_path)


@record_action("validate_reasoning")
def validate_reasoning(text: str, model: str) -> bool:
    """Validate the reasoning of the provided text."""
    resp = litellm.completion(
        model=model,
        # response_format={"type": "json_object"},
        num_retries=5,
        messages=[
            {
                "role": "system",
                "content": """You are a reviewer agent. You've been tasked with reviewing the corrections and suggestions of someone else. The problem is they don't always make sense, and could use a second pair of eyes to just make sure they reasoned abotu the problem correctly. Your job is to follow their reasoning steps and think step by step to resolve whether they are correct in their suggestions. Here's some examples:


                Example where the reasoning is correct:
                ```
                Original
                
                To get the most out of AgentOps, it is best to carefully consider what events to record - For example, if you decorate a function that makes several openai calls, then each openai call will show in the replay graph as a child of the decorated function.
    
                Corrected
                
                To get the most out of AgentOps, it is best to carefully consider what events to record.
                
                For example, if you decorate a function that makes several OpenAI calls, then each OpenAI call will show in the replay graph as a child of the decorated function.

                Explanation
                
                Removed unnecessary dash.
                Proper noun capitalization (OpenAI).
                ```

                Result:
                ```
                The reasoning is correct here in both cases. The unnecessary dash seems like an typo and is not needed, even though dashes are common in markdown files. There's no reason to believe this was intended syntax.

                The proper noun capitalization is correct. OpenAI should be capitalized instead of just openai

                Conclustion:
                The results are correct.

                **VALID**
                ```

                Example of where the reasoning is incorrect:

                ```
                Original
                
                The 'completion', 'embedding', and 'image_generation' endpoints

                Corrected
                
                the completion, embedding, and image generation endpoints

                Explanation
                
                Added indefinite article "the" before the endpoints for a proper noun phrase.
                ```

                Result:
                ```
                The reasoning is incorrect here because the endpoints were intended to be strings within single quotes. However, the quotes were removed, and the endpoints were not intended to be proper nouns.                

                Conclustion:
                The results are incorrect.

                **INVALID**    
                
                """
                f" The JSON object must use the schema: {json.dumps(Grammar.model_json_schema(), indent=2)}. Filter out the content that is INVALID.\n"
                "It is strictly imperative that you return as JSON. DO NOT return any other characters other than valid JSON as your response."
            },
            {
                "role": "user",
                "content": text
            }
        ]
    )
    text_response = resp.choices[0].message.content

    if "INVALID" in text_response:
        return False
    return True


def display_results(response: Grammar, path: str, repo_link: str = ""):
    """Display the grammar check results using Rich."""
    # Replace local file path with GitHub URL
    if repo_link:
        path = repo_link.rstrip('/') + '/blob/main/' + \
            '/'.join(response.file_path.split("samples/")[1].split('/')[2:])
    # Create a console for file output
    console = Console(record=True)

    console.print(f"\n[bold cyan]File: {path}[/bold cyan]")

    total_errors = 0

    for category in ['spelling', 'punctuation', 'grammar']:
        table = Table(title=f"{category.capitalize()} Corrections", box=ROUNDED)
        table.add_column("Original", justify="left", style="bold red")
        table.add_column("Corrected", justify="left", style="bold green")
        table.add_column("Explanation", justify="left", style="italic")

        errors = getattr(response, category)
        for error in errors:
            if error.before != error.after:
                table.add_row(error.before, error.after, error.explanation)
                table.add_row("", "", "")  # Add an empty row for spacing
                total_errors += 1

        if table.row_count > 0:
            console.print(table)
        else:
            no_errors_msg = f"No {category} errors found."
            console.print(no_errors_msg)

    console.print(f"[bold red]Total errors found: {total_errors}[/bold red]")

    with open("output.txt", "w") as f:
        f.write(console.export_text())

    return total_errors
