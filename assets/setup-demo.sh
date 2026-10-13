#!/usr/bin/env bash
# Builds a small sinful repo at /tmp/demo for the git-sins demo GIF.
# Used by demo.tape; safe to run anywhere (creates nothing outside /tmp).
set -e
rm -rf /tmp/demo
mkdir -p /tmp/demo && cd /tmp/demo
git init -q
git config user.email demo@example.com
git config user.name "Demo Dev"
echo one > a.txt && git add . && GIT_AUTHOR_DATE=2026-09-01T03:30 GIT_COMMITTER_DATE=2026-09-01T03:30 git commit -qm "wip"
echo two > b.txt && git add . && GIT_AUTHOR_DATE=2026-09-02T04:10 GIT_COMMITTER_DATE=2026-09-02T04:10 git commit -qm "fix"
echo TODO later >> b.txt && seq 1 600 > big.txt && git add . && GIT_AUTHOR_DATE=2026-09-03T02:50 GIT_COMMITTER_DATE=2026-09-03T02:50 git commit -qm "final version"
echo "demo repo ready: 3 sinful commits"
