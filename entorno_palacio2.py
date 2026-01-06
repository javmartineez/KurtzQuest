import numpy as np 
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich.panel import Panel
from rich.columns import Columns

def crear_entorno(N: int = 6):
    """
    Genera el tablero del palacio (N x N) asignando aleatoriamente los elementos del entorno.
    En esta versión las trampas (F, P, D) pueden coincidir en la misma celda, y el resto de
    elementos (M, S, CK) se colocan en celdas sin trampas, pudiendo también coincidir entre ellos.

    Args:
        - N (int): dimensión del palacio (N x N).

    Returns:
        - palacio (np.ndarray): matriz de tamaño N x N donde cada celda contiene un set con
          los elementos presentes en esa posición.
        - pos_F (tuple[int, int]): posición de la trampa F.
        - pos_P (tuple[int, int]): posición de la trampa P.
        - pos_D (tuple[int, int]): posición de la trampa D.
        - pos_M (tuple[int, int]): posición del elemento M.
        - pos_S (tuple[int, int]): posición del soldado S.
        - pos_CK (tuple[int, int]): posición del Coronel Kurtz (CK).
    """

    # En esta version se permiten dos peligros en una misma celda
    palacio = np.empty((N, N), dtype=object)
    for i in range(N):
        for j in range(N):
            palacio[i, j] = set()

    indices_posibles = np.arange(1, N * N)  # se excluye (0,0)

    indices_trampas = np.random.choice(indices_posibles, size=3, replace=True)
    posiciones_trampas = [(i // N, i % N) for i in indices_trampas]

    pos_F = posiciones_trampas[0]
    pos_P = posiciones_trampas[1]
    pos_D = posiciones_trampas[2]

    palacio[pos_F].add("F")
    palacio[pos_P].add("P")
    palacio[pos_D].add("D")

    # Resto (M, S, CK): en celdas SIN trampas (pero pueden coincidir entre sí)
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
    Renderiza la interfaz mostrando el estado del agente y mapas de calor
    con las probabilidades (belief) de trampas, soldado y salida en cada celda.

    Args:
        - console (Console): consola Rich utilizada para renderizar la interfaz.
        - mundo (dict): información del entorno (incluye el tamaño N).
        - estado (dict): estado actual del agente (posición, granada, flags).
        - belief (object): estructura que contiene las distribuciones de probabilidad y visitadas.
    """

    N = mundo["N"]
    pos = estado["agent_pos"]

    trampa_any = belief.F + belief.P + belief.D

    soldado = belief.M.copy()
    if not estado["soldado_vivo"]:
        soldado[:] = 0.0

    salida = belief.S

    p_estado = tabla_estado(N, pos, estado["has_kurtz"], belief.visitadas)
    p_trampa = tabla_heatmap(N, trampa_any, "P(trampa cualquiera)", pos_agente=pos, has_kurtz=estado["has_kurtz"])
    p_M = tabla_heatmap(N, soldado, "P(soldado)", pos_agente=pos, has_kurtz=estado["has_kurtz"])
    p_sal  = tabla_heatmap(N, salida, "P(salida)", pos_agente=pos, has_kurtz=estado["has_kurtz"])

    console.clear()
    console.print(Align.center(Columns([p_estado, p_trampa, p_M, p_sal], padding=(0, 2))))

def tabla_heatmap(N: int, matriz, title: str, pos_agente=None, has_kurtz=False):
    """
    Construye una tabla tipo heatmap que representa una matriz de probabilidades
    sobre el palacio, codificando visualmente los valores mediante colores.

    Args:
        - N (int): tamaño del palacio (N x N).
        - matriz (array-like): matriz de probabilidades a representar.
        - title (str): título que se mostrará en el panel.
        - pos_agente (tuple[int, int] | None): posición actual del agente, que se
          destacará visualmente si se proporciona.
        - has_kurtz (bool): indica si el agente ya ha encontrado a Kurtz, para
          modificar su estilo de representación.

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
        title="Palacio (estado del agente)",
        border_style="cyan",
        padding=(1, 2),
    )

def estilo_prob(p: float) -> str:
    """
    Calcula el color asociado a una probabilidad para su representación 
    en el heatmap, utilizando un gradiente de blanco a rojo.

    Args:
        - p (float): valor de probabilidad a representar, esperado en el rango [0, 1].

    Returns:
        - estilo (str): cadena de estilo Rich en formato RGB.
    """

    p = max(0.0, min(1.0, p))
    p = p ** 0.4 

    r = 255
    g = int(255 * (1 - p))
    b = int(255 * (1 - p))

    return f"bold rgb({r},{g},{b})"

