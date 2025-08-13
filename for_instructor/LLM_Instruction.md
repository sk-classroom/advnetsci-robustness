# For instructor

## Workflow

- [ ] Test run the teacher notebook by running
  - `uv run tests/test_01.py`  (more tests if needed)
  - `./grading/run_quiz_test.sh --config ./grading/config.toml --quiz-file ./assignment/quiz.toml --api-key ${{ secrets.CHAT_API }} --output ./assignment/quiz_results.json`
  - If the results are not as expected, fix the code in "grading/assignment.py" and repeat the process
- [ ] Generate the student version and the encrypted teacher's notebook
  - Copy "./grading/assignment.py" to "./assignment/assignment.py"
  - Remove the code to test in the student version
  - Encrypt using OpenSSL with PBKDF2 and iterations (recommended):
    ```bash
    openssl enc -aes-256-cbc -salt -pbkdf2 -iter 100000 \
      -in grading/assignment.py \
      -out grading/assignment.py.enc \
      -pass env:GITHUB_CLASSROOM_ASSIGNMENT_KEY
    ```
- [ ] Add the encrypted teacher's notebook to the repository
  - Remove all commit history if needed by following these steps:
    1. Create a fresh orphan branch: `git checkout --orphan latest_branch`
    2. Add all files: `git add -A`
    3. Commit: `git commit -am "Initial commit"`
    4. Delete the old branch: `git branch -D main` (or your current branch name)
    5. Rename the new branch: `git branch -m main`
    6. Force push to overwrite history: `git push -f origin main`
    7. One line command: `git checkout --orphan latest_branch && git add -A && git commit -am "Initial commit" && git branch -D main && git branch -m main && git push -f origin main`

## Check list

- [ ] Upload
  - [ ] The `assignment/assignment.py` is uploaded to the repository
  - [ ] The `grading/assignment.py` is **NOT** uploaded to the repository
  - [ ] The `grading/assignment.py.enc` is uploaded to the repository
- [ ] Autograding
  - [ ] All tests run successfully
- [ ] Keep the password secret
