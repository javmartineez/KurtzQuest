import numpy as np 
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich.panel import Panel
from rich.columns import Columns

def crear_entorno(N: int = 6):

    # Cada celda guarda un conjunto de elementos (permite solapamientos)
    palacio = np.empty((N, N), dtype=object)
    for i in range(N):
        for j in range(N):
            palacio[i, j] = set()

    indices_posibles = np.arange(1, N * N)  # excluye (0,0)

    # Trampas: pueden solaparse
    indices_trampas = np.random.choice(indices_posibles, size=3, replace=True)
    posiciones_trampas = [(i // N, i % N) for i in indices_trampas]

    pos_F = posiciones_trampas[0]
    pos_P = posiciones_trampas[1]
    pos_D = posiciones_trampas[2]

    palacio[pos_F].add("F")
    palacio[pos_P].add("P")
    palacio[pos_D].add("D")

    # Resto (M, S, CK): en celdas SIN trampas (pero pueden coincidir entre sí)
    indices_posibles_resto = [
        i for i in indices_posibles
        if len(palacio[i // N, i % N] & {"F", "P", "D"}) == 0
    ]

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
    
    N = mundo["N"]
    pos = estado["agent_pos"]

    # Mapas exigidos por el enunciado:
    # 1) trampa cualquiera = suma de tipos (intuición)
    trampa_any = belief.F + belief.P + belief.D

    # 2) soldado (si ya está muerto, todo 0)
    soldado = belief.M.copy()
    if not estado["soldado_vivo"]:
        soldado[:] = 0.0

    # 3) salida
    salida = belief.S

    p_estado = tabla_estado(N, pos, estado["has_kurtz"], belief.visitadas)
    p_trampa = tabla_heatmap(N, trampa_any, "P(trampa cualquiera)", pos_agente=pos, has_kurtz=estado["has_kurtz"])
    p_sold = tabla_heatmap(N, soldado, "P(soldado)", pos_agente=pos, has_kurtz=estado["has_kurtz"])
    p_sal  = tabla_heatmap(N, salida, "P(salida)", pos_agente=pos, has_kurtz=estado["has_kurtz"])

    legend = Text.from_markup(
        "[bold]Info[/bold]\n\n"
        f"Pos: {pos}\n"
        f"has_kurtz: {estado['has_kurtz']}\n"
        f"soldado_vivo: {estado['soldado_vivo']}\n"
        f"granada: {estado['granada']}\n\n"
        "[bold]Colores[/bold]\n"
        "[dim]<0.01[/dim]  "
        "[cyan]0.01-0.05[/cyan]  "
        "[green]0.05-0.15[/green]  "
        "[yellow]0.15-0.30[/yellow]  "
        "[orange1]0.30-0.60[/orange1]  "
        "[red]>0.60[/red]"
    )
    p_legend = Panel.fit(legend, border_style="cyan", padding=(1, 2))

    console.clear()
    console.print(Align.center(Columns([p_estado, p_trampa, p_sold, p_sal], padding=(0, 2))))

def tabla_heatmap(N: int, matriz, title: str, pos_agente=None, has_kurtz=False):
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
        title="Palacio (estado del agente)",
        border_style="cyan",
        padding=(1, 2),
    )

def estilo_prob(p: float) -> str:
    p = max(0.0, min(1.0, p))
    p = p ** 0.4 

    r = 255
    g = int(255 * (1 - p))
    b = int(255 * (1 - p))

    return f"bold rgb({r},{g},{b})"

