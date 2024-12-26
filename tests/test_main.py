import unittest
from unittest.mock import patch, MagicMock
from src.main import main, process_files, process_patch, get_env_vars


class TestMainModule(unittest.TestCase):

    @patch("src.main.GithubClient")
    @patch("src.main.OpenAIClient")
    @patch("src.main.get_env_vars")
    def test_main_files_mode(self, mock_get_env_vars, MockOpenAIClient, MockGithubClient):
        # Mock environment variables
        mock_get_env_vars.return_value = {
            "GH_TOKEN": "fake_github_token",
            "OPENAI_API_KEY": "fake_openai_api_key",
            "OPENAI_MODEL": "gpt-4",
            "OPENAI_TEMPERATURE": 0.7,
            "OPENAI_MAX_TOKENS": 2000,
            "MODE": "files",
            "GITHUB_PR_ID": 123,
            "GITHUB_REVIEWER": "sonargptreviewer",
            "LANGUAGE": "en",
            "CUSTOM_PROMPT": None,
        }

        # Mock GitHub and OpenAI clients
        mock_github_client = MockGithubClient.return_value
        mock_openai_client = MockOpenAIClient.return_value

        # Mock get_most_recent_reviewer to match the assigned reviewer
        mock_github_client.get_most_recent_reviewer.return_value = "sonargptreviewer"

        with patch("src.main.process_files") as mock_process_files:
            main()
            mock_process_files.assert_called_once_with(
                mock_github_client,
                mock_openai_client,
                123,
                "en",
                None,
                "gpt-4",
                "files",
                0.7
            )

    @patch("src.main.GithubClient")
    @patch("src.main.OpenAIClient")
    @patch("src.main.get_env_vars")
    def test_main_patch_mode(self, mock_get_env_vars, MockOpenAIClient, MockGithubClient):
        # Mock environment variables for 'patch' mode
        mock_get_env_vars.return_value = {
            "GH_TOKEN": "fake_github_token",
            "OPENAI_API_KEY": "fake_openai_api_key",
            "OPENAI_MODEL": "gpt-4",
            "OPENAI_TEMPERATURE": 0.7,
            "OPENAI_MAX_TOKENS": 2000,
            "MODE": "patch",
            "GITHUB_PR_ID": 123,
            "GITHUB_REVIEWER": "sonargptreviewer",
            "LANGUAGE": "en",
            "CUSTOM_PROMPT": None,
        }

        # Mock GitHub and OpenAI clients
        mock_github_client = MockGithubClient.return_value
        mock_openai_client = MockOpenAIClient.return_value

        # Mock get_most_recent_reviewer to match the assigned reviewer
        mock_github_client.get_most_recent_reviewer.return_value = "sonargptreviewer"

        with patch("src.main.process_patch") as mock_process_patch:
            main()
            mock_process_patch.assert_called_once_with(
                mock_github_client,
                mock_openai_client,
                123,
                "en",
                None,
                "gpt-4",
                "patch",
                0.7
            )

    @patch("src.main.get_env_variable")
    def test_get_env_vars(self, mock_get_env_variable):
        # Mock environment variables
        mock_get_env_variable.side_effect = lambda var, required: {
            "GH_TOKEN": "fake_github_token",
            "OPENAI_API_KEY": "fake_openai_api_key",
            "GITHUB_PR_ID": "123",
            "OPENAI_MODEL": "gpt-4",
            "OPENAI_TEMPERATURE": "0.7",
            "OPENAI_MAX_TOKENS": "2000",
            "MODE": "files",
            "LANGUAGE": "en",
            "CUSTOM_PROMPT": None,
        }.get(var, None)

        env_vars = get_env_vars()
        self.assertEqual(env_vars["GH_TOKEN"], "fake_github_token")
        self.assertEqual(env_vars["GITHUB_PR_ID"], 123)
        self.assertEqual(env_vars["OPENAI_TEMPERATURE"], 0.7)

    @patch("src.main.GithubClient")
    @patch("src.main.OpenAIClient")
    def test_process_files(self, MockOpenAIClient, MockGithubClient):
        mock_github_client = MockGithubClient.return_value
        mock_openai_client = MockOpenAIClient.return_value

        mock_pull_request = MagicMock()
        mock_commit = MagicMock(sha="abc123")
        mock_file = MagicMock(filename="testit.py")

        mock_github_client.get_pr.return_value = mock_pull_request
        mock_pull_request.get_commits.return_value = [mock_commit]
        mock_github_client.get_commit_files.return_value = [mock_file]
        mock_github_client.get_file_content.return_value = "print('Hello, World!')"
        mock_openai_client.generate_response.return_value = "Code review response"

        process_files(
            mock_github_client,
            mock_openai_client,
            pr_id=123,
            language="en",
            custom_prompt=None,
            oai_model="gpt-4",
            mode="files",
            oai_temp=0.7
        )

        mock_github_client.get_pr.assert_called_once_with(123)
        mock_pull_request.get_commits.assert_called_once()
        mock_github_client.get_commit_files.assert_called_once_with(mock_commit)
        mock_openai_client.generate_response.assert_called_once()
        mock_github_client.post_comment.assert_called_once()

if __name__ == "__main__":
    unittest.main()