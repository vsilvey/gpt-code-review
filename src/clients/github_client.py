"""
This module contains the GithubClient class, which is used to interact with the Github API. 
The GithubClient class can be used to retrieve information about users, commits, content of pull requests files and patches.
"""

import os
import logging
import requests
from github import Github


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class GithubClient:
    """
    A client for interacting with the GitHub API to manage pull requests and repository content.
    """

    def __init__(self, token):
        """
        Initialize the GithubClient with a GitHub token.

        Args:
            token (str): The GitHub token for authentication.
        """
        try:
            self.client = Github(token)
            logging.info("Github repository is: %s", os.getenv('GITHUB_REPOSITORY'))
            self.repo_name = os.getenv('GITHUB_REPOSITORY')
            self.repo = self.client.get_repo(self.repo_name)
            logging.info("Initialized GitHub client for repository: %s", self.repo_name)
        except Exception as e:
            logging.error("Error initializing GitHub client: %s", e)
            raise

    def get_pr(self, pr_id):
        """
        Retrieve a pull request by its ID.

        Args:
            pr_id (int): The pull request ID.

        Returns:
            PullRequest: The pull request object.
        """
        try:
            pr = self.repo.get_pull(pr_id)
            logging.info("Retrieved PR ID: %s", pr_id)
            return pr
        except Exception as e:
            logging.error("Error retrieving PR ID %s: %s", pr_id, e)
            raise

    def get_pr_comments(self, pr_id):
        """
        Retrieve comments from a pull request.

        Args:
            pr_id (int): The pull request ID.

        Returns:
            PaginatedList: The list of comments.
        """
        try:
            pr = self.get_pr(pr_id)
            comments = pr.get_issue_comments()
            logging.info("Retrieved comments for PR ID: %s", pr_id)
            return comments
        except Exception as e:
            logging.error("Error retrieving comments for PR ID %s: %s", pr_id, e)
            raise

    def post_comment(self, pr_id, body):
        """
        Post a comment to a pull request.

        Args:
            pr_id (int): The pull request ID.
            body (str): The comment body.

        Returns:
            IssueComment: The created comment.
        """
        try:
            pr = self.get_pr(pr_id)
            comment = pr.create_issue_comment(body)
            logging.info("Posted comment to PR ID: %s", pr_id)
            return comment
        except Exception as e:
            logging.error("Error posting comment to PR ID %s: %s", pr_id, e)
            raise

    def get_commit_files(self, commit):
        """
        Retrieve the files modified in a commit.

        Args:
            commit (Commit): The commit object.

        Returns:
            list: The list of files modified in the commit.
        """
        try:
            files = commit.files
            logging.info("Retrieved files for commit: %s", commit.sha)
            return files
        except Exception as e:
            logging.error("Error retrieving files for commit %s: %s", commit.sha, e)
            raise

    def get_file_content(self, commit_sha, filename):
        """
        Retrieve the content of a file at a specific commit.

        Args:
            commit_sha (str): The commit SHA.
            filename (str): The name of the file.

        Returns:
            str: The content of the file.
        """
        try:
            content = self.repo.get_contents(filename, ref=commit_sha).decoded_content.decode()
            logging.info("Retrieved content for file: %s at commit: %s", filename, commit_sha)
            return content
        except Exception as e:
            logging.error(
                "Error retrieving content for file %s at commit %s: %s",
                filename,
                commit_sha,
                e
            )
            raise

    def get_pr_patch(self, pr_id):
        """
        Retrieve the patch content of a pull request.

        Args:
            pr_id (int): The pull request ID.

        Returns:
            str: The patch content of the pull request.
        """
        try:
            url = f"https://api.github.com/repos/{self.repo_name}/pulls/{pr_id}"
            headers = {
                'Authorization': f"token {os.getenv('GH_TOKEN')}",
                'Accept': 'application/vnd.github.v3.diff'
            }
            response = requests.get(url, headers=headers, timeout=60)
            response.raise_for_status()
            logging.info("Retrieved patch for PR ID: %s", pr_id)
            return response.text
        except requests.RequestException as e:
            logging.error("Error retrieving patch for PR ID %s: %s", pr_id, e)
            raise

    def is_reviewer_assigned(self, pr_id, reviewer_name):
        """
        Check if the given reviewer is assigned to the pull request.
            
        Args:
            pr_id (int): The pull request ID.
            reviewer_name (str): The reviewer's username to check.

        Returns:
            bool: True if the reviewer passed in reviewer_name is assigned, False otherwise.
        """
        try:
            pr = self.get_pr(pr_id)
            reviewers = [r.login for r in pr.get_review_requests()[0]]  # Get user reviewers
            logging.info("Reviewers for PR ID %s: %s", pr_id, reviewers)
            return reviewer_name in reviewers
        except requests.RequestException as e:
            logging.error("Error checking for reviewers for PR ID %s: %s", pr_id, e)
            return False

    def get_most_recent_reviewer(self, pr_id):
        """
        Fetches the most recently assigned reviewer for a specific pull request,
        iterating through all paginated results and filtering by 'review_requested' event type.

        Args:
            pr_id (int): The pull request number.

        Returns:
            str: The username of the most recently assigned reviewer, or None if no reviewer was assigned.
        """
        try:
            base_url = f"https://api.github.com/repos/{self.repo_name}/issues/{pr_id}/timeline"
            headers = {
                'Authorization': f"token {os.getenv('GH_TOKEN')}",
                "Accept": "application/vnd.github.v3+json"
            }
            filtered_events = []
            page = 1

            # Paginate through all results
            while True:
                url = f"{base_url}?page={page}&per_page=100"
                response = requests.get(url, headers=headers, timeout=60)
                response.raise_for_status()
                events = response.json()

                if not events:
                    break  # Exit the loop if no more events are returned

                # Filter for "review_requested" events during pagination
                for event in events:
                    if event.get("event") == "review_requested" and event.get("requested_reviewer"):
                        filtered_events.append(event)

                page += 1  # Move to the next page

            logging.info("Retrieved %d 'review_requested' events for PR ID: %s", len(filtered_events), pr_id)

        except requests.RequestException as e:
            logging.error("Error retrieving timeline for PR ID %s: %s", pr_id, e)
            raise

        # Find the most recent "review_requested" event from filtered events
        for event in reversed(filtered_events):
            reviewer_login = event["requested_reviewer"]["login"]
            logging.info("Most recent reviewer requested is: %s", reviewer_login)
            return reviewer_login

        logging.info("No reviewer assignment found for PR ID: %s", pr_id)
        return None