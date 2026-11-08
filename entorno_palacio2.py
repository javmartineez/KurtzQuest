import numpy as np 
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich.panel import Panel
from rich.columns import Columns

def crear_entorno(N: int = 6):
    """
    Generates the palace board (N x N) by randomly placing the environment elements.
    In this version the traps (F, P, D) may share the same cell, and the remaining
    elements (M, S, CK) are placed in trap-free cells, where they may also overlap.

    Args:
        - N (int): size of the palace (N x N).

    Returns:
        - palacio (np.ndarray): N x N matrix where each cell holds a set with
          the elements present at that position.
        - pos_F (tuple[int, int]): position of trap F.
        - pos_P (tuple[int, int]): position of trap P.
        - pos_D (tuple[int, int]): position of trap D.
        - pos_M (tuple[int, int]): position of element M.
        - pos_S (tuple[int, int]): position of soldier S.
        - pos_CK (tuple[int, int]): position of Colonel Kurtz (CK).
    """

    # In this version two hazards are allowed in the same cell
    palacio = np.empty((N, N), dtype=object)
    for i in range(N):
        for j in range(N):
            palacio[i, j] = set()

    indices_posibles = np.arange(1, N * N)  # (0,0) is excluded

    indices_trampas = np.random.choice(indices_posibles, size=3, replace=True)
    posiciones_trampas = [(i // N, i % N) for i in indices_trampas]

    pos_F = posiciones_trampas[0]
    pos_P = posiciones_trampas[1]
    pos_D = posiciones_trampas[2]

    palacio[pos_F].add("F")
    palacio[pos_P].add("P")
    palacio[pos_D].add("D")

    # Others (M, S, CK): in cells WITHOUT traps (but they may overlap with each other)
    indices_posibles_resto = [i for i in indices_posibles if len(palacio[i // N, i % N] & {"F", "P", "D"}) == 0]

    indices_resto = np.random.choice(indices_posibles_resto, size=3, replace=True)
    posiciones_resto = [(i // N, i % N) for i in indices_resto]

    pos_M = posiciones_resto[0]
    pos_S = posiciones_resto[1]
    pos_CK = posiciones_resto[2]

    palacio[pos_M].add("M")
    palacio[pos_S].add("S")
    palacio[pos_CK].add("CK")

    return palacio, pos_F, pos_P, pos_D, pos_M, pos_S, pos_CK

def render_bayes(console: Console, mundo: dict, estado: dict, belief):
    """
    Renders the interface showing the agent's state and heat maps
    with the probabilities (belief) of traps, soldier and exit in each cell.

    Args:
        - console (Console): Rich console used to render the interface.
        - mundo (dict): environment information (includes the size N).
        - estado (dict): current agent state (position, grenade, flags).
        - belief (object): structure holding the probability distributions and visited cells.
    """

    N = mundo["N"]
    pos = estado["agent_pos"]

    trampa_any = belief.F + belief.P + belief.D

    soldado = belief.M.copy()
    if not estado["soldado_vivo"]:
        soldado[:] = 0.0

    salida = belief.S

    p_estado = tabla_estado(N, pos, estado["has_kurtz"], belief.visitadas)
    p_trampa = tabla_heatmap(N, trampa_any, "P(any trap)", pos_agente=pos, has_kurtz=estado["has_kurtz"])
    p_M = tabla_heatmap(N, soldado, "P(soldier)", pos_agente=pos, has_kurtz=estado["has_kurtz"])
    p_sal  = tabla_heatmap(N, salida, "P(exit)", pos_agente=pos, has_kurtz=estado["has_kurtz"])

    console.clear()
    console.print(Align.center(Columns([p_estado, p_trampa, p_M, p_sal], padding=(0, 2))))

def tabla_heatmap(N: int, matriz, title: str, pos_agente=None, has_kurtz=False):
    """
    Builds a heatmap-style table representing a probability matrix
    over the palace, visually encoding the values with colours.

    Args:
        - N (int): size of the palace (N x N).
        - matriz (array-like): probability matrix to display.
        - title (str): title shown on the panel.
        - pos_agente (tuple[int, int] | None): current position of the agent, which is
          highlighted if provided.
        - has_kurtz (bool): whether the agent has already found Kurtz, to
          change how it is displayed.

    """

    t = Table(show_header=False, box=None)
    for _ in range(N):
        t.add_column(justify="center", width=6)

    for i in range(N):
        row = []
        for j in range(N):
            p = float(matriz[i, j])
            txt = f"{p:.2f}"
            style = estilo_prob(p)

            if pos_agente == (i, j):
                txt = "CW"
                style = "bold purple" if has_kurtz else "bold orange1"

            row.append(Text(txt, style=style))
        t.add_row(*row)

    return Panel.fit(Align.center(t), title=title, border_style="cyan", padding=(1, 2))

def tabla_estado(N: int, pos_agente, has_kurtz, visited):
    t = Table(show_header=False, box=None)
    for _ in range(N):
        t.add_column(justify="center", width=6)

    for i in range(N):
        row = []
        for j in range(N):
            pos = (i, j)
            if pos == pos_agente:
                estilo = "bold purple" if has_kurtz else "bold orange1"
                cell = Text("CW", style=estilo)
            elif pos in visited:
                cell = Text("•", style="bold blue")
            else:
                cell = Text("·", style="dim")
            row.append(cell)
        t.add_row(*row)

    return Panel.fit(
        Align.center(t),
        title="Palace (agent state)",
        border_style="cyan",
        padding=(1, 2),
    )

def estilo_prob(p: float) -> str:
    """
    Computes the colour associated with a probability for display
    in the heatmap, using a white-to-red gradient.

    Args:
        - p (float): probability value to display, expected in the range [0, 1].

    Returns:
        - estilo (str): Rich style string in RGB format.
    """

    p = max(0.0, min(1.0, p))
    p = p ** 0.4 

    r = 255
    g = int(255 * (1 - p))
    b = int(255 * (1 - p))

    return f"bold rgb({r},{g},{b})"

