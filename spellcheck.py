from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
import os
import requests
import base64

# Ensure Anthropic API key is set
api_key = os.environ.get('anthropicsecret')
if not api_key:
    raise ValueError("Please set the 'anthropicsecret' environment variable.")

anthropic = Anthropic(api_key=api_key)

def get_github_file_content(url):
    # Extract owner, repo, and file path from the URL
    parts = url.split('/')
    owner, repo = parts[3], parts[4]
    file_path = '/'.join(parts[7:])

    # Construct the GitHub API URL
    api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"

    # Send a GET request to the GitHub API
    response = requests.get(api_url)
    response.raise_for_status()

    # Decode the content
    content = base64.b64decode(response.json()['content']).decode('utf-8')
    return content

def spell_check_document(document):
    prompt = f"{HUMAN_PROMPT}Please carefully review the following document and identify any spelling errors. Provide a list of misspelled words and their corrections in the format 'misspelled_word: correct_word'. If there are no spelling errors, state 'No spelling errors found.'\n\nDocument: {document}\n{AI_PROMPT}"
    
    response = anthropic.completions.create(
        model="claude-2",
        max_tokens_to_sample=1000,
        prompt=prompt
    )
    
    return response.completion

# Example texts with varying levels of spelling errors
mild_errors = """
The company's anual report showed significant growth in the tecnology sector. 
Despite some challanges, they managed to achive their goals and expand their 
customer base. The CEO emphasized the importence of innovation and continous 
improvement in their products and services.
"""

moderate_errors = """
The resturant recieved excelent reviews for its uniqe cuisine and athmosphere. 
The chef's signture dishes were particullarly praised for thier exquisite flavors 
and creative presentasion. Customers also apreciated the freindly service and 
cozy ambiance of the dinning area.
"""

severe_errors = """
The sientist's grounbreaking reserch on klimat chang has atracted considerble 
atention from the akademic comunity. Her hipothesis chalenges convenshional 
wisdom and proposes inovative solutons to mitigat the efects of globel worming. 
The studdy's metodology and findins have been widly debated in recent confrenzes.
"""

# Example usage
if __name__ == '__main__':
    print("Checking mild errors:")
    result = spell_check_document(mild_errors)
    print(result)

    print("\nChecking moderate errors:")
    result = spell_check_document(moderate_errors)
    print(result)

    print("\nChecking severe errors:")
    result = spell_check_document(severe_errors)
    print(result)

    # Original GitHub file check
    github_url = "https://github.com/mintlify/docs/blob/main/code.mdx"
    try:
        mdx_content = get_github_file_content(github_url)
        print("\nChecking GitHub MDX file:")
        result = spell_check_document(mdx_content)
        print(result)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
