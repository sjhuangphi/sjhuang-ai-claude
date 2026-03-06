Create a GitHub Pull Request workflow.

Arguments: $ARGUMENTS
Parse the arguments as: `<head-branch> <base-branch> [title]`
- `<head-branch>`: the branch with your changes (source)
- `<base-branch>`: the branch to merge into (target)
- `[title]`: optional PR title; if omitted, auto-generate from branch name

Example: `dev/feature release/feature`
Example: `dev/login main "feat: add login page"`

Steps to execute:
1. Verify both branches exist on remote: `gh api repos/{owner}/{repo}/branches`
2. If `<base-branch>` does NOT exist on remote, create it from `main`:
   - `git fetch origin main`
   - `git checkout -b <base-branch> origin/main`
   - `git push -u origin <base-branch>`
3. Create the Pull Request:
   - `gh pr create --head <head-branch> --base <base-branch> --title "<title>" --body "..."`
   - Body should include: Summary section and Test plan checklist
4. Output the PR URL

Safety checks before proceeding:
- Do NOT delete any branches
- Do NOT merge anything
- If `<head-branch>` does not exist on remote, abort and inform the user

After completion, report:
- PR URL
- head → base direction
- PR title
