import numpy as np 
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich.panel import Panel
from rich.columns import Columns

def crear_entorno(N: int = 6):
    """
    Randomly generates the initial palace environment, including
    the board layout and the location of the key game elements.
    The starting cell (0,0) is always reserved as a safe starting position.

    Args:
        - N (int): size of the palace (N x N). Defaults to 6.

    Returns:
        - palacio (np.ndarray): matrix representing the game board,
          where each cell may contain:
          - None (empty cell),
          - "P" (pit),
          - "S" (enemy soldier),
          - "CK" (Colonel Kurtz).
        - pos_soldado (tuple[int, int]): position of the enemy soldier.
        - pos_kurtz (tuple[int, int]): position of Colonel Kurtz.
        - pos_salida (tuple[int, int]): position of the palace exit.
    """

    NUM_TRAMPAS = 3
    NUM_SOLDADOS = 1

    palacio = np.full((N,N), None, dtype=object)                                              

    indices_posibles = np.arange(1, N * N)                                                              # 1 to 35 - (0,0) must always be the starting cell
    indices = np.random.choice(indices_posibles, 
                               size=NUM_TRAMPAS + NUM_SOLDADOS + 2, 
                               replace=False)    #Pick random positions for the traps (making sure they are not in the same cell and that (0,0) is not one of them)
    posiciones_random = [(i // N, i % N) for i in indices]  

    pos_soldado = posiciones_random[0]  
    pos_kurtz = posiciones_random[1]
    pos_salida = posiciones_random[2]
    
    palacio[pos_kurtz] = "CK"  
    palacio[pos_soldado] = "S"          

    for p in posiciones_random[3:]:
        palacio[p] = "P"

    return palacio, pos_soldado, pos_kurtz, pos_salida

def render(
    console,
    N: int,
    pos_agente: tuple[int, int],
    has_kurtz: bool,
    visited: set[tuple[int, int]],
    safe: set[tuple[int, int]],
    possible_pits: set[tuple[int, int]],
    possible_soldier: set[tuple[int, int]],
    show_exit_if_known: bool = False,
    exit_pos: tuple[int, int] | None = None,
):
    """
    Renders the palace map in the console from the perspective of the agent's
    current knowledge, showing its position, the visited cells, the safe
    cells and the possible threats inferred from the KB.

    Args:
        - console (Console): Rich console used to render the interface.
        - N (int): size of the palace (N x N).
        - pos_agente (tuple[int, int]): current position of Captain Willard.
        - has_kurtz (bool): whether the agent has already found Colonel Kurtz.
        - visited (set[tuple[int, int]]): set of cells already visited by the agent.
        - safe (set[tuple[int, int]]): set of cells deduced to be safe.
        - possible_pits (set[tuple[int, int]]): cells that might contain a pit.
        - possible_soldier (set[tuple[int, int]]): cells that might contain the enemy soldier.
        - show_exit_if_known (bool): whether the exit should be shown once its position
          has been deduced with certainty.
        - exit_pos (tuple[int, int] | None): exit position if known; None otherwise.
    """

    table = Table(show_header=False, box=None)
    for _ in range(N):
        table.add_column(justify="center", width=6)

    for i in range(N):
        row = []
        for j in range(N):
            pos = (i, j)

            if pos == pos_agente:
                estilo = "bold purple" if has_kurtz else "bold orange1"
                cell = Text("CW", style=estilo)

            elif show_exit_if_known and (exit_pos is not None) and pos == exit_pos:
                cell = Text("•", style="bold green")

            elif pos in visited:
                cell = Text("•", style="bold blue")

            elif pos in safe:
                cell = Text("✓", style="bold cyan")

            else:
                is_p = pos in possible_pits
                is_s = pos in possible_soldier
                if is_p and is_s:
                    cell = Text("?!", style="bold red")
                elif is_p:
                    cell = Text("P?", style="bold white")
                elif is_s:
                    cell = Text("S?", style="bold yellow")
                else:
                    cell = Text("·", style="dim")

            row.append(cell)
        table.add_row(*row)

    # Map panel: FIT (does not take up the whole terminal)
    map_panel = Panel.fit(
        Align.center(table),
        title="Palace (agent knowledge)",
        border_style="cyan",
        padding=(1, 2),
    )

    # Legend panel: FIT as well
    legend_text = Text.from_markup(
        "[bold]Legend[/bold]\n\n"
        "[blue]•[/blue] visited\n"
        "[bold cyan]✓[/bold cyan] safe\n"
        "[bold white]P?[/bold white] possible pit\n"
        "[bold yellow]S?[/bold yellow] possible soldier\n"
        "[bold red]?![/bold red] possible danger\n"
        "[bold green]•[/bold green] exit (if known)\n"
        "[bold purple]CW[/bold purple] CK found"
    )
    legend_panel = Panel.fit(
        legend_text,
        border_style="cyan",
        padding=(1, 2),
    )

    console.print(
        Align.center(
            Columns([map_panel, legend_panel], expand=False, equal=False, padding=(0, 2))
        )
    )