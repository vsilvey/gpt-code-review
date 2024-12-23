"""
Main module for handling the code review process using ChatGPT and GitHub's API.
"""

import logging
from clients.github_client import GithubClient
from clients.openai_client import OpenAIClient
from utils.helpers import get_env_variable

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    """
    Main function to handle the code review process based on the reviewer assigned and the mode specified.
    """
    try:
        env_vars = get_env_vars()
    except ValueError as e:
        logging.error("Environment variable error: %s", e)
        return

    github_client = GithubClient(env_vars['GH_TOKEN'])
    openai_client = OpenAIClient(env_vars['OPENAI_MODEL'],
                                 env_vars['OPENAI_TEMPERATURE'],
                                 env_vars['OPENAI_MAX_TOKENS'])

    pr_id = env_vars['GITHUB_PR_ID']
    reviewer = env_vars.get('GITHUB_REVIEWER', '').strip()
    oai_model = env_vars['OPENAI_MODEL']
    oai_temp = env_vars['OPENAI_TEMPERATURE']
    mode = env_vars['MODE']
    max_tokens = env_vars['OPENAI_MAX_TOKENS']


# Proceed with code review if reviewer matches most recently requested reviewer.

    if  github_client.get_most_recent_reviewer(pr_id) == reviewer:
        logging.info("Reviewer %s assigned. Starting code review.", reviewer)
        language = env_vars.get('LANGUAGE', 'en')
        custom_prompt = env_vars.get('CUSTOM_PROMPT')
        if mode == "files":
            process_files(github_client, openai_client, pr_id, language, custom_prompt, oai_model, mode, oai_temp)
        elif mode == "patch":
            process_patch(github_client, openai_client, pr_id, language, custom_prompt, oai_model, mode, oai_temp)
        else:
            logging.error("Invalid mode. Choose either 'files' or 'patch'.")
    else:
        logging.warning("No action taken. Reviewer is not %s.", reviewer)

def get_env_vars():
    """
    Retrieve required and optional environment variables and ensure they are not empty.
    Convert specific variables to their appropriate types.

    Returns:
        dict: A dictionary of environment variables.

    Raises:
        ValueError: If any required environment variable is missing, empty, or has an invalid type.
    """
    variables = {
        'OPENAI_API_KEY': (str, True),
        'GH_TOKEN': (str, True),
        'GITHUB_PR_ID': (int, True),
        'GITHUB_REVIEWER': (str, True),
        'OPENAI_MODEL': (str, True),
        'OPENAI_TEMPERATURE': (float, True),
        'OPENAI_MAX_TOKENS': (int, True),
        'MODE': (str, True),
        'LANGUAGE': (str, True),
        'CUSTOM_PROMPT': (str, False)
    }

    env_vars = {}
    for var, (var_type, required) in variables.items():
        value = get_env_variable(var, required)
        if value:
            try:
                env_vars[var] = var_type(value)
                logging.info(
                    "%s (%s) retrieved and converted successfully.",
                    var,
                    var_type.__name__
                )
            except ValueError as e:
                logging.error("%s must be of type %s. Error: %s", var, var_type.__name__, e)
                raise ValueError(f"{var} must be of type {var_type.__name__}.") from e
        else:
            env_vars[var] = None

    return env_vars

def process_files(github_client, openai_client, pr_id, language, custom_prompt, oai_model, mode, oai_temp):
    """
    Process the files changed in the last commit of the pull request.

    Args:
        github_client (GithubClient): The GitHub client instance.
        openai_client (OpenAIClient): The OpenAI client instance.
        pr_id (int): The pull request ID.
        language (str): The language for the review.
        custom_prompt (str, optional): Custom prompt for the code review.
        oai_model (str): The OpenAI model being leveraged for the review.
        mode (str): The processing mode of file or patch
        oai_temp (int): Number from 0 to 1 indicating level of creativity for OpenAI response
    """
    logging.info("Processing files for PR ID: %s", pr_id)
    pull_request = github_client.get_pr(pr_id)
    commits = list(pull_request.get_commits())

    if not commits:
        logging.info("No commits found.")
        return

    last_commit = commits[-1]
    analyze_commit_files(github_client, openai_client, pr_id, last_commit, language, custom_prompt, oai_model, mode, oai_temp)

def process_patch(github_client, openai_client, pr_id, language, custom_prompt, oai_model, mode, oai_temp):
    """
    Process the patch content of a pull request.

    Args:
        github_client (GithubClient): The GitHub client instance.
        openai_client (OpenAIClient): The OpenAI client instance.
        pr_id (int): The pull request ID.
        language (str): The language for the review.
        custom_prompt (str, optional): Custom prompt for the code review.
        oai_model (str): The OpenAI model being leveraged for the review.
        mode (str): The processing mode of file or patch
        oai_temp (int): Number from 0 to 1 indicating level of creativity for OpenAI response

    """
    logging.info("Processing patch for PR ID: %s", pr_id)
    patch_content = github_client.get_pr_patch(pr_id)
    if not patch_content:
        logging.info("Patch file does not contain any changes.")
        github_client.post_comment(pr_id, "Patch file does not contain any changes")
        return
    analyze_patch(github_client, openai_client, pr_id, patch_content, language, custom_prompt, oai_model, mode, oai_temp)

def analyze_commit_files(github_client, openai_client, pr_id, commit, language, custom_prompt, oai_model, mode, oai_temp):
    """
    Analyze all files in a given commit together and post a single comment.

    Args:
        github_client (GithubClient): The GitHub client instance.
        openai_client (OpenAIClient): The OpenAI client instance.
        pr_id (int): The pull request ID.
        commit (Commit): The commit objects.
        language (str): The language for the review.
        custom_prompt (str, optional): Custom prompt for the code review.
        oai_model (str): The OpenAI model being leveraged for the review.
        mode (str): The processing mode of file or patch
        oai_temp (int): Number from 0 to 1 indicating level of creativity for OpenAI response
    """
    logging.info("Analyzing files in commit: %s", commit.sha)
    files = github_client.get_commit_files(commit)

    combined_content = ""
    for file in files:
        logging.info("Processing file: %s", file.filename)
        content = github_client.get_file_content(commit.sha, file.filename)
        combined_content += f"\n### File: {file.filename}\n```{content}```\n"

    review = openai_client.generate_response(create_review_prompt(combined_content,
                                                                  language,
                                                                  custom_prompt))

    github_client.post_comment(pr_id, f"ChatGPT model: {oai_model}\n mode: {mode}\n temperature: {oai_temp}\n {review}")

def analyze_patch(github_client, openai_client, pr_id, patch_content, language, custom_prompt, oai_model, mode, oai_temp):
    """
    Analyze the patch content of a pull request and post a single comment.

    Args:
        github_client (GithubClient): The GitHub client instance.
        openai_client (OpenAIClient): The OpenAI client instance.
        pr_id (int): The pull request ID.
        patch_content (str): The patch content.
        language (str): The language for the review.
        custom_prompt (str, optional): Custom prompt for the code review.
        oai_model (str): The OpenAI model being leveraged for the review.
        mode (str): The processing mode of file or patch
        oai_temp (int): Number from 0 to 1 indicating level of creativity for OpenAI response

    """
    logging.info("Analyzing patch content for PR ID: %s", pr_id)

    combined_chgs = ""

    logging.info("patch content is: %s", patch_content) #for troubleshooting, to remove later
    for chgs_text in patch_content.split(" diff "):
        if chgs_text:
            try:
                file_name = chgs_text.split("b/")[1].splitlines()[0]
                logging.info("Processing changes for file: %s", file_name)
                combined_chgs += f"\n### File: {file_name}\n```chgs\n{chgs_text}```\n"
            except (TypeError, ValueError) as e:
                logging.error("Error processing changes for file: %s: %s", file_name, str(e))
                github_client.post_comment(
                    pr_id,
                    f"ChatGPT was unable to process the response for {file_name}: {str(e)}"
                )

    review_prompt = create_review_prompt(combined_chgs, language, custom_prompt)
    review = openai_client.generate_response(review_prompt)
    github_client.post_comment(pr_id, f"ChatGPT model: {oai_model}\n mode: {mode}\n temperature: {oai_temp}\n {review}")

def create_review_prompt(content, language, max_tokens, custom_prompt=None):
    """
    Create a review prompt for the OpenAI API.

    Args:
        content (str): The content of the code to be reviewed.
        language (str): The language for the review.
        custom_prompt (str, optional): Custom prompt for the code review.
        max_tokens (str): Max number of tokens returnable

    Returns:
        str: The review prompt.
    """
    if custom_prompt:
        logging.info("Using custom prompt: %s", custom_prompt)
        return (
            f"{custom_prompt}\n"
            "### Code\n"
            f"```{content}```\n\n"
            f"Write this code review in the following {language}:\n\n"
        )
    return (
        f"You are now an expert code reviewer. Please review the following code for clarity, efficiency, and adherence to best practices. "
        f"Identify any areas for improvement, suggest specific optimizations, and note potential bugs or security vulnerabilities. "
        f"Additionally, provide suggestions for how to address the identified issues, with a focus on maintainability and scalability. "
        f"Include examples of code where relevant. Use markdown formatting for your response:\n\n"
        f"Keep your responses within the defined max token limit of {max_tokens}, ensuring you summarize as necessary to stay within the limit."
        f"Make it clear when you summarized to stay within the max token limit and indicate the number of tokens used for the review."
        f"Write this code review in the following {language}:\n\n"
        f"Do not write the code or guidelines in the review. Only write the review itself.\n\n"
        f"### Code\n```{content}```\n\n"
        f"### Review Guidelines\n"
        f"1. **Clarity**: Is the code easy to understand?\n"
        f"2. **Efficiency**: Are there any performance improvements?\n"
        f"3. **Best Practices**: Does the code follow standard coding conventions?\n"
        f"4. **Bugs/Security**: Are there any potential bugs or security vulnerabilities?\n"
        f"5. **Maintainability**: Is the code easy to maintain and scale?\n\n"
        f"### Review Example\n"
        f"1. **Issue**: The variable names are not descriptive.\n"
        f"   **Suggestion**: Use more descriptive variable names that reflect their purpose. For example:\n"
        f"   ```python\n"
        f"   # Instead of this:\n"
        f"   x = 5\n"
        f"   # Use this:\n"
        f"   item_count = 5\n"
        f"   ```\n"
        f"2. **Issue**: There is a potential SQL injection vulnerability.\n"
        f"   **Suggestion**: Use parameterized queries to prevent SQL injection. For example:\n"
        f"   ```python\n"
        f"   # Instead of this:\n"
        f"   cursor.execute('SELECT * FROM users WHERE username = (username)')\n"
        f"   # Use this:\n"
        f"   cursor.execute('SELECT * FROM users WHERE username = %s', (username,))\n"
        f"   ```"
    )

if __name__ == "__main__":
    main()
