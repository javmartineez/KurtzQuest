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
    Genera el entorno del río para el juego, creando una cuadrícula con un punto
    de inicio, una salida, islas intermedias y una fuerza de corriente asociada
    a cada columna del río.

    Args:
        - N (int): tamaño del tablero del río (N x N).
        - n_islas (int): número de islas a generar en el interior del río.
        - seed (int | None): semilla para el generador aleatorio, para reproducibilidad.

    Returns:
        - rio (np.ndarray): matriz que representa el tablero del río con sus elementos.
        - start (tuple[int, int]): posición inicial del agente.
        - exit_pos (tuple[int, int]): posición de la salida del río.
        - islas (set[tuple[int, int]]): conjunto de posiciones ocupadas por islas.
        - river_strength (list[float]): lista con la fuerza de la corriente por columna.
    """

    if seed is not None:
        random.seed(seed)

    if n_islas > (N - 2) ** 2:
        raise ValueError("Demasiadas islas para el tamaño del río.")

    start_row = random.randrange(0,N)
    start_pos = (start_row, 0)
    exit_row = random.randrange(0, N)
    exit_pos = (exit_row, N - 1)

    # Fuerza del río por columnas
    river_strength = []
    for j in range(N):
        if j == 0 or j == N - 1:
            river_strength.append(0.0)
        else:
            river_strength.append(round(random.uniform(0.06, 0.94), 1))

    rio = np.full((N, N), None, dtype=object)

    # Río solo en columnas interiores
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
               islas: set, river_strength: list[float], title="Entorno"):
    """
    Renderiza en consola el entorno del río, mostrando la posición inicial, la salida,
    las islas y el cauce del río, junto con la fuerza de la corriente asociada a cada columna.

    Args:
        - console (Console): consola Rich utilizada para mostrar la tabla.
        - rio (np.ndarray): matriz que representa el tablero del río.
        - start (tuple[int, int]): posición inicial del agente.
        - exit_pos (tuple[int, int]): posición de la salida del río.
        - islas (set[tuple[int, int]]): conjunto de posiciones ocupadas por islas.
        - river_strength (list[float]): fuerza de la corriente por columna del río.
        - title (str): título mostrado en la tabla de renderizado.
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
                # río / orilla
                if j == 0 or j == N-1:
                    cell = Text("·", style="dim")
                else:
                    cell = Text("R", style="cyan")

            row.append(cell)
        t.add_row(*row)

    console.print(t)

def render_politica(console: Console, rio, start, exit_pos, islas, politica, title="Política óptima"):
    """
    Muestra en consola la política óptima sobre el tablero del río mediante flechas,
    indicando la acción recomendada en cada celda.

    Args:
        - console (Console): consola Rich utilizada para el renderizado.
        - rio (np.ndarray): matriz que representa el entorno del río.
        - start (tuple[int, int]): posición inicial del agente.
        - exit_pos (tuple[int, int]): posición de la salida.
        - islas (set[tuple[int, int]]): posiciones ocupadas por islas.
        - politica (dict): política óptima que asigna una acción a cada celda.
        - title (str): título del panel mostrado.
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
    Genera la lista de todos los estados posibles del entorno del río.
    Args:
        - rio (np.ndarray): matriz que representa el tablero del río.

    Returns:
        - estados (list[tuple[int, int]]): lista de todas las posiciones (i, j) del tablero.
    """

    N = rio.shape[0]
    return [(i, j) for i in range(N) for j in range(N)]

def acciones():
    """
    Devuelve el conjunto de acciones disponibles desde un estado dado.
    Returns:
        - acciones (list[str] | set[str]): acciones permitidas en el entorno.
    """
    return ACCIONES

def transicion(
    s: tuple[int, int],
    a: str,
    rio,
    river_strength: list[float]
    ) -> dict[tuple[int, int], float]:
    """
    Función de transición estocástica del entorno del río.
    Dado un estado y una acción, devuelve la distribución de probabilidad
    sobre los posibles estados siguientes, teniendo en cuenta la corriente
    del río y las celdas bloqueadas (bordes e islas).

    Args:
        - s (tuple[int, int]): estado actual (posición en el río).
        - a (str): acción ejecutada ("up", "down", "left", "right" o "stay").
        - rio (np.ndarray): matriz que representa el entorno del río.
        - river_strength (list[float]): probabilidad de ser arrastrado hacia abajo
          por la corriente en cada columna.

    Returns:
        - dist (dict[tuple[int, int], float]): distribución de probabilidad sobre
          los estados siguientes.
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

    # Acción stay
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
        raise ValueError(f"Acción desconocida: {a}")

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
    Función de recompensa del entorno del río.
    Premia alcanzar la salida, penaliza intentar moverse contra una isla
    y aplica un coste por cada paso.

    Args:
        - s (tuple[int, int]): estado actual (posición en el río).
        - a (str): acción ejecutada ("up", "down", "left", "right" o "stay").
        - s_next (tuple[int, int]): estado siguiente tras aplicar la acción.
        - rio (np.ndarray): matriz que representa el entorno del río.

    Returns:
        - recompensa (int): valor de la recompensa
    """

    i2, j2 = s_next

    if rio[i2, j2] == "E":
        return 100

    if a != "stay" and s_next == s:  #detecto que quería moverme y no he podido. Puede ser por isla o por salirse del tablero
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
    Aplica el algoritmo de value iteration para calcular el valor
    óptimo de todos los estados del río.

    Args:
        - estados (list[tuple[int, int]]): lista de todos los estados posibles.
        - rio (np.ndarray): matriz que representa el entorno del río.
        - river_strength (list[float]): fuerza de la corriente por columna.
        - gamma (float): factor de descuento.
        - epsilon (float): umbral de convergencia.

    Returns:
        - V (dict): función de valor óptima para cada estado.
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

        if delta < epsilon: #el cambio ya es despreciable (o directamente no existe)
            break

    return V

def extraer_politica(estados: list, V: dict, rio: np.ndarray, river_strength: list[float], gamma: float=0.9) -> dict:
    """
    Extrae la política óptima a partir de una función de valor ya calculada,
    eligiendo en cada estado la acción que maximiza el valor esperado.

    Args:
        - estados (list[tuple[int, int]]): lista de todos los estados posibles.
        - V (dict): función de valor de los estados.
        - rio (np.ndarray): matriz que representa el entorno del río.
        - river_strength (list[float]): fuerza de la corriente por columna.
        - gamma (float): factor de descuento.

    Returns:
        - politica (dict): política óptima que asigna una acción a cada estado.
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
    Muestra aleatoriamente un estado siguiente a partir de una distribución
    de probabilidad discreta. También conocido como roulette wheel selection.

    Args:
        - dist (dict[tuple[int, int], float]): distribución de probabilidad sobre
          los posibles estados siguientes.

    Returns:
        - s_next (tuple[int, int]): estado siguiente muestreado según la distribución.
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
    Simula una o varias partidas siguiendo una política fija en el entorno del río,
    acumulando estadísticas de éxito, pasos y recompensa total.

    Args:
        - politica (dict): política que asigna una acción a cada estado.
        - rio (np.ndarray): matriz que representa el entorno del río.
        - river_strength (list[float]): fuerza de la corriente por columna.
        - start (tuple[int, int]): estado inicial de cada partida.
        - n_partidas (int): número de partidas a simular.
        - max_pasos (int): número máximo de pasos por partida.
        - paso_a_paso (bool): si True, muestra la simulación paso a paso.
        - console (Console | None): consola Rich para el modo paso a paso.

    Returns:
        - victorias (int): número de partidas en las que se alcanza la salida.
        - pasos (list[int]): lista con el número de pasos de cada partida.
        - recompensas (list[int]): lista con la recompensa total de cada partida.
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
                    f"[dim]Paso {num_pasos}[/dim]  "
                    f"estado={estado}  "
                    f"acción=[bold]{accion}[/bold]  "
                    f"r={r_paso}  "
                    f"R={recompensa_total}"
                )

        # Comprobación final
        if not exito:
            i, j = estado
            if rio[i, j] == "E":
                exito = True

        victorias += int(exito)
        pasos.append(num_pasos)
        recompensas.append(recompensa_total)

        # El modo paso a paso solo tiene sentido para una partida
        if paso_a_paso and n_partidas != 1:
            paso_a_paso = False

    return victorias, pasos, recompensas

def main():
    """
    Función de flujo principal
    """
    console = Console()

    seed = 42

    while True:
        # 1) Crear entorno
        rio, start, exit_pos, islas, river_strength = crear_entorno(seed=seed)

        # 2) Resolver con Value Iteration
        estados = crear_estados(rio)
        V = value_iteration(estados, rio, river_strength)
        politica = extraer_politica(estados, V, rio, river_strength)

        console.clear()
        console.print(Panel.fit(f"RÍO MDP | seed={seed}", border_style="cyan"))

        console.print("[bold]Entorno:[/bold]")
        render_rio(console, rio, start, exit_pos, islas, river_strength)
        render_politica(console, rio, start, exit_pos, islas, politica)

        console.print("\n[bold cyan]Opciones[/bold cyan]")
        console.print("1) Simular 1 partida (paso a paso)")
        console.print("2) Simular N partidas (estadísticas)")
        console.print("3) Cambiar seed")
        console.print("4) Salir")

        op = Prompt.ask("Elige", choices=["1", "2", "3", "4"], default="2")

        if op == "1":
            console.print()
            victorias, pasos, recompensas = simular_partidas(
                politica, rio, river_strength, start,
                n_partidas=1, max_pasos=300,
                paso_a_paso=True, console=console
            )

            ok = (victorias == 1)
            console.print(Panel.fit(
                f"Resultado: {'LLEGA' if ok else 'NO LLEGA'}\n"
                f"Pasos: {pasos[0]}\n"
                f"Recompensa total: {recompensas[0]}",  
                border_style="green" if ok else "red"
            ))
            Prompt.ask("ENTER para continuar", default="")

        elif op == "2":
            n = IntPrompt.ask("¿Cuántas partidas quieres simular?", default=100)

            victorias, pasos, recompensas = simular_partidas(
                politica, rio, river_strength, start,
                n_partidas=n, max_pasos=300
            )

            tasa = 100.0 * victorias / n
            pasos_medios = sum(pasos) / n
            recompensa_media = sum(recompensas) / n

            t = Table(title="Resumen simulaciones", show_header=True, header_style="bold cyan")
            t.add_column("N", justify="right")
            t.add_column("Éxitos", justify="right")
            t.add_column("Tasa éxito", justify="right")
            t.add_column("Pasos medios", justify="right")
            t.add_column("Recompensa media", justify="right")

            t.add_row(str(n), str(victorias), f"{tasa:.1f}%", f"{pasos_medios:.2f}", f"{recompensa_media:.2f}")
            console.print(t)
            Prompt.ask("ENTER para continuar", default="")

        elif op == "3":
            seed = IntPrompt.ask("Nueva seed", default=seed)

        elif op == "4":
            break

if __name__ == "__main__":
    main()

