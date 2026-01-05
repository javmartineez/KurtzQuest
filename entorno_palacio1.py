import numpy as np 
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich.panel import Panel
from rich.columns import Columns

def crear_entorno(N: int = 6):
    """
    Genera de forma aleatoria el entorno inicial del palacio, incluyendo
    la disposición del tablero y la ubicación de los elementos clave del juego.
    La celda inicial (0,0) se reserva siempre como posición segura de inicio.

    Args:
        - N (int): dimensión del palacio (N x N). Por defecto, 6.

    Returns:
        - palacio (np.ndarray): matriz que representa el tablero del juego,
          donde cada celda puede contener:
          - None (celda vacía),
          - "P" (precipicio),
          - "S" (soldado enemigo),
          - "CK" (Coronel Kurtz).
        - pos_soldado (tuple[int, int]): posición del soldado enemigo.
        - pos_kurtz (tuple[int, int]): posición del Coronel Kurtz.
        - pos_salida (tuple[int, int]): posición de la salida del palacio.
    """

    NUM_TRAMPAS = 3
    NUM_SOLDADOS = 1

    palacio = np.full((N,N), None, dtype=object)                                              

    indices_posibles = np.arange(1, N * N)                                                              # del 1 al 35 - el (0,0) siempre debe ser la casilla inicial
    indices = np.random.choice(indices_posibles, 
                               size=NUM_TRAMPAS + NUM_SOLDADOS + 2, 
                               replace=False)    #Escogemos posiciones aleatorias para las trampas (asegurando que no estén en la misma casilla y que el (0,0) no sea una de ellas)
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
    Renderiza en consola el mapa del palacio desde la perspectiva del conocimiento
    actual del agente, mostrando su posición, las celdas visitadas, las celdas
    seguras y las posibles amenazas sacadas a paritr de la KB.

    Args:
        - console (Console): consola Rich utilizada para renderizar la interfaz.
        - N (int): tamaño del palacio (N x N).
        - pos_agente (tuple[int, int]): posición actual del Capitán Willard.
        - has_kurtz (bool): indica si el agente ya ha encontrado al Coronel Kurtz.
        - visited (set[tuple[int, int]]): conjunto de celdas ya visitadas por el agente.
        - safe (set[tuple[int, int]]): conjunto de celdas deducidas como seguras.
        - possible_pits (set[tuple[int, int]]): celdas que podrían contener un precipicio.
        - possible_soldier (set[tuple[int, int]]): celdas que podrían contener al soldado enemigo.
        - show_exit_if_known (bool): indica si debe mostrarse la salida cuando su posición
          ha sido deducida con certeza.
        - exit_pos (tuple[int, int] | None): posición de la salida si es conocida; None en caso contrario.
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

    # Panel del mapa: FIT (no ocupa toda la terminal)
    map_panel = Panel.fit(
        Align.center(table),
        title="Palacio (conocimiento del agente)",
        border_style="cyan",
        padding=(1, 2),
    )

    # Panel de leyenda: FIT también
    legend_text = Text.from_markup(
        "[bold]Leyenda[/bold]\n\n"
        "[blue]•[/blue] visitado\n"
        "[bold cyan]✓[/bold cyan] seguro\n"
        "[bold white]P?[/bold white] posible precipicio\n"
        "[bold yellow]S?[/bold yellow] posible soldado\n"
        "[bold red]?![/bold red] posible peligro\n"
        "[bold green]•[/bold green] salida (si conocida)\n"
        "[bold purple]CW[/bold purple] CK encontrado"
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