# git-sins — the confession booth for your git history.
# Any repo, any project: Docker is just how you run it, not what it is about.
FROM python:3.12-alpine

RUN apk add --no-cache git

COPY git_sins.py /usr/local/bin/git-sins
RUN chmod +x /usr/local/bin/git-sins

# Read-only by design: the container never pushes, commits or modifies anything.
ENTRYPOINT ["git-sins"]
CMD ["--help"]
