# KurtzQuest

**A terminal game where AI agents reason their way through a hostile palace, first with logic, then with probability, then across a river with a Markov Decision Process.**

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Rich](https://img.shields.io/badge/UI-Rich-4B8BBE)
![AI](https://img.shields.io/badge/AI-Logic%20%7C%20Bayes%20%7C%20MDP-8A2BE2)

Captain Willard has to find Colonel Kurtz inside a ruined palace and get both of them out alive. The palace hides deadly pits and an enemy soldier, the exit is unknown, and the agent only perceives its immediate surroundings. KurtzQuest implements the same mission with three classic AI paradigms. You can play each one yourself or watch an autonomous agent solve it.

> Final project for *Fundamentals of Artificial Intelligence*, Universidad Pontificia Comillas (ICAI), 2025/26.

---

## The three missions

| Module | Paradigm | What the agent does |
|---|---|---|
| `kurtz.py` | **Propositional logic / model checking** | Builds a knowledge base from percepts (breeze, snore, glow, scream) and enumerates every world consistent with them to *prove* which cells are safe and where the exit is. An autonomous **BFS agent** plans paths through proven-safe cells, with backtracking when it gets stuck. |
| `palacio.py` | **Bayesian reasoning under uncertainty** | Keeps a probability map (belief) for each hazard type, the soldier and the exit, updating it after every percept. A **greedy agent** scores moves by risk, exploration value and exit probability, with loop detection and an "escape mode", and decides when it is worth throwing the grenade. |
| `river_mdp.py` | **Markov Decision Process** | Crossing a river whose current drags you downstream with column-dependent probability. The optimal policy is computed with **value iteration** and evaluated through Monte Carlo simulation. |

### Example: river MDP and its optimal policy

```
                Environment                       ╭──────────────────────────╮
┏━━━━━┳━━━━━┳━━━━━┳━━━━━┳━━━━━┳━━━━━┳━━━━━┓       │      Optimal policy      │
┃ i\j ┃  0  ┃  1  ┃  2  ┃  3  ┃  4  ┃  5  ┃       │  →   →   →   →   →    E  │
┃ r_s ┃ 0.0 ┃ 0.1 ┃ 0.3 ┃ 0.3 ┃ 0.7 ┃ 0.0 ┃       │  ↑   ↑   ↑   I   →    ↑  │
┡━━━━━╇━━━━━╇━━━━━╇━━━━━╇━━━━━╇━━━━━╇━━━━━┩       │  →   →   →   →   →    ↑  │
│   0 │  ·  │  R  │  R  │  R  │  R  │  E  │       │  ↑   ↑   I   →   →    ↑  │
│   1 │  ·  │  R  │  R  │  I  │  R  │  ·  │       │  →   →   →   →   →    ↑  │
│   2 │  ·  │  R  │  R  │  R  │  R  │  ·  │       │ CW   →   →   →   →    ↑  │
│   3 │  ·  │  R  │  I  │  R  │  R  │  ·  │       ╰──────────────────────────╯
│   4 │  ·  │  R  │  R  │  R  │  R  │  ·  │
│   5 │ CW  │  R  │  R  │  R  │  R  │  ·  │
└─────┴─────┴─────┴─────┴─────┴─────┴─────┘
```

`R` = river (row `r_s` is the probability of being dragged one cell down), `I` = island, `E` = exit. With `seed=42`, the computed policy reaches the exit in **200 out of 200** simulated crossings.

## Highlights

- **Sound logical inference**: a cell is only marked safe if it is safe in *every* world consistent with the knowledge base. The exit is only declared known when all consistent worlds agree on it.
- **Two levels of uncertainty**: deterministic logic (`kurtz.py`) versus probabilistic beliefs with renormalisation and contradiction detection (`palacio.py`).
- **Planning and decision-making**: BFS path planning with backtracking, a tunable greedy risk/reward policy, and value iteration for a stochastic MDP.
- **Polished terminal UI** built with [Rich](https://github.com/Textualize/rich): live maps of the agent's knowledge, probability heatmaps, menus and game-over screens.

## Getting started

```bash
git clone https://github.com/javmartineez/KurtzQuest.git
cd KurtzQuest
pip install -r requirements.txt
```

Run any of the three missions:

```bash
python kurtz.py        # Mission 1: logic-based agent (manual or BFS)
python palacio.py      # Mission 2: Bayesian beliefs (manual or greedy agent)
python river_mdp.py    # Mission 3: river MDP with value iteration
```

**Controls** (missions 1 and 2): `W/A/S/D` to move, `G` + direction to throw the grenade, `E` to leave through the exit once you have found Kurtz.

## Project structure

```
KurtzQuest/
├── kurtz.py              # Mission 1: game loop, transition model, manual and BFS agents
├── knowledge_base.py     # Logical knowledge base (model checking over consistent worlds)
├── entorno_palacio1.py   # Palace generation and rendering for mission 1
├── palacio.py            # Mission 2: Bayesian beliefs and greedy agent
├── entorno_palacio2.py   # Palace generation and probability heatmaps for mission 2
├── river_mdp.py          # Mission 3: river MDP, value iteration and simulation
└── requirements.txt
```

## Tech stack

Python · NumPy · Rich · pyfiglet

## Author

**Javier Martínez Berenguer** · [GitHub](https://github.com/javmartineez)
