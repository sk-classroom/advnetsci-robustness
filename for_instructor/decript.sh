openssl enc -d -aes-256-cbc -salt -pbkdf2 -iter 100000 \
  -in ./grading/assignment.py.enc \
  -out ./grading/assignment.py \
  -pass env:GITHUB_CLASSROOM_ASSIGNMENT_KEY
