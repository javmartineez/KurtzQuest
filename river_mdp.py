import random
import numpy as np
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.prompt import IntPrompt, Prompt


ACCIONES = ["up", "down", "left", "right", "stay"]
FLECHAS = {"up": "↑", "down": "↓", "left": "←", "right": "→", "stay": "•"}

def crear_entorno(N: int = 6, n_islas: int = 2, seed: int | None = None):
    """
    Generates the river environment for the game, creating a grid with a
    starting point, an exit, intermediate islands and a current strength associated
    with each river column.

    Args:
        - N (int): size of the river board (N x N).
        - n_islas (int): number of islands to generate inside the river.
        - seed (int | None): seed for the random generator, for reproducibility.

    Returns:
        - rio (np.ndarray): matrix representing the river board and its elements.
        - start (tuple[int, int]): starting position of the agent.
        - exit_pos (tuple[int, int]): position of the river exit.
        - islas (set[tuple[int, int]]): set of positions occupied by islands.
        - river_strength (list[float]): list with the current strength per column.
    """

    if seed is not None:
        random.seed(seed)

    if n_islas > (N - 2) ** 2:
        raise ValueError("Too many islands for the size of the river.")

    start_row = random.randrange(0,N)
    start_pos = (start_row, 0)
    exit_row = random.randrange(0, N)
    exit_pos = (exit_row, N - 1)

    # River strength per column
    river_strength = []
    for j in range(N):
        if j == 0 or j == N - 1:
            river_strength.append(0.0)
        else:
            river_strength.append(round(random.uniform(0.06, 0.94), 1))

    rio = np.full((N, N), None, dtype=object)

    # River only in the inner columns
    for j in range(1, N - 1):
        for i in range(N):
            rio[i, j] = "R"

    posibles_islas = [
        (i, j)
        for i in range(1, N - 1)
        for j in range(1, N - 1)
        ]

    islas = set(random.sample(posibles_islas, k=n_islas))

    for pos in islas:
        rio[pos] = "I"

    rio[start_pos] = "CWCK"
    rio[exit_pos] = "E"

    return rio, start_pos, exit_pos, islas, river_strength

def render_rio(console: Console, rio: np.ndarray, start: tuple, exit_pos: tuple, 
               islas: set, river_strength: list[float], title="Environment"):
    """
    Renders the river environment in the console, showing the starting position, the exit,
    the islands and the riverbed, along with the current strength of each column.

    Args:
        - console (Console): Rich console used to display the table.
        - rio (np.ndarray): matrix representing the river board.
        - start (tuple[int, int]): starting position of the agent.
        - exit_pos (tuple[int, int]): position of the river exit.
        - islas (set[tuple[int, int]]): set of positions occupied by islands.
        - river_strength (list[float]): current strength per river column.
        - title (str): title shown on the rendered table.
    """

    N = rio.shape[0]
    t = Table(title=title, show_header=True, header_style="bold cyan")

    t.add_column("i\\j\nr_s", justify="right")
    for j in range(N):
        if j == 0 or j == N-1:
            t.add_column(f"{j}\n0.0", justify="center")
        else:
            t.add_column(f"{j}\n{river_strength[j]:.1f}", justify="center")

    for i in range(N):
        row = [str(i)]
        for j in range(N):
            pos = (i, j)

            if pos == start:
                cell = Text("CW", style="bold orange1")
            elif pos == exit_pos:
                cell = Text("E", style="bold green")
            elif pos in islas:
                cell = Text("I", style="bold red")
            else:
                # river / bank
                if j == 0 or j == N-1:
                    cell = Text("·", style="dim")
                else:
                    cell = Text("R", style="cyan")

            row.append(cell)
        t.add_row(*row)

    console.print(t)

def render_politica(console: Console, rio, start, exit_pos, islas, politica, title="Optimal policy"):
    """
    Displays the optimal policy over the river board using arrows,
    showing the recommended action in each cell.

    Args:
        - console (Console): Rich console used for rendering.
        - rio (np.ndarray): matrix representing the river environment.
        - start (tuple[int, int]): starting position of the agent.
        - exit_pos (tuple[int, int]): position of the exit.
        - islas (set[tuple[int, int]]): positions occupied by islands.
        - politica (dict): optimal policy mapping each cell to an action.
        - title (str): title of the displayed panel.
    """
    
    N = rio.shape[0]
    t = Table(title=title, show_header=False, box=None, pad_edge=False)
    for _ in range(N):
        t.add_column(justify="center", width=2)

    for i in range(N):
        row = []
        for j in range(N):
            pos = (i, j)
            if pos == start:
                row.append(Text("CW", style="bold orange1"))
            elif pos == exit_pos:
                row.append(Text("E", style="bold green"))
            elif pos in islas:
                row.append(Text("I", style="bold red"))
            else:
                a = politica.get(pos, "stay")
                row.append(Text(FLECHAS.get(a, "?"), style="bold"))
        t.add_row(*row)

    console.print(Panel.fit(t, border_style="cyan"))

def crear_estados(rio: np.ndarray):
    """
    Generates the list of all possible states of the river environment.
    Args:
        - rio (np.ndarray): matrix representing the river board.

    Returns:
        - estados (list[tuple[int, int]]): list of every position (i, j) on the board.
    """

    N = rio.shape[0]
    return [(i, j) for i in range(N) for j in range(N)]

def acciones():
    """
    Returns the set of actions available from a given state.
    Returns:
        - acciones (list[str] | set[str]): actions allowed in the environment.
    """
    return ACCIONES

def transicion(
    s: tuple[int, int],
    a: str,
    rio,
    river_strength: list[float]
    ) -> dict[tuple[int, int], float]:
    """
    Stochastic transition function of the river environment.
    Given a state and an action, returns the probability distribution
    over the possible next states, taking into account the river current
    and the blocked cells (edges and islands).

    Args:
        - s (tuple[int, int]): current state (position in the river).
        - a (str): action taken ("up", "down", "left", "right" or "stay").
        - rio (np.ndarray): matrix representing the river environment.
        - river_strength (list[float]): probability of being dragged down
          by the current in each column.

    Returns:
        - dist (dict[tuple[int, int], float]): probability distribution over
          the next states.
    """
    i, j = s
    N = rio.shape[0]

    def bloqueado(pos):
        x, y = pos
        return (
            x < 0 or x >= N or
            y < 0 or y >= N or
            rio[x, y] == "I"
        )

    # Stay action
    if a == "stay":
        return {s: 1.0}


    if a == "down":
        s_dir = (i + 1, j)
        if bloqueado(s_dir):
            return {s: 1.0}
        return {s_dir: 1.0}

    p_down = river_strength[j]
    p_dir = 1.0 - p_down

    if a == "up":
        s_dir = (i - 1, j)
    elif a == "left":
        s_dir = (i, j - 1)
    elif a == "right":
        s_dir = (i, j + 1)
    else:
        raise ValueError(f"Unknown action: {a}")

    dist = {}

    if bloqueado(s_dir):
        dist[s] = dist.get(s, 0.0) + p_dir
    else:
        dist[s_dir] = dist.get(s_dir, 0.0) + p_dir

    s_down = (i + 1, j)
    if bloqueado(s_down):
        dist[s] = dist.get(s, 0.0) + p_down
    else:
        dist[s_down] = dist.get(s_down, 0.0) + p_down

    return dist

def recompensa(s: tuple[int, int], a: str, s_next: tuple[int, int], rio: np.ndarray) -> int:
    """
    Reward function of the river environment.
    Rewards reaching the exit, penalises trying to move into an island
    and applies a cost for every step.

    Args:
        - s (tuple[int, int]): current state (position in the river).
        - a (str): action taken ("up", "down", "left", "right" or "stay").
        - s_next (tuple[int, int]): next state after applying the action.
        - rio (np.ndarray): matrix representing the river environment.

    Returns:
        - recompensa (int): reward value
    """

    i2, j2 = s_next

    if rio[i2, j2] == "E":
        return 100

    if a != "stay" and s_next == s:  #detect that I tried to move and could not. It may be due to an island or to leaving the board
        N = rio.shape[0]
        i, j = s
        if a == "up":
            target = (i-1, j)
        elif a == "down":
            target = (i+1, j)
        elif a == "left":
            target = (i, j-1)
        elif a == "right":
            target = (i, j+1)
        else:
            target = None

        if target is not None:
            x, y = target
            if 0 <= x < N and 0 <= y < N and rio[x, y] == "I":
                return -100

    return -1

def value_iteration(estados: list, rio: np.ndarray, river_strength: list[float], gamma: float=0.9, epsilon: float=1e-6) -> dict:
    """
    Applies the value iteration algorithm to compute the optimal
    value of every river state.

    Args:
        - estados (list[tuple[int, int]]): list of all possible states.
        - rio (np.ndarray): matrix representing the river environment.
        - river_strength (list[float]): current strength per column.
        - gamma (float): discount factor.
        - epsilon (float): convergence threshold.

    Returns:
        - V (dict): optimal value function for each state.
    """


    V = {s: 0.0 for s in estados}

    while True:
        delta = 0.0

        for s in estados:
            mejor_valor = float("-inf")

            for a in acciones():
                valor = 0.0
                dist = transicion(s, a, rio, river_strength)

                for s_next, p in dist.items():
                    valor += p * (recompensa(s, a, s_next, rio) + gamma * V[s_next])

                if valor > mejor_valor:
                    mejor_valor = valor

            delta = max(delta, abs(mejor_valor - V[s]))
            V[s] = mejor_valor

        if delta < epsilon: #the change is now negligible (or nonexistent)
            break

    return V

def extraer_politica(estados: list, V: dict, rio: np.ndarray, river_strength: list[float], gamma: float=0.9) -> dict:
    """
    Extracts the optimal policy from an already computed value function,
    choosing in each state the action that maximises the expected value.

    Args:
        - estados (list[tuple[int, int]]): list of all possible states.
        - V (dict): state value function.
        - rio (np.ndarray): matrix representing the river environment.
        - river_strength (list[float]): current strength per column.
        - gamma (float): discount factor.

    Returns:
        - politica (dict): optimal policy mapping each state to an action.
    """
    politica = {}

    for s in estados:
        mejor_accion = None
        mejor_valor = float("-inf")

        for a in acciones():
            valor = 0.0
            dist = transicion(s, a, rio, river_strength)

            for s_next, p in dist.items():
                valor += p * (recompensa(s, a, s_next, rio) + gamma * V[s_next])

            if valor > mejor_valor:
                mejor_valor = valor
                mejor_accion = a

        politica[s] = mejor_accion

    return politica

def muestrear_siguiente(dist: dict[tuple[int, int], float]) -> tuple[int, int]:
    """
    Randomly samples a next state from a discrete probability
    distribution. Also known as roulette wheel selection.

    Args:
        - dist (dict[tuple[int, int], float]): probability distribution over
          the possible next states.

    Returns:
        - s_next (tuple[int, int]): next state sampled from the distribution.
    """
    r = random.random()
    acumulado = 0.0
    for s_next, p in dist.items():
        acumulado += p
        if r <= acumulado:
            return s_next
    return next(reversed(dist))  

def simular_partidas(
    politica: dict,
    rio: np.ndarray,
    river_strength: list[float],
    start: tuple[int, int],
    n_partidas: int = 1,
    max_pasos: int = 300,
    paso_a_paso: bool = False,
    console: bool = None
    ):
    """
    Simulates one or more games following a fixed policy in the river environment,
    collecting statistics on success, steps and total reward.

    Args:
        - politica (dict): policy mapping each state to an action.
        - rio (np.ndarray): matrix representing the river environment.
        - river_strength (list[float]): current strength per column.
        - start (tuple[int, int]): initial state of each game.
        - n_partidas (int): number of games to simulate.
        - max_pasos (int): maximum number of steps per game.
        - paso_a_paso (bool): if True, shows the simulation step by step.
        - console (Console | None): Rich console for the step-by-step mode.

    Returns:
        - victorias (int): number of games in which the exit is reached.
        - pasos (list[int]): list with the number of steps of each game.
        - recompensas (list[int]): list with the total reward of each game.
    """


    victorias = 0
    pasos = []
    recompensas = []

    for k in range(n_partidas):
        estado = start
        recompensa_total = 0
        num_pasos = 0
        exito = False

        for _ in range(max_pasos):
            i, j = estado

            if rio[i, j] == "E":
                exito = True
                break

            accion = politica[estado]
            dist = transicion(estado, accion, rio, river_strength)
            s_next = muestrear_siguiente(dist)

            r_paso = recompensa(estado, accion, s_next, rio)
            recompensa_total += r_paso
            estado = s_next
            num_pasos += 1

            if paso_a_paso and n_partidas == 1 and console is not None:
                console.print(
                    f"[dim]Step {num_pasos}[/dim]  "
                    f"state={estado}  "
                    f"action=[bold]{accion}[/bold]  "
                    f"r={r_paso}  "
                    f"R={recompensa_total}"
                )

        # Final check
        if not exito:
            i, j = estado
            if rio[i, j] == "E":
                exito = True

        victorias += int(exito)
        pasos.append(num_pasos)
        recompensas.append(recompensa_total)

        # Step-by-step mode only makes sense for a single game
        if paso_a_paso and n_partidas != 1:
            paso_a_paso = False

    return victorias, pasos, recompensas

def main():
    """
    Main program flow
    """
    console = Console()

    seed = 42

    while True:
        # 1) Create the environment
        rio, start, exit_pos, islas, river_strength = crear_entorno(seed=seed)

        # 2) Solve with Value Iteration
        estados = crear_estados(rio)
        V = value_iteration(estados, rio, river_strength)
        politica = extraer_politica(estados, V, rio, river_strength)

        console.clear()
        console.print(Panel.fit(f"RIVER MDP | seed={seed}", border_style="cyan"))

        console.print("[bold]Environment:[/bold]")
        render_rio(console, rio, start, exit_pos, islas, river_strength)
        render_politica(console, rio, start, exit_pos, islas, politica)

        console.print("\n[bold cyan]Options[/bold cyan]")
        console.print("1) Simulate 1 game (step by step)")
        console.print("2) Simulate N games (statistics)")
        console.print("3) Change seed")
        console.print("4) Quit")

        op = Prompt.ask("Choose", choices=["1", "2", "3", "4"], default="2")

        if op == "1":
            console.print()
            victorias, pasos, recompensas = simular_partidas(
                politica, rio, river_strength, start,
                n_partidas=1, max_pasos=300,
                paso_a_paso=True, console=console
            )

            ok = (victorias == 1)
            console.print(Panel.fit(
                f"Result: {'REACHED' if ok else 'NOT REACHED'}\n"
                f"Steps: {pasos[0]}\n"
                f"Total reward: {recompensas[0]}",  
                border_style="green" if ok else "red"
            ))
            Prompt.ask("Press ENTER to continue", default="")

        elif op == "2":
            n = IntPrompt.ask("How many games do you want to simulate?", default=100)

            victorias, pasos, recompensas = simular_partidas(
                politica, rio, river_strength, start,
                n_partidas=n, max_pasos=300
            )

            tasa = 100.0 * victorias / n
            pasos_medios = sum(pasos) / n
            recompensa_media = sum(recompensas) / n

            t = Table(title="Simulation summary", show_header=True, header_style="bold cyan")
            t.add_column("N", justify="right")
            t.add_column("Successes", justify="right")
            t.add_column("Success rate", justify="right")
            t.add_column("Mean steps", justify="right")
            t.add_column("Mean reward", justify="right")

            t.add_row(str(n), str(victorias), f"{tasa:.1f}%", f"{pasos_medios:.2f}", f"{recompensa_media:.2f}")
            console.print(t)
            Prompt.ask("Press ENTER to continue", default="")

        elif op == "3":
            seed = IntPrompt.ask("New seed", default=seed)

        elif op == "4":
            break

if __name__ == "__main__":
    main()

