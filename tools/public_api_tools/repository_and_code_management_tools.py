import logging

from github import Github
from utilities.make_return_response import make_return_response

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename='mcp_server.log')

def initialise_standard_tools(mcp):
    mcp.tool(name="code_replace_in_file")(code_replace_in_file)
    
async def code_replace_in_file(
    owner: str,
    repo: str,
    file_path: str,
    search_text: str,
    replacement_text: str,
    github_token: str,
    commit_message: str = "Automated file replacement via AI agent"
) -> list:
    """
    Finds and replaces text within a specified file in a GitHub repository, 
    then commits the change directly to the default branch. The GitHub token 
    must be provided to authenticate the request.

    :param owner: The GitHub repository owner (e.g., 'octocat').
    :param repo: The name of the repository (e.g., 'Spoon-Knife').
    :param file_path: The full path to the file to modify (e.g., 'src/main.py').
    :param search_text: The exact text string to search for.
    :param replacement_text: The replacement text string.
    :param github_token: The GitHub Personal Access Token (PAT) or App Token for authentication.
    :param commit_message: The commit message for the change (optional).
    :return: A message indicating success or failure, including the commit URL.
    """
    
    # Initialize GitHub client with the provided token
    try:
        g = Github(github_token)
        repository = g.get_user(owner).get_repo(repo)
    except Exception as e:
        logging.error(f"Authentication/Repo Access Error: {e}")
        return make_return_response({
            "status_code": 401,
            "message": f"Error: Could not authenticate or access repository {owner}/{repo}. Check the provided token and permissions."
        })

    # Get the File Content
    try:
        contents = repository.get_contents(file_path)
        if isinstance(contents, list):
            logging.error(f"File Access Error: '{file_path}' is a directory, not a file.")
            return make_return_response({
                "status_code": 400,
                "message": f"Error: '{file_path}' is a directory, not a file."
            })
        current_content = contents.decoded_content.decode('utf-8')
    except Exception as e:
        logging.error(f"File Access Error: {e}")
        return make_return_response({
            "status_code": 404,
            "message": f"Error accessing file '{file_path}': The file may not exist or the token lacks read permission."
        })
        
    # Perform the Replacement
    if search_text not in current_content:
        return make_return_response({
            "status_code": 400,
            "message": f"Warning: Search text '{search_text}' not found in {file_path}. No changes committed."
        })

    new_content = current_content.replace(search_text, replacement_text)
    
    if new_content == current_content:
        return make_return_response({
            "status_code": 400,
            "message": "Warning: Replacement resulted in no change to content. No changes committed."
        })

    # Commit the Change
    try:
        # The author info will be derived from the token's owner
        update = repository.update_file(
            path=file_path,
            message=commit_message,
            content=new_content,
            sha=contents.sha,
            branch=repository.default_branch
        )
        
        logging.info(f"Successful commit to {owner}/{repo}: {update['commit'].html_url}")
        return make_return_response({
            "status_code": 200,
            "message": f"✅ Success! File '{file_path}' updated and committed. Commit URL: {update['commit'].html_url}"
        })

    except Exception as e:
        logging.error(f"Commit Operation Error: {e}")
        return make_return_response({
            "status_code": 500,
            "message": f"❌ Fatal Error during commit: {e}"
        })