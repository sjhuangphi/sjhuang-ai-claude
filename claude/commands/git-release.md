Perform a git release workflow.

Arguments: $ARGUMENTS
Parse the arguments as: `<branch-name> <tag-name> [annotation]`
- `<branch-name>`: branch to release; if `main`, tag main directly without merging
- `<tag-name>`: the tag to create
- `[annotation]`: optional tag annotation body; behaviour depends on Case A/B below

Example: `release/feature v20260301-2`
Example: `main v20260301-2`
Example: `release/feature v20260301-2 "feat: TCG-12345"`

---

## Case A: branch is NOT `main` (normal release flow)

1. `git fetch origin <branch-name>`
2. `git checkout main` (ensure we're on main)
3. `git merge origin/<branch-name>`
4. `git push origin main`
5. Collect tag annotation message:
   - If `[annotation]` argument was provided, use it as the body
   - Otherwise, run `git log origin/main...origin/<branch-name> --no-merges --pretty=format:"%h %s"` and use the output as the body
   - Format the full annotation as:
     ```
     <tag-name>

     <body>
     ```
   - The first line (tag name) becomes the tag title; commit log goes in the body
6. `git tag <tag-name> -m "<formatted annotation>"`
7. `git push origin <tag-name>`
8. `git push origin --delete <branch-name>`
9. If local branch exists: `git branch -d <branch-name>`

## Case B: branch IS `main` (tag main directly)

1. `git fetch origin main`
2. `git checkout main`
3. Build tag annotation:
   - If `[annotation]` argument was provided, format as:
     ```
     <tag-name>

     <annotation>
     ```
   - If NOT provided, annotation is just the tag name (no body):
     ```
     <tag-name>
     ```
4. `git tag <tag-name> -m "<annotation>"`
5. `git push origin <tag-name>`
6. Do NOT delete main branch

---

After completion, summarize:
- Which branch was merged (or "tagged main directly")
- What tag was created
- Tag annotation content
- Branch deletion status
