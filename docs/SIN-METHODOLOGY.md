# The Sin Methodology

Deterministic rules, not vibes. Every sin is computed **only** from git data
(`log`, `numstat`, `ls-files`, `for-each-ref`, `merge-base`) — same evidence,
same verdict, every time. No network, no heuristics that shame without proof.

## Evidence collected

| Source | Command | Used for |
|---|---|---|
| Commit list | `log --pretty=format:%H%x1f%aI%x1f%an%x1f%s` | hours, authors, subjects |
| Diff sizes | `log --numstat --pretty=format:%x1e%H` | mega-commits |
| Merge count | `rev-list --count --merges HEAD` | straight-to-main |
| Branch ages | `for-each-ref refs/heads --format=…(committerdate:unix)` + `merge-base --is-ancestor` | zombie branches |
| Debt markers | scan of tracked files for `TODO/FIXME/HACK/XXX` | debt graveyard |

## The nine sins and their scoring

| # | Sin | Trigger | Points |
|---|---|---|---|
| 1 | 🌑 Nocturnal commits | author hour in 00:00–04:59 | 3 × count, cap 20 |
| 2 | 💬 Empty confession | subject is `wip`/`fix`/`asdf`/`test`/`…` or shorter than 4 chars | 2 × count, cap 20 |
| 3 | 🍔 Gluttony | one commit changes ≥ 500 lines | 5 × count, cap 15 |
| 4 | 🪦 Debt graveyard | TODO/FIXME/HACK/XXX occurrences in tracked files | 2 + 2 per 10 markers, cap 15 |
| 5 | 🥩 Vanity versioning | subject contains `final`/`v2`/`definitive`… | 2 × count, cap 10 |
| 6 | 🧟 Zombie branches | unmerged local branch, committer date ≥ 30 days old | 4 × count, cap 10 |
| 7 | 👑 Benevolent dictatorship | top author ≥ 80% of ≥ 20 commits | flat 15 |
| 8 | 🌊 Straight to main | ≥ 50 commits and 0 merge commits | flat 10 |
| 9 | 📅 Crunch days | any single day with ≥ 20 commits | 5 × days, cap 10 |

**Sin Score** = sum of points, capped at 100.

**Mercy clause:** repositories with fewer than 5 commits cannot score above 19 —
there is not enough history to judge anyone.

## Levels

| Score | Level | Badge color |
|---|---|---|
| 0–19 | 🟢 Absolved | `00A884` |
| 20–49 | 🟡 Penance | `F5C542` |
| 50–79 | 🟠 Confession required | `FF8C42` |
| 80–100 | 🔴 Excommunication | `D93F3F` |

The **dominant sin** is the one contributing the most points — fix that one first.

## Design rules for new sins

1. Provable from git data alone (a command, a regex, a threshold).
2. Evidence shown in the report (hashes, subjects, dates) — no shaming without proof.
3. A penance that a developer can act on this week.
4. Deterministic: same repo, same score, always.
