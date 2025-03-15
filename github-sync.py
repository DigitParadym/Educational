# Updated on 2024-09-05 15:30:00.000000
import os
from git import Repo, GitCommandError

def push_to_github(repo_path, commit_message="Update scripts", branch_name=None):
    try:
        # Change to the directory containing the git repository
        os.chdir(os.path.expanduser(repo_path))

        repo = Repo(repo_path)

        # Optionally set a branch to push to
        if branch_name:
            print(f"Checking out branch: {branch_name}")
            repo.git.checkout(branch_name)

        print(f"Attempting to automatically pull and merge changes from remote {repo.active_branch.name} branch...")
        print("Conflicts will be resolved automatically if possible, but manual review might be necessary.")
        
        try:
            repo.git.pull('origin', repo.active_branch.name)
        except GitCommandError as pull_error:
            if "CONFLICT" in str(pull_error):
                print(f"Merge conflicts encountered during pull. Automatic resolution was attempted, but some conflicts might remain.")
                print("Please carefully review and resolve any remaining conflicts manually.")
                return
            else:
                raise

        # Add all changes, including untracked files
        print("Adding all changes...")
        repo.git.add(A=True)
        
        if repo.is_dirty():
            print(f"Committing changes with message: '{commit_message}'")
            repo.index.commit(commit_message)
        else:
            print("No changes to commit.")
        
        origin = repo.remote(name='origin')
        print(f"Pushing changes to {repo.active_branch.name} branch on GitHub...")
        push_info = origin.push()

        # Confirm that the push was successful
        if push_info[0].flags & push_info[0].ERROR:
            print(f"Failed to push changes: {push_info[0].summary}")
        else:
            print("Changes pushed to GitHub successfully.")
    
    except GitCommandError as e:
        print(f"Git command error: {e}")
    
    except OSError as e:
        print(f"OS error: {e.strerror}. Check if the path exists and you have sufficient permissions.")
    
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    repo_path = 'C:\\Users\\User\\Script_Loop_Development'  # The correct path to your repository
    push_to_github(repo_path, "Auto-sync commit", branch_name="commit-to-change")
