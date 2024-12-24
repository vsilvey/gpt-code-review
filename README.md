
# Automated Code Review with OpenAI and GitHub Actions

This project automates code reviews for pull requests using OpenAI's GPT models. It integrates seamlessly with GitHub Actions to provide detailed, AI-powered feedback on code changes directly in the pull request.

---

## Setup

Follow the steps below to set up the automated code review for your repository.

### Prerequisites

Ensure you have the following:

- **OpenAI API Key**: Obtain your API key by signing up on the OpenAI platform at [OpenAI API](https://openai.com/api/).
- **GitHub Repository**: Have an existing GitHub repository where this automation will be used.

---

### Step 1: Add Your OpenAI API Key as a GitHub Secret

1. Navigate to your GitHub repository.
2. Go to **Settings > Secrets and variables > Actions**.
3. Create a new secret:
   - Name: `OPENAI_API_KEY`
   - Value: Your OpenAI API Key.

---

### Step 2: Adjust GitHub Actions Permissions

Ensure GitHub Actions can write comments to pull requests by configuring the repository's permission settings. Refer to the [GitHub documentation on automatic token authentication](https://docs.github.com/en/actions/security-guides/automatic-token-authentication#modifying-the-permissions-for-the-github_token) for more details.

---

### Step 3: Add the Workflow File

Create a workflow file in your repository under `.github/workflows/code-review.yml` with the following content:

```yaml
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  code_review:
    runs-on: ubuntu-latest
    name: Automated Code Review
    steps:
      - name: Checkout Code
        uses: actions/checkout@v3

      - name: Run OpenAI Code Review
        uses: your-org/your-action-name@v1
        with:
          openai_api_key: ${{ secrets.OPENAI_API_KEY }}
          github_token: ${{ secrets.GITHUB_TOKEN }}
          github_pr_id: ${{ github.event.pull_request.number }}
          github_reviewer: "sonargptreviewer"  # Specify reviewer name
          openai_model: "gpt-4"               # Optional: Model to use
          openai_temperature: 0.7             # Optional: Creativity level
          openai_max_tokens: 2048             # Optional: Max tokens for response
          mode: patch                         # 'files' or 'patch'
          language: en                        # Language for the review
          custom_prompt: ""                   # Optional: Provide specific instructions for reviews
```

This workflow triggers whenever a pull request is opened or updated, and the action uses the provided configurations to perform the review.

---

## Configuration Parameters

| Parameter            | Description                                                                                   | Default          | Options                    |
|----------------------|-----------------------------------------------------------------------------------------------|------------------|----------------------------|
| **openai_model**     | The OpenAI model used for reviews.                                                            | `gpt-4`          | Other models like `gpt-3.5-turbo` |
| **openai_temperature** | Controls creativity of responses. Higher values are more creative, lower values more deterministic. | `0.5`            | Range: `0.0` to `1.0`      |
| **openai_max_tokens** | The maximum token limit for responses.                                                       | `2048`           | Up to model's limit        |
| **mode**             | The mode for reviewing code.                                                                 | `files`          | `files`, `patch`           |
| **language**         | Language for the review comments.                                                            | `en`             | Any valid language code    |
| **custom_prompt**    | Custom instructions for AI reviews.                                                          | `""`             | User-defined string        |

---

## How It Works

The action leverages OpenAI and GitHub APIs to perform the following steps:

1. Authenticates with OpenAI using the provided API key and with GitHub using the `GITHUB_TOKEN`.
2. Identifies the pull request and the files or patches changed.
3. Submits these changes to OpenAI's GPT model for review.
4. Posts the AI-generated feedback as comments on the pull request.

---

## Modes of Operation

### **Files Mode**
The action analyzes the content of changed files in the pull request and provides detailed reviews.

### **Patch Mode**
The action reviews only the differences (patches) between the original and updated files, focusing on the modifications.

---

## Custom Prompts

### Overview
The `custom_prompt` parameter lets you tailor the review process to your specific needs. By providing a custom prompt, you can direct the AI to focus on areas like:

- Code quality and readability
- Security concerns
- Performance optimization
- Adherence to coding standards

### Example
To request a code rating, use the following configuration:

```yaml
custom_prompt: "Rate the code quality on a scale from 1 to 10 and explain the rating."
```

---

## Built With

- [OpenAI](https://openai.com/) - AI platform
- [GitHub Actions](https://github.com/features/actions) - CI/CD automation

---

## Security and Privacy

When using this tool, ensure that sensitive code or data is handled carefully. OpenAI and GitHub provide strong security measures, but it is the user's responsibility to:

- Avoid sending sensitive information in requests.
- Use secure secrets management for API keys and tokens.
- Periodically rotate and revoke unused keys.

For additional details, refer to [OpenAI's Privacy Policy](https://openai.com/privacy/).

---

## Authors and Contributors

- **Your Name/Organization** - [GitHub Profile](https://github.com/your-profile)

---

## License

This project is licensed under the MIT License. See the LICENSE file for details.
