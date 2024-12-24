
# Automated Code Review Assistance with OpenAI and GitHub Actions

This project automates code reviews using the GPT language model. It integrates with Github Actions so that when a PR is requested, if the assigned reviewer is "arovygptassistant", each code change made will be sent to GPT for review. GPT review comments will be posted as normal comments within the PR. Assignment of "arovygptassistant" is optional and this reviewer does not have the capability to approve or reject PRs.

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
    types: [review_requested]

jobs:
  genai_code_review:
    runs-on: ubuntu-latest
    name: GPT Code Review
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      - name: GPT Code Review
        uses: vsilvey/gpt-code-review@master
        with:
          openai_api_key: ${{ secrets.OPENAI_API_KEY }}
          github_token: ${{ secrets.GH_TOKEN }}
          github_pr_id: ${{ github.event.pull_request.number }}
          github_reviewer: 'arovygptassistant' # purposely hardcoded to trigger review when this reviewer is assigned
          openai_model: 'o1-mini' # 'o1-mini' is optimized for code reviews
          openai_temperature: 1 # default value accepted by 'o1-mini' model
          openai_max_tokens: 3000
          mode: patch # files (reviews any file in the pr with changes) or patch(reviews only the file changes)
          language: en # optional, default is 'en'
          custom_prompt: "" # optional
```

This workflow triggers whenever a pull request is opened or updated, and the action uses the provided configurations to perform the review.

---

## Configuration Parameters

| Parameter            | Description                                                                                   | Default          | Options                    |
|----------------------|-----------------------------------------------------------------------------------------------|------------------|----------------------------|
| **openai_model**     | The OpenAI model used for reviews.                                                            | `o1-mini`         | Other models like `gpt-4o` |
| **openai_temperature** | Controls creativity of responses. Higher values are more creative, lower values more deterministic. | `1`            | Range: `0.0` to `1.0`      |
| **openai_max_tokens** | The maximum token limit for responses.                                                       | `3000`           | Up to model's limit        |
| **mode**             | The mode for reviewing code.                                                                 | `files`          | `files`, `patch`           |
| **language**         | Language for the review comments.                                                            | `en`             | Any valid language code    |
| **custom_prompt**    | Custom instructions for AI reviews.                                                          | `""`             | User-defined string        |

---

## How It Works

The action leverages OpenAI and GitHub APIs to perform the following steps:

1. Authenticates with OpenAI using the provided API key and with GitHub using the `GITHUB_TOKEN`.
2. Identifies the pull request and the files or patches changed.
3. Determines wether or not the assigned reviewer is "arovygptassistant" 
4. Submits the changes to OpenAI's GPT model for review.
5. Posts the AI-generated feedback as comments on the pull request.

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

- **Rafael Cirolini** - [cirolini](https://github.com/cirolini)
    - Created the original process
    
- **Vince Silvey(Contributor)** - [vsilvey](https://github.com/vsilvey)
    - Altered the process to allow for the GPT review to be optionally triggered upon assignment of a specific reviewer instead of automatically generating a review as a pull request is opened or altered. Also changed the process to leverage the '1o-mini' model, providing the most advanced code review capability. Finally, updated packages in requirements.txt so the most current are used.

---

## License

This project is licensed under the MIT License. See the LICENSE file for details.
