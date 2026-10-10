#!/usr/bin/env python3
"""Tests for git-sins. Builds tiny real git repositories in temp dirs."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(__file__))
import git_sins


def git(repo, *args, env_extra=None, date=None):
    env = dict(os.environ)
    env.setdefault("GIT_AUTHOR_NAME", "Tester")
    env.setdefault("GIT_AUTHOR_EMAIL", "tester@example.com")
    env.setdefault("GIT_COMMITTER_NAME", "Tester")
    env.setdefault("GIT_COMMITTER_EMAIL", "tester@example.com")
    if date is not None:
        stamp = date.strftime("%Y-%m-%dT%H:%M:%S+0000")
        env["GIT_AUTHOR_DATE"] = stamp
        env["GIT_COMMITTER_DATE"] = stamp
    if env_extra:
        env.update(env_extra)
    p = subprocess.run(["git", "-C", repo, *args], env=env,
                       capture_output=True, text=True, timeout=30)
    if p.returncode != 0:
        raise AssertionError("git %s failed: %s" % (args, p.stderr))
    return p.stdout


def commit_file(repo, name, content, message, date=None):
    with open(os.path.join(repo, name), "w", encoding="utf-8") as fh:
        fh.write(content)
    git(repo, "add", name)
    git(repo, "commit", "-m", message, date=date)


def make_repo(*commits):
    """commits: list of (filename, content, message, date|None)."""
    tmp = tempfile.mkdtemp()
    git(tmp, "init", "-b", "main")
    for filename, content, message, date in commits:
        commit_file(tmp, filename, content, message, date=date)
    return tmp


class TestRegexRules(unittest.TestCase):
    def test_empty_subjects(self):
        for s in ["wip", "WIP", "fix", "asdf", "final2", "aaa", "...", "xx"]:
            self.assertIsNotNone(git_sins.EMPTY_SUBJECT.match(s), s)
        for s in ["add parser", "fix: crash on empty input", "release 1.0"]:
            self.assertIsNone(git_sins.EMPTY_SUBJECT.match(s), s)

    def test_vanity_subjects(self):
        for s in ["final version", "v2 of the parser", "real final now"]:
            self.assertIsNotNone(git_sins.VANITY_SUBJECT.search(s), s)
        self.assertIsNone(git_sins.VANITY_SUBJECT.search("add version parser"))

    def test_level_thresholds(self):
        self.assertEqual(git_sins._level_name(git_sins.level_for(0)), "Absolved")
        self.assertEqual(git_sins._level_name(git_sins.level_for(25)), "Penance")
        self.assertEqual(git_sins._level_name(git_sins.level_for(60)), "Confession required")
        self.assertEqual(git_sins._level_name(git_sins.level_for(90)), "Excommunication")


class TestSinEngine(unittest.TestCase):
    def test_clean_repo_is_absolved(self):
        repo = make_repo(
            ("a.txt", "hello\n", "add greeting module", datetime(2026, 9, 1, 10, 0)),
            ("a.txt", "hello world\n", "greeting: add punctuation", datetime(2026, 9, 2, 11, 0)),
        )
        data = git_sins.collect(repo)
        sins = git_sins.analyze(data)
        value = git_sins.score(sins, len(data["commits"]))
        self.assertEqual(value, 0)
        self.assertEqual(git_sins._level_name(git_sins.level_for(value)), "Absolved")

    def test_sinner_repo_scores_high(self):
        night = datetime(2026, 9, 1, 3, 30)
        commits = [("f%d.txt" % i, "x\n", "wip", night + timedelta(days=i)) for i in range(10)]
        repo = make_repo(*commits)
        data = git_sins.collect(repo)
        sins = git_sins.analyze(data)
        titles = [s[1] for s in sins]
        self.assertIn("Empty confession (meaningless messages)", titles)
        self.assertIn("Nocturnal commits", titles)
        value = git_sins.score(sins, len(data["commits"]))
        self.assertGreaterEqual(value, 40)

    def test_mega_commit_detected(self):
        big = "\n".join("line %d" % i for i in range(600)) + "\n"
        repo = make_repo(
            ("a.txt", "x\n", "start", datetime(2026, 9, 1, 10, 0)),
            ("big.txt", big, "add everything at once", datetime(2026, 9, 2, 10, 0)),
        )
        sins = git_sins.analyze(git_sins.collect(repo))
        self.assertTrue(any(s[0].startswith("🍔") for s in sins))

    def test_todo_graveyard_detected(self):
        repo = make_repo(
            ("a.txt", "# TODO fix\n# FIXME broken\n# HACK ugly\n", "add code", datetime(2026, 9, 1, 10, 0)),
        )
        sins = git_sins.analyze(git_sins.collect(repo))
        self.assertTrue(any(s[0].startswith("🪦") for s in sins))
        self.assertGreater(git_sins.score(sins, 1), 0)

    def test_zombie_branch_detected(self):
        tmp = tempfile.mkdtemp()
        git(tmp, "init", "-b", "main")
        commit_file(tmp, "a.txt", "x\n", "start", date=datetime(2026, 6, 1, 10, 0))
        git(tmp, "checkout", "-b", "feature/ancient")
        commit_file(tmp, "b.txt", "y\n", "feature work", date=datetime(2026, 6, 2, 10, 0))
        git(tmp, "checkout", "main")
        commit_file(tmp, "c.txt", "z\n", "main work", date=datetime.now())
        sins = git_sins.analyze(git_sins.collect(tmp))
        self.assertTrue(any(s[0].startswith("🧟") for s in sins))

    def test_tiny_repo_gets_mercy(self):
        night = datetime(2026, 9, 1, 3, 30)
        repo = make_repo(("a.txt", "x\n", "wip", night))
        data = git_sins.collect(repo)
        value = git_sins.score(git_sins.analyze(data), len(data["commits"]))
        self.assertLessEqual(value, 19)

    def test_read_only_collect(self):
        """collect() must never modify the repository."""
        repo = make_repo(("a.txt", "x\n", "start", datetime(2026, 9, 1, 10, 0)))
        before = git(repo, "status", "--porcelain") + git(repo, "rev-parse", "HEAD")
        git_sins.collect(repo)
        after = git(repo, "status", "--porcelain") + git(repo, "rev-parse", "HEAD")
        self.assertEqual(before, after)


class TestCLI(unittest.TestCase):
    def setUp(self):
        self.repo = make_repo(
            ("a.txt", "hello\n", "add greeting module", datetime(2026, 9, 1, 10, 0)),
            ("b.txt", "# TODO later\n", "wip", datetime(2026, 9, 2, 3, 0)),
        )

    def test_markdown_report(self):
        out = subprocess.run([sys.executable, git_sins.__file__, self.repo],
                             capture_output=True, text=True, timeout=60)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("Confession", out.stdout)
        self.assertIn("Sin Score", out.stdout)

    def test_json_output(self):
        out = subprocess.run([sys.executable, git_sins.__file__, self.repo, "--json"],
                             capture_output=True, text=True, timeout=60)
        payload = json.loads(out.stdout)
        self.assertIn("sin_score", payload)
        self.assertIn("sins", payload)
        self.assertEqual(payload["repo"], os.path.basename(self.repo))

    def test_share_block(self):
        out = subprocess.run([sys.executable, git_sins.__file__, self.repo, "--share"],
                             capture_output=True, text=True, timeout=60)
        self.assertIn("img.shields.io/badge/git__sins", out.stdout)

    def test_out_flag_writes_file(self):
        path = os.path.join(self.repo, "..", "confession.md")
        subprocess.run([sys.executable, git_sins.__file__, self.repo, "--out", path],
                       capture_output=True, text=True, timeout=60)
        with open(path, encoding="utf-8") as fh:
            self.assertIn("Sin Score", fh.read())
        os.remove(path)

    def test_non_git_dir_fails_friendly(self):
        tmp = tempfile.mkdtemp()
        out = subprocess.run([sys.executable, git_sins.__file__, tmp],
                             capture_output=True, text=True, timeout=60)
        self.assertNotEqual(out.returncode, 0)
        self.assertIn("not a git working tree", out.stderr)


if __name__ == "__main__":
    unittest.main()
