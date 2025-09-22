import requests

def initialise_standard_tools(mcp):
    mcp.tool(name="fetch_all_public_repos_for_user")(fetch_all_public_repos_for_user)
    mcp.tool(name="is_repo_owned_by_user")(is_repo_owned_by_user)

async def fetch_all_public_repos_for_user(username: str) -> list:
    """
    Fetch all public repositories for a given GitHub username.

    Args:
        username (str): GitHub username.
    Returns:
        list: List of public repositories.
    """
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    url = f"https://api.github.com/users/{username}/repos"

    response = requests.get(url, headers=headers)
    repos = response.json()
    return repos

async def is_repo_owned_by_user(username: str, repo_name: str) -> bool:
    """
    Check if a repository is owned by a particular user.

    Args:
        username (str): GitHub username.
        repo_name (str): Repository name.
    Returns:
        bool: True if the user owns the repo, False otherwise.
    """
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    url = f"https://api.github.com/repos/{username}/{repo_name}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        repo = response.json()
        return repo.get("owner", {}).get("login", "").lower() == username.lower()
    return False