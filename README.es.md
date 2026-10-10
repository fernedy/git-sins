<div align="center">

[🇬🇧 English](README.md) · [🇪🇸 Español](README.es.md)

</div>

<div align="center">

# ⛪ git-sins

**Tu repositorio ha estado guardando secretos. Déjalo confesar.**

![Python](https://img.shields.io/badge/python-3.8%2B-blue?style=flat-square&logo=python&logoColor=white)
![Dependencies](https://img.shields.io/badge/dependencies-0-00A884?style=flat-square)
![Docker](https://img.shields.io/badge/deployed%20with-docker-2496ED?style=flat-square&logo=docker&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-yellow?style=flat-square)

**Cero dependencias · Un archivo · Solo lectura · AI First, con aprobación humana**

</div>

---

![demo de git-sins](assets/demo.gif)

> *El GIF de arriba es reproducible: `vhs assets/demo.tape` (ver [assets/demo.tape](assets/demo.tape)).*

Cada repositorio esconde una historia que nadie cuenta en el daily: los commits de las 3 a.m., la avalancha de "wip", la rama podrida durante cuatro meses, el cementerio de TODOs. El code review ve el código. **Nadie revisa la historia.**

**git-sins** es un confesionario para tu historial de Git. Lee el log, los diffs, los TODOs y las ramas (solo lectura, nunca modifica nada), aplica un motor de pecados determinista sobre la evidencia y te entrega una **confesión en markdown**: cada pecado con su conteo, su evidencia y su penitencia, un **Sin Score de 0 a 100**, y el pecado que deberías arreglar primero.

Funciona con **cualquier repositorio** — el tuyo, el de tu equipo, ese proyecto open source que sospechas. No es una herramienta de Docker; Docker es simplemente cómo se despliega: una imagen, cualquier repo montado en solo lectura, confesión en stdout.

## ⚡ Inicio rápido

```bash
git clone https://github.com/fernedy/git-sins.git
cd git-sins
python git_sins.py /ruta/a/cualquier/repo
```

Ejemplo de salida:

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

## ⚰️ Los nueve pecados

🌑 **Commits nocturnos** (00:00–04:59) · 💬 **Confesión vacía** (`wip`, `fix`, `asdf`…) · 🍔 **Glotonería** (mega-commits de 500+ líneas) · 🪦 **Cementerio de deuda** (TODO/FIXME/HACK/XXX) · 🥩 **Versionado vanidoso** (`final_final_v3`) · 🧟 **Ramas zombi** (sin fusionar, 30+ días) · 👑 **Dictadura benévola** (un autor ≥ 80%) · 🌊 **Directo a main** (ni un merge a la vista) · 📅 **Días de crunch** (20+ commits en un día).

Cada pecado viene con evidencia concreta (hashes, subjects, fechas) y una penitencia accionable. Metodología completa de puntuación en [docs/SIN-METHODOLOGY.md](docs/SIN-METHODOLOGY.md).

## 🤖 AI First, con aprobación humana

Añade `--ai` y tu CLI de agente **local** (p. ej. [opencode](https://opencode.ai)) lee la confesión terminada y añade una nota de absolución: el hábito raíz detrás de los pecados, un hábito que adoptar y uno que abandonar.

- **Opt-in**: sin la bandera, nada sale de tu máquina. Nunca.
- **Local**: sin API keys, sin nube, sin telemetría.
- **Humano en el ciclo**: el reporte determinista es la fuente de verdad; la IA solo lo anota.

## 📣 Confiesa en público

Añade `--share` y el reporte termina con un bloque de insignia listo para pegar:

```markdown
### my-app — Sin Score 62/100 🟠 Confession required
![sin score badge](https://img.shields.io/badge/git__sins-62%2F100-Confession_required-FF8C42?style=flat-square&logo=git)
```

Pon los repos de tu equipo lado a lado. El muro de insignias **es** la retrospectiva.

## 🧰 Todos los controles

```bash
python git_sins.py <repo>          # confesión completa (markdown)
python git_sins.py <repo> --json   # evidencia cruda, legible por máquinas
python git_sins.py <repo> --ai     # + nota de absolución con IA local
python git_sins.py <repo> --share  # + bloque de insignia compartible
python git_sins.py <repo> --out confession.md   # también guarda el reporte
```

## 🐳 Desplegado con Docker

```bash
git clone https://github.com/fernedy/git-sins.git
cd git-sins
docker build -t git-sins .
docker run --rm -v /ruta/a/cualquier/repo:/repo:ro git-sins /repo --share
```

o con compose:

```bash
SIN_REPO=/ruta/a/cualquier/repo docker compose run --rm confession /repo --share
```

El repo se monta en **solo lectura** y la herramienta solo ejecuta `log`, `numstat`, `ls-files`, `for-each-ref` y `merge-base`. Nunca hace commit, push, rebase ni escribe dentro de tu repo. Los reportes van a stdout (o `--out` / `./reports`).

## ✅ Probado

```bash
python -m unittest discover -v
```

La suite construye mini repos de git reales en directorios temporales y los confiesa — 15 tests, sin mocks, sin red. CI corre en Python 3.8, 3.10 y 3.12. Ver [`.github/workflows/ci.yml`](.github/workflows/ci.yml).

## 🤝 Contribuir

Nuevos pecados (atrocidades de rebase, lockfiles de 10k líneas, conflictos `.orig`), nuevas penitencias, nuevas insignias. Regla de la casa: **un pecado debe ser demostrable solo con datos de git — nada de heurísticas que avergüencen sin evidencia.**

## 📜 Licencia

MIT — ver [LICENSE](LICENSE).

---

<div align="center">

Built AI-first by [Fernedy Arias](https://github.com/fernedy) · Tech Explorer

*Si git-sins hizo reír a tu equipo y luego arreglar algo, dale una ⭐ y confiesa tu peor puntaje.*

</div>
