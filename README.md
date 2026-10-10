<div align="center">

[🇬🇧 English](README.md) · [🇪🇸 Español](README.es.md)

</div>

<div align="center">

# ⛪ git-sins

**Your repo has been keeping secrets. Let it confess.**

![Python](https://img.shields.io/badge/python-3.8%2B-blue?style=flat-square&logo=python&logoColor=white)
![Dependencies](https://img.shields.io/badge/dependencies-0-00A884?style=flat-square)
![Docker](https://img.shields.io/badge/deployed%20with-docker-2496ED?style=flat-square&logo=docker&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-yellow?style=flat-square)

**Zero dependencies · One file · Read-only · AI First, human-approved**

</div>

---

![git-sins demo](assets/demo.gif)

> *The gif above is reproducible: `vhs assets/demo.tape` (see [assets/demo.tape](assets/demo.tape)).*

Every repository hides a story nobody puts in the standup: the 3 AM commits, the "wip" avalanche, the branch that rotted for four months, the TODO graveyard. Code review sees the code. **Nobody reviews the history.**

**git-sins** is a confession booth for your git history. It reads the log, the diffs, the TODOs and the branches (read-only, it never modifies anything), runs a deterministic sin engine over the evidence and hands you a **markdown confession**: every sin with its count, its evidence and its penance, a **Sin Score from 0 to 100**, and the one sin you should fix first.

Works on **any repository** — yours, your team's, that open-source project you suspect. It is not a Docker tool; Docker is simply how you deploy it: one image, any repo mounted read-only, confession on stdout.

## ⚡ Quickstart

```bash
# any repo, no install
git clone https://github.com/fernedy/git-sins.git
cd git-sins
python git_sins.py /path/to/any/repo
```

Sample output:

```markdown
## ⛪ Confession — `my-app`

| Evidence | Value |
|---|---|
| Commits analyzed | 412 |
| Merge commits | 3 |
| TODO/FIXME markers | 87 |
| Zombie branches | 2 |

**Sin Score: 62/100 — 🟠 Confession required**
**Dominant sin: 💬 Empty confession (meaningless messages)**

| Sin | Count | Evidence | Penance |
|---|---|---|---|
| 🌑 Nocturnal commits | 14 | Committed between 00:00 and 04:59: "wip" (a1b2c3d: 3h) | Sleep is a feature... |
| 💬 Empty confession | 96 | Subjects that confess nothing: "wip", "fix", "asdf" | A subject line is a promise... |
| 🪦 Debt graveyard | 87 | 87 unfinished-business markers haunting the codebase | Turn the oldest ten into issues... |

Say five descriptive commit messages and three reviewed PRs, and go in peace. ⛪
```

## ⚰️ The nine sins

🌑 **Nocturnal commits** (00:00–04:59) · 💬 **Empty confession** (`wip`, `fix`, `asdf`…) · 🍔 **Gluttony** (mega-commits of 500+ lines) · 🪦 **Debt graveyard** (TODO/FIXME/HACK/XXX) · 🥩 **Vanity versioning** (`final_final_v3`) · 🧟 **Zombie branches** (unmerged, 30+ days) · 👑 **Benevolent dictatorship** (one author ≥ 80%) · 🌊 **Straight to main** (no merges in sight) · 📅 **Crunch days** (20+ commits in one day).

Every sin comes with concrete evidence (hashes, subjects, dates) and a penance you can act on. Full scoring methodology in [docs/SIN-METHODOLOGY.md](docs/SIN-METHODOLOGY.md).

## 🤖 AI First, human-approved

Add `--ai` and your **local** agent CLI (e.g. [opencode](https://opencode.ai)) reads the finished confession and appends an absolution note: the root habit behind the sins, one habit to adopt, one to quit.

- **Opt-in**: without the flag, nothing leaves your machine. Ever.
- **Local**: no API keys, no cloud calls, no telemetry.
- **Human in the loop**: the deterministic report is the source of truth; the AI only annotates it.

## 📣 Confess publicly

Add `--share` and the report ends with a paste-ready badge block:

```markdown
### my-app — Sin Score 62/100 🟠 Confession required
![sin score badge](https://img.shields.io/badge/git__sins-62%2F100-Confession_required-FF8C42?style=flat-square&logo=git)
```

Put your team's repos side by side. The badge wall **is** the retrospective.

## 🧰 All the knobs

```bash
python git_sins.py <repo>          # full confession (markdown)
python git_sins.py <repo> --json   # raw evidence, machine-readable
python git_sins.py <repo> --ai     # + local AI absolution note
python git_sins.py <repo> --share  # + shareable badge block
python git_sins.py <repo> --out confession.md   # also save the report
```

## 🐳 Deployed with Docker

```bash
git clone https://github.com/fernedy/git-sins.git
cd git-sins
docker build -t git-sins .
docker run --rm -v /path/to/any/repo:/repo:ro git-sins /repo --share
```

or with compose:

```bash
SIN_REPO=/path/to/any/repo docker compose run --rm confession /repo --share
```

The repo is mounted **read-only** and the tool only ever runs `log`, `numstat`, `ls-files`, `for-each-ref` and `merge-base`. It never commits, pushes, rebases or writes inside your repo. Reports go to stdout (or `--out` / `./reports`).

## ✅ Tested

```bash
python -m unittest discover -v
```

The suite builds tiny real git repositories in temp dirs and confesses them — 15 tests, no mocks, no network. CI runs on Python 3.8, 3.10 and 3.12. See [`.github/workflows/ci.yml`](.github/workflows/ci.yml).

## 🤝 Contributing

New sins (rebase atrocities, 10k-line lock files, `.orig` conflicts), new penances, new badges. See the sin methodology and open a PR. House rule: **a sin must be provable from git data alone — no heuristics that shame without evidence.**

## 📜 License

MIT — see [LICENSE](LICENSE).

---

<div align="center">

Built AI-first by [Fernedy Arias](https://github.com/fernedy) · Tech Explorer

*If git-sins made your team laugh and then fix something, drop a ⭐ and confess your worst score.*

</div>
