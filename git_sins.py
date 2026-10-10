#!/usr/bin/env python3
"""
git-sins — the confession booth for your git history.

Zero dependencies (beyond a git binary). Reads a repository's history (log,
numstat, TODO counts, branch ages), runs a deterministic sin engine over it and
renders a markdown confession report: each sin, its evidence, its penance, a
0-100 Sin Score and a shareable badge. Optional --ai mode asks your local agent
CLI for an absolution note. Read-only by design: it never touches your repo.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime

__version__ = "1.0.0"

# --- Sin detection rules -----------------------------------------------------
EMPTY_SUBJECT = re.compile(
    r"^(wip|wi+|fix|fixes|fixe[d s]*|asdf+|test|tests|update|updates|stuff|"
    r"things|changes|minor|temp|tmp|oops|final|final2|finalfinal|real.?final|"
    r"aaa+|xxx+|xx+|\.{2,}|-+)$", re.I)
VANITY_SUBJECT = re.compile(
    r"\b(v\d+|final|definitive|real.?final|last.?one|really.?final|"
    r"now.?for.?real|final.?final)\b", re.I)
TODO_PATTERN = re.compile(r"\b(TODO|FIXME|HACK|XXX)\b")
NOCTURNAL_HOURS = range(0, 5)  # 00:00 - 04:59 local
MEGA_LINES = 500
CRUNCH_COMMITS = 20
DICTATOR_SHARE = 0.80

LEVELS = [
    (80, "🔴 Excommunication", "D93F3F"),
    (50, "🟠 Confession required", "FF8C42"),
    (20, "🟡 Penance", "F5C542"),
    (0,  "🟢 Absolved", "00A884"),
]


def sh(repo, *args):
    """Run a git command in repo, returning (ok, stdout, stderr)."""
    try:
        p = subprocess.run(["git", "-C", repo, *args],
                           capture_output=True, text=True, timeout=60)
        return p.returncode == 0, p.stdout, p.stderr
    except FileNotFoundError:
        sys.exit("error: git not found in PATH. Install git or run this tool in its official image.")
    except subprocess.TimeoutExpired:
        return False, "", "git command timed out"


def collect(repo):
    """Gather the evidence. Read-only: inspect only, never modify."""
    repo = os.path.abspath(repo)
    ok, _, err = sh(repo, "rev-parse", "--is-inside-work-tree")
    if not ok or _.strip() != "true":
        sys.exit("error: '%s' is not a git working tree: %s" % (repo, (err or "no .git").strip()))
    ok, out, err = sh(repo, "log", "--pretty=format:%H%x1f%aI%x1f%an%x1f%s")
    if not ok:
        sys.exit("error: cannot read history of '%s': %s" % (os.path.basename(repo), (err or "empty repo").strip()))
    commits = []
    for line in out.splitlines():
        if not line.strip():
            continue
        h, ts, author, subject = (line.split("\x1f") + ["", "", ""])[:4]
        commits.append({"hash": h, "ts": ts, "author": author, "subject": subject})
    if not commits:
        sys.exit("error: '%s' has no commits yet. Even saints started somewhere." % os.path.basename(repo))

    ok, out, _ = sh(repo, "log", "--numstat", "--pretty=format:%x1e%H")
    numstat = {}
    for chunk in out.split("\x1e"):
        lines = [l for l in chunk.splitlines() if l.strip()]
        if not lines:
            continue
        changed = 0
        for l in lines[1:]:
            parts = l.split("\t")
            if len(parts) >= 2 and parts[0].isdigit():
                changed += int(parts[0]) + int(parts[1])
        numstat[lines[0]] = changed

    ok, out, _ = sh(repo, "rev-list", "--count", "--merges", "HEAD")
    merges = int(out.strip() or 0)

    ok, out, _ = sh(repo, "for-each-ref", "refs/heads",
                    "--format=%(refname:short)%09%(committerdate:unix)")
    zombies = []
    if ok:
        for line in out.splitlines():
            if "\t" not in line:
                continue
            name, unix = line.split("\t")
            if name == current_branch(repo):
                continue
            ok2, out2, _ = sh(repo, "merge-base", "--is-ancestor", name, "HEAD")
            age_days = (datetime.now() - datetime.fromtimestamp(int(unix))).days
            if age_days >= 30 and ok2 is False:
                zombies.append((name, age_days))

    todos = 0
    ok, out, _ = sh(repo, "ls-files")
    if ok:
        for f in out.splitlines()[:5000]:
            try:
                with open(os.path.join(repo, f), "r", encoding="utf-8", errors="ignore") as fh:
                    todos += len(TODO_PATTERN.findall(fh.read(1_000_000)))
            except OSError:
                pass

    return {
        "name": os.path.basename(repo),
        "commits": commits,
        "numstat": numstat,
        "merges": merges,
        "zombies": zombies,
        "todos": todos,
    }


def current_branch(repo):
    ok, out, _ = sh(repo, "rev-parse", "--abbrev-ref", "HEAD")
    return out.strip() if ok else ""


# --- Deterministic sin engine -------------------------------------------------
def analyze(data):
    """Deterministic rule engine -> list of sins (emoji, title, count, evidence, penance, points)."""
    sins = []
    total = len(data["commits"])

    nocturnal = [c for c in data["commits"]
                 if _ts(c["ts"]) is not None and _ts(c["ts"]).hour in NOCTURNAL_HOURS]
    if nocturnal:
        ex = ", ".join("“%s” (%s: %02dh)" % (c["subject"][:30], c["hash"][:7], _ts(c["ts"]).hour)
                       for c in nocturnal[:3])
        sins.append(("🌑", "Nocturnal commits", len(nocturnal),
                     "Committed between 00:00 and 04:59: %s" % ex,
                     "Sleep is a feature. Push at dawn what you cannot explain at noon.",
                     min(20, 3 * len(nocturnal))))

    empty = [c for c in data["commits"]
             if EMPTY_SUBJECT.match(c["subject"].strip()) or len(c["subject"].strip()) < 4]
    if empty:
        ex = ", ".join("“%s”" % c["subject"][:20] for c in empty[:3])
        sins.append(("💬", "Empty confession (meaningless messages)", len(empty),
                     "Subjects that confess nothing: %s" % ex,
                     "A subject line is a promise: what changed and why. `git commit -m \"fix\"` is a lie you tell your future self.",
                     min(20, 2 * len(empty))))

    mega = [(c["hash"][:7], data["numstat"].get(c["hash"], 0))
            for c in data["commits"] if data["numstat"].get(c["hash"], 0) >= MEGA_LINES]
    if mega:
        ex = ", ".join("%s (+%d lines)" % (h, n) for h, n in mega[:3])
        sins.append(("🍔", "Gluttony (mega-commits)", len(mega),
                     "Commits swallowing %d+ changed lines: %s" % (MEGA_LINES, ex),
                     "A commit should be reviewable in one sitting. Split by concern; your reviewers' evenings will thank you.",
                     min(15, 5 * len(mega))))

    if data["todos"]:
        sins.append(("🪦", "Debt graveyard (TODO/FIXME/HACK/XXX)", data["todos"],
                     "%d unfinished-business markers haunting the codebase" % data["todos"],
                     "Turn the oldest ten into issues this week. A TODO without an issue is a wish, not a plan.",
                     min(15, 2 + (data["todos"] * 2) // 10)))

    vanity = [c for c in data["commits"] if VANITY_SUBJECT.search(c["subject"])]
    if vanity:
        ex = ", ".join("“%s”" % c["subject"][:30] for c in vanity[:3])
        sins.append(("🥩", "Vanity versioning", len(vanity),
                     "The final-final saga: %s" % ex,
                     "If the message needs “real final” to be true, use the diff, not the adjective. Revert/rework instead of piling v3 on v2.",
                     min(10, 2 * len(vanity))))

    if data["zombies"]:
        ex = ", ".join("%s (%dd)" % (n, d) for n, d in data["zombies"][:3])
        sins.append(("🧟", "Zombie branches", len(data["zombies"]),
                     "Unmerged and rotting for 30+ days: %s" % ex,
                     "Branches do not age like wine. Merge, kill or annotate each one with a reason to live.",
                     min(10, 4 * len(data["zombies"]))))

    authors = Counter(c["author"] for c in data["commits"])
    if authors and total >= 20:
        top, n = authors.most_common(1)[0]
        if n / total >= DICTATOR_SHARE:
            sins.append(("👑", "Benevolent dictatorship", 1,
                         "%s authored %d/%d commits (%.0f%%)" % (top, n, total, 100.0 * n / total),
                         "Solo is fine; invisible is not. Document decisions so the repo survives its author's vacation.",
                         15))

    if data["merges"] == 0 and total >= 50:
        sins.append(("🌊", "Straight to main", 1,
                     "%d commits, 0 merge commits — everything lands directly on main" % total,
                     "Even a solo dev benefits from PR-shaped history: reviewable units, revertable steps, honest main.",
                     10))

    days = Counter((c["ts"] or "    ")[:10] for c in data["commits"])
    crunch = [d for d, n in days.items() if n >= CRUNCH_COMMITS]
    if crunch:
        worst = max(crunch, key=lambda d: days[d])
        sins.append(("📅", "Crunch days", len(crunch),
                     "Worst day: %s with %d commits" % (worst, days[worst]),
                     "Twenty commits in a day is a sprint, not a rhythm. Batch by feature and review the batch.",
                     min(10, 5 * len(crunch))))

    return sins


def _ts(ts):
    try:
        return datetime.fromisoformat(ts[:25])
    except (ValueError, TypeError):
        return None


def score(sins, total_commits):
    points = sum(s[5] for s in sins)
    if total_commits < 5:
        points = min(points, 19)  # too little history to judge; mercy
    return min(100, points)


def level_for(value):
    for threshold, label, color in LEVELS:
        if value >= threshold:
            return label, color
    return LEVELS[-1][1], LEVELS[-1][2]


def render_markdown(data, sins, value, dominant, level):
    lines = [
        "## ⛪ Confession — `%s`" % data["name"],
        "",
        "| Evidence | Value |",
        "|---|---|",
        "| Commits analyzed | %d |" % len(data["commits"]),
        "| Merge commits | %d |" % data["merges"],
        "| TODO/FIXME markers | %d |" % data["todos"],
        "| Zombie branches | %d |" % len(data["zombies"]),
        "",
        "**Sin Score: %d/100 — %s**" % (value, level),
    ]
    if dominant:
        lines += ["**Dominant sin: %s %s**" % (dominant[0], dominant[1])]
    if sins:
        lines += ["",
                  "| Sin | Count | Evidence | Penance |",
                  "|---|---|---|---|"]
        for emoji, title, count, evidence, penance, _pts in sins:
            lines += ["| %s %s | %s | %s | %s |" % (emoji, title, count, evidence, penance)]
    else:
        lines += ["", "🟢 *Nothing to confess. Either you are disciplined or you deleted .git. Both are valid.*"]
    closing = {
        "🔴 Excommunication": "Ten Hail Merges and a revert won't save this one. Start with the dominant sin tomorrow morning.",
        "🟠 Confession required": "Say five descriptive commit messages and three reviewed PRs, and go in peace. ⛪",
        "🟡 Penance": "Two clean weeks and the score forgives itself. ⛪",
        "🟢 Absolved": "Go in peace — and teach the others. ⛪",
    }
    lines += ["", closing[level]]
    lines += ["", "*Confessed by [git-sins](https://github.com/fernedy/git-sins) — "
                  "read-only, zero dependencies, deterministic. Your repo talked so you don't have to.*"]
    return "\n".join(lines) + "\n"


def _level_name(level):
    label = level[0] if isinstance(level, tuple) else level
    return " ".join(label.split(" ")[1:])


def share_block(data, value, level, color):
    label = _level_name(level).replace(" ", "_")
    return (
        "### %s — Sin Score %d/100 %s\n"
        "![sin score badge](https://img.shields.io/badge/git__sins-%d%%2F100-%s-%s?style=flat-square&logo=git)\n\n"
        "Confessed by [git-sins](https://github.com/fernedy/git-sins) — "
        "your repo's history, read back to it honestly.\n"
        % (data["name"], value, level, value, label, color)
    )


def ai_absolution(report):
    """Optional: ask a local agent CLI (opencode) for an absolution note."""
    exe = "opencode"
    if not any(os.access(os.path.join(p, exe), os.X_OK) for p in os.environ.get("PATH", "").split(os.pathsep)):
        return "_[ai] opencode not found in PATH — skipping AI absolution (everything else works without it)._"
    prompt = ("You are a wise but brutally honest confessor for developers. Given this git "
              "confession report, add a short section '### 🤖 AI absolution' with: the most "
              "likely root habit behind all these sins, one habit to adopt this week, and one "
              "habit to quit immediately. Be concise and slightly funny.\n\n" + report)
    try:
        p = subprocess.run([exe, "run", prompt], capture_output=True, text=True, timeout=120)
        if p.returncode != 0:
            return "_[ai] local agent failed: %s_" % (p.stderr.strip() or "unknown error")
        return p.stdout.strip()
    except FileNotFoundError:
        return "_[ai] opencode not found in PATH — skipping AI absolution._"
    except subprocess.TimeoutExpired:
        return "_[ai] local agent timed out — skipping AI absolution._"


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="git-sins",
        description="The confession booth for your git history: deterministic sins, "
                    "a 0-100 Sin Score and the penance to go with it.")
    ap.add_argument("repo", nargs="?", default=".", help="path to the git repository to confess (default: .)")
    ap.add_argument("--json", action="store_true", help="output raw evidence and sins as JSON")
    ap.add_argument("--ai", action="store_true", help="add an AI absolution note via your local agent CLI (opencode)")
    ap.add_argument("--share", action="store_true", help="print a shareable markdown block with a badge")
    ap.add_argument("--out", metavar="FILE", help="also write the markdown report to FILE")
    ap.add_argument("--version", action="version", version="%(prog)s " + __version__)
    args = ap.parse_args(argv)

    data = collect(args.repo)
    sins = analyze(data)
    value = score(sins, len(data["commits"]))
    level, color = level_for(value)
    dominant = max(sins, key=lambda s: s[5]) if sins and value > 0 else None

    if args.json:
        payload = {
            "repo": data["name"],
            "commits_analyzed": len(data["commits"]),
            "sin_score": value,
            "level": _level_name(level),
            "dominant_sin": "%s %s" % (dominant[0], dominant[1]) if dominant else None,
            "sins": [{"emoji": e, "sin": t, "count": c, "evidence": ev, "penance": p, "points": pt}
                     for e, t, c, ev, p, pt in sins],
        }
        print(json.dumps(payload, indent=2))
        return 0

    report = render_markdown(data, sins, value, dominant, level)
    if args.ai:
        report += "\n" + ai_absolution(report) + "\n"

    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(report + ("\n" + share_block(data, value, level, color) if args.share else ""))
        print("report written to %s" % args.out, file=sys.stderr)
    print(report)
    if args.share:
        print(share_block(data, value, level, color))
    return 0


if __name__ == "__main__":
    sys.exit(main())
