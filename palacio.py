import entorno_palacio2
import numpy as np
from rich.panel import Panel
from rich.align import Align
from rich.console import Console
from rich.text import Text 
from rich.table import Table
from rich.columns import Columns
import time
import pyfiglet
from collections import deque, defaultdict
import math

def bienvenida(console: Console) -> str:
    """
    Shows the game's main menu and asks the user for the game mode.

    Args:
        - console (Console): Rich console used to display the interface.

    Returns:
        - game_mode (str): option selected by the user.
    """
    console.clear()

    figlet = pyfiglet.Figlet(font="slant")
    titulo = figlet.renderText("FINDING \nCOLONEL\nKURTZ vol.2")

    titulo = Text(titulo, style="bold cyan", justify="center")
    console.print(Panel(Align.center(titulo), border_style="cyan", padding=(1, 4)))

    # Options panel
    opciones = (
        "[bold cyan]1.[/bold cyan] [bold]How to play?[/bold]  [dim]→ rules and controls[/dim]\n"
        "[bold cyan]2.[/bold cyan] [bold]Manual game mode[/bold]  [dim]→ you choose the actions[/dim]\n"
        "[bold cyan]3.[/bold cyan] [bold]Algorithm mode[/bold]  [dim]→ BFS[/dim]\n"
        "[bold cyan]4.[/bold cyan] [bold]Quit[/bold]"
    )

    console.print(
        Panel(
            Align.left(Text.from_markup(opciones)),
            title="[bold]Main menu[/bold]",
            title_align="left",
            border_style="cyan",
            padding=(1, 4),
        )
    )

    while True:
        game_mode = input("Choose a mode [1/2/3/4]: ").strip()
        if game_mode in {"1", "2", "3", "4"}:
            return game_mode
        console.print("[bold red]Invalid input.[/bold red] Type 1, 2, 3 or 4.")

def instrucciones(console: Console) -> None:
    """
    Displays the mission instructions and the game controls.

    Args:
        - console (Console): Rich console used to display the text panels.
    """
    console.clear()

    titulo1 = Text("MISSION BRIEFING", style="bold cyan", justify="center")
    titulo2 = Text("CONTROLS", style="bold cyan", justify="center")

    instrucciones = (
        "[bold cyan]SECOND PHASE:[/bold cyan] Reasoning under uncertainty\n"
        "You must find [bold magenta]Colonel Kurtz (CK)[/bold magenta] and get out of the palace alive, "
        "but in this phase the environment is uncertain and you only have partial information, obtained through your percepts.\n\n"
        "To help you decide, the system shows [bold]four maps[/bold] at the same time:\n\n"
        "[bold cyan]1. Exploration map[/bold cyan]\n"
        "Shows the rooms you have already been through. "
        "Visited cells are marked so you can follow your route.\n"
        "[bold cyan]2. Trap map[/bold cyan]\n"
        "Shows the [bold]probability that a room contains a deadly trap[/bold]. "
        "The colour indicates the risk: the more intense, the higher the chance of running into one.\n"
        "[bold cyan]3. Soldier map[/bold cyan]\n"
        "Shows the [bold]probability of running into the enemy soldier[/bold] in each room. "
        "Remember that the soldier is lethal while alive, but you can eliminate him with the grenade.\n"
        "[bold cyan]4. Exit map[/bold cyan]\n"
        "Shows the [bold]probability that a room is the palace exit[/bold]. "
        "As you explore and perceive the environment, this map gets refined.\n\n"
        "Your goal remains the same: find Kurtz and get out alive. "
        "[bold]Good luck, captain.[/bold]"
    )

    controles = (
        "Use [bold cyan]W/A/S/D[/bold cyan] to move up/left/down/right respectively.\n"
        "Use [bold cyan]G[/bold cyan] to throw the grenade. After pressing it, you must specify "
        "the throwing direction with W/A/S/D\n"
        "Once you find the exit, press [bold cyan]E[/bold cyan] to leave"
    )

    console.print(
        Panel(
            Align.center(titulo1),
            border_style="cyan",
            padding=(1, 4),
        )
    )

    console.print(
        Panel(
            Text.from_markup(instrucciones),
            border_style="cyan",
            padding=(1, 4),
        )
    )

    console.print(
        Panel(
            Align.center(titulo2),
            border_style="cyan",
            padding=(1, 4),
        )
    )

    console.print(
        Panel(
            Text.from_markup(controles),
            border_style="cyan",
            padding=(1, 4),
        )
    )

    console.input("\nPress ENTER to go back to the menu...")

def pantalla_carga(console: Console, segundos: float = 1.0) -> None:
    """
    Shows a simulated loading screen with a console spinner.

    Args:
        - console (Console)
        - segundos (float): duration of the loading screen in seconds.
    """

    console.clear()
    with console.status("[bold]Preparing the palace...[/bold]", spinner="dots"):
        time.sleep(segundos)

def inicializar_palacio(N: int = 6):
    """
    Initialises the palace environment by generating the board and
    the agent's initial state, and shows a loading screen
    before the game starts.

    Args:
        - N (int): size of the palace (N x N). Defaults to 6.

    Returns:
        - mundo (dict): dictionary holding the palace board
                        and the size of the environment.
        - estado_0 (dict): agent's initial state, including position,
                           soldier status, grenade and internal flags.
    """

    console = Console()
    pantalla_carga(console)

    palacio, _, _, _, _, _, _ = entorno_palacio2.crear_entorno(N)

    estado_0 = {
        "agent_pos": (0, 0),
        "has_kurtz": False,
        "soldado_vivo": True,
        "granada": True,
        "ultima_accion_matar_soldado": False
    }

    mundo = {
        "palacio": palacio,
        "N": N
    }

    return mundo, estado_0

def pantalla_game_over(console: Console, texto: str, color: str):
    """
    Shows a screen after the game ends.

    Args:
        - console (Console): Rich console used to render the screen.
        - texto (str): main text displayed as ASCII art.
        - color (str): colour used for the text and the panel border.
    """

    console.clear()
    fig = pyfiglet.Figlet(font="doom")
    art = fig.renderText(texto)

    console.print(
        Panel(
            Align.center(Text(art, style=f"bold {color}")),
            border_style=color,
            padding=(1, 4),
        )
    )

def menu_post_partida(console: Console) -> str:
    """
    Shows the post-game menu and asks the user what to do next:
    retry, go back to the main menu or quit the program.

    Args:
        - console (Console): Rich console used to display the options panel.

    Returns:
        - opcion (str): option chosen by the user ("1", "2" or "3").
    """

    opciones = (
        "[bold cyan]1.[/bold cyan] Retry\n"
        "[bold green]2.[/bold green] Back to the main menu\n"
        "[bold red]3.[/bold red] Quit"
    )
    console.print(
        Panel(
            Align.left(Text.from_markup(opciones)),
            title="[bold]What do you want to do now?[/bold]",
            title_align="left",
            border_style="cyan",
            padding=(1, 4),
        )
    )

    while True:
        x = input("Choose [1/2/3]: ").strip()
        if x in {"1", "2", "3"}:
            return x
        console.print("[bold red]Invalid input.[/bold red] Type 1, 2 or 3.")

def percept(estado: dict, mundo: dict) -> list[bool]:
    """
    Computes the agent's percept from its current position, detecting the
    presence of elements (F, P, D, M, S) in the area made up of the current cell
    and its neighbours, as well as walls and the scream after killing the soldier.

    Args:
        - estado (dict): current agent state (position, flags and soldier status).
        - mundo (dict): environment information (board and size N).

    Returns:
        - perceptos (list[bool]): list of booleans in the following order:
          [e_F, e_P, e_D, e_M, e_S, wall_up, wall_down, wall_left, wall_right, scream].
    """
  
    N = mundo["N"]

    palacio = mundo["palacio"]

    pos = estado["agent_pos"]
    vecinos = neighbours(pos, N)
    zona = vecinos + [pos]

    e_S = any("S" in palacio[v] for v in zona)
    e_M = estado["soldado_vivo"] and any("M" in palacio[v] for v in zona)

    e_F = any("F" in palacio[v] for v in zona)
    e_P = any("P" in palacio[v] for v in zona)
    e_D = any("D" in palacio[v] for v in zona)

    pared_arriba, pared_abajo, pared_izq, pared_der = comprobar_paredes(pos, mundo["N"])

    grito = estado["ultima_accion_matar_soldado"]

    perceptos = [e_F, e_P, e_D, e_M, e_S, pared_arriba, pared_abajo, pared_izq, pared_der, grito]
    return perceptos

def comprobar_paredes(pos: tuple, N: int) -> tuple[bool]:
    """
    Determines whether there are walls around a given position.

    Args:
        - pos (tuple[int, int]): current position (row, column) of the agent.
        - N (int): size of the palace (N x N).

    Returns:
        - pared_arriba (bool): wall above
        - pared_abajo (bool): wall below
        - pared_izquierda (bool): wall to the left
        - pared_derecha (bool): wall to the right
    """

    i, j = pos

    pared_arriba = (i == 0)
    pared_abajo = (i == N - 1)
    pared_izq = (j == 0)
    pared_der = (j == N - 1)

    return pared_arriba, pared_abajo, pared_izq, pared_der

def neighbours(pos: tuple[int, int], N: int) -> list[tuple[int, int]]:
    """
    Returns the valid neighbouring cells (up, down, left and right)
    of a given position within the board.

    Args:
        - pos (tuple[int, int]): current position (row, column).
        - N (int): size of the palace (N x N).

    Returns:
        - vecinos (list[tuple[int, int]]): list of neighbouring cells within the board limits.
    """
    i, j = pos
    cand = [(i-1, j), (i+1, j), (i, j-1), (i, j+1)]
    return [(x, y) for x, y in cand if 0 <= x < N and 0 <= y < N]

class Beliefs:
    """
    Keeps probability distributions (N x N matrices) for each type of palace
    element (F, P, D, M, S) and the set of cells visited by the agent.
    """

    def __init__(self, N):
        """
        Initialises the beliefs with a uniform prior over the board, excluding
        the starting cell (0,0), which is assumed to be safe.

        Args:
            - N (int): size of the palace (N x N).
        """
        self.N = N
        self.F = self.prior()
        self.P = self.prior()
        self.D = self.prior()
        self.M = self.prior()
        self.S = self.prior()
        self.visitadas = set()

    def prior(self):
        """
        Generates a uniform prior over every board cell except the starting one (0,0).

        Returns:
            - prior (np.ndarray): normalised N x N matrix with zero probability at (0,0).
        """
        P = np.ones((self.N, self.N), dtype=float)
        P[0, 0] = 0.0
        P /= P.sum()
        return P

    def update(self, P, pos, vecinos, estimulo):
        """
        Updates a probability distribution based on an observed stimulus.
        If the stimulus is True, the element must be in the area (current cell or neighbours).
        If the stimulus is False, the element cannot be in that area.
        After applying the constraint, the matrix is renormalised.

        Args:
            - P (np.ndarray): probability matrix to update.
            - pos (tuple[int, int]): current position of the agent.
            - vecinos (list[tuple[int, int]]): neighbours of the current position.
            - estimulo (bool): whether the stimulus associated with the element is present.
        """
        zona = set(vecinos + [pos])

        if estimulo:
            for i in range(self.N):
                for j in range(self.N):
                    if (i, j) not in zona:
                        P[i, j] = 0.0
        else:
            for (i, j) in zona:
                P[i, j] = 0.0

        s = P.sum()
        if s == 0:
            raise ValueError("Contradiction")
        P /= s

def renormalizar(P: np.ndarray) -> np.ndarray:
    """
    Renormalises a probability matrix so that it sums to 1.
    If the total mass is 0, raises an exception due to a contradiction.

    Args:
        - P (np.ndarray): probability matrix to renormalise.

    Returns:
        - P_norm (np.ndarray): renormalised matrix summing to 1.
    """
    s = P.sum()
    if s == 0:
        raise ValueError("Contradiction: renormalising with zero mass")
    return P / s

def update_beliefs(beliefs: Beliefs, estado: dict, mundo: dict, perceptos: list) -> None:
    """
    Updates the agent's Bayesian beliefs from the observed percept,
    applying presence/absence constraints on F, P, D, M and S in the area
    (current cell + neighbours), handling the soldier's death and giving
    zero probability to visited cells.

    Args:
        - beliefs (Beliefs): structure holding the agent's probability distributions.
        - estado (dict): current agent state (position, flags and soldier status).
        - mundo (dict): environment information (includes N and the board).
        - perceptos (list[bool]): list of percepts in the order:
          [e_F, e_P, e_D, e_M, e_S, wall_up, wall_down, wall_left, wall_right, scream].
    """

    N = mundo["N"]
    pos = estado["agent_pos"]
    vecinos = neighbours(pos, N)

    e_F, e_P, e_D, e_M, e_S = perceptos[0], perceptos[1], perceptos[2], perceptos[3], perceptos[4]
    grito = perceptos[9]

    #if there is a scream, the soldier no longer exists
    if grito:
        estado["soldado_vivo"] = False
        beliefs.M[:] = 0.0
    else:
        # Updating M only makes sense if the soldier is still alive
        if estado.get("soldado_vivo", True):
            beliefs.update(beliefs.M, pos, vecinos, e_M)

    beliefs.update(beliefs.F, pos, vecinos, e_F)
    beliefs.update(beliefs.P, pos, vecinos, e_P)
    beliefs.update(beliefs.D, pos, vecinos, e_D)
    beliefs.update(beliefs.S, pos, vecinos, e_S)

    beliefs.visitadas.add(pos)

    #If the agent is alive, the probability of danger here is 0
    for v in beliefs.visitadas:
        beliefs.F[v] = 0.0
        beliefs.P[v] = 0.0
        beliefs.D[v] = 0.0
        beliefs.M[v] = 0.0


    beliefs.F = renormalizar(beliefs.F)
    beliefs.P = renormalizar(beliefs.P)
    beliefs.D = renormalizar(beliefs.D)

    if estado.get("soldado_vivo", True) and not grito:
        beliefs.M = renormalizar(beliefs.M)

class AgenteGreedy:
    """
    Greedy agent that chooses moves by maximising a score that combines:
    - estimated risk of dying when entering a cell (traps + soldier)
    - preference for exploring unvisited cells
    - preference for approaching the exit once Kurtz has been found
    - a penalty for loops
    It can also throw the grenade if it detects a high probability of the soldier in a neighbour.
    """

    def __init__(
        self,
        p_umbral: float = 0.20,
        w_risk: float = 10.0,
        w_exit: float = 2.0,
        w_explore: float = 0.6,
        grenade_trigger: float = 0.55,
        eps: float = 1e-9,
        recent_len: int = 12,
        loop_trigger: int = 4,
        w_recent: float = 2.5,
        w_visit: float = 0.8,
    ):
        """
        Initialises the greedy agent and its decision parameters.

        Args:
            - p_umbral (float): "acceptable" risk threshold when moving (options below it are prioritised).
            - w_risk (float): weight of the risk in the score (higher = more conservative).
            - w_exit (float): weight of the exit probability (only applied if has_kurtz is True).
            - w_explore (float): bonus for exploring unvisited cells.
            - grenade_trigger (float): threshold to throw the grenade if P(soldier in neighbour) exceeds it.
            - eps (float): numerical tolerance when comparing risks with the threshold.
            - recent_len (int): length of the short-term memory used to detect and penalise loops.
            - loop_trigger (int): number of times the current position appears in recent memory to trigger escape mode.
            - w_recent (float): penalty for returning to cells in the recent history.
            - w_visit (float): penalty for visiting cells too many times (logarithmic).
        """
        self.umbral_riesgo = p_umbral
        self.peso_riesgo = w_risk
        self.peso_salida = w_exit
        self.peso_explorar = w_explore
        self.umbral_granada = grenade_trigger
        self.eps = eps

        self.reciente = deque(maxlen=recent_len)
        self.conteo_visitas = defaultdict(int)

        self.disparador_bucle = loop_trigger
        self.peso_reciente = w_recent
        self.peso_visitas = w_visit

    def tope(self, x: float) -> float:
        """
        Clamps a value to the [0, 1] interval to avoid invalid probabilities.

        Args:
            - x (float): value to clamp.

        Returns:
            - x_acotado (float): value within [0, 1].
        """
        if x < 0.0:
            return 0.0
        if x > 1.0:
            return 1.0
        return x

    def decidir(self, estado: dict, beliefs, mundo: dict) -> str:
        """
        Decides the next action based on the beliefs and the current state.
        Main priorities:
        - leave if Kurtz is already with you and the exit probability of the cell is almost 1
        - throw the grenade if there is a high probability of the soldier in an adjacent cell
        - pick the neighbour with the best score, avoiding loops
        If there are no valid neighbours, returns "BLOCKED".

        Args:
            - estado (dict): agent state (positions and flags: has_kurtz, soldado_vivo, granada).
            - beliefs (Beliefs): structure with the F/P/D/M/S probability matrices and visited set.
            - mundo (dict): environment information (includes the size N).

        Returns:
            - accion (str): selected action ("UP", "DOWN", "LEFT", "RIGHT", "EXIT" or "GRENADE_DIR").
        """
        N = mundo["N"]
        posicion = estado["agent_pos"]
        vecinos = neighbours(posicion, N)

        tiene_kurtz = bool(estado.get("has_kurtz", False))
        soldado_vivo = bool(estado.get("soldado_vivo", True))
        tiene_granada = bool(estado.get("granada", False))

        # 0) Leave if you can already win and are practically sure to be on the exit
        if tiene_kurtz and float(beliefs.S[posicion]) > 0.99:
            return "EXIT"

        # 1) Memory
        self.conteo_visitas[posicion] += 1
        self.reciente.append(posicion)

        repeticiones_aqui = 0
        for p in self.reciente:
            if p == posicion:
                repeticiones_aqui += 1
        modo_escape = repeticiones_aqui >= self.disparador_bucle

        # 2) Grenade
        if soldado_vivo and tiene_granada and vecinos:
            mejor_vecino = None
            mejor_prob = 0.0

            for vecino in vecinos:
                p_militar = self.tope(float(beliefs.M[vecino]))
                if p_militar > mejor_prob:
                    mejor_prob, mejor_vecino = p_militar, vecino

            if mejor_vecino is not None and mejor_prob >= self.umbral_granada:
                return self.accion_granada(posicion, mejor_vecino)

        # 3) Evaluate candidates
        candidatos = []
        for vecino in vecinos:
            p_trampa = self.tope(float(beliefs.F[vecino] + beliefs.P[vecino] + beliefs.D[vecino]))
            p_soldado = self.tope(float(beliefs.M[vecino])) if soldado_vivo else 0.0

            riesgo = 1.0 - (1.0 - p_trampa) * (1.0 - p_soldado)
            riesgo = self.tope(riesgo)

            p_salida = self.tope(float(beliefs.S[vecino])) if tiene_kurtz else 0.0

            no_visitada = 1.0 if vecino not in beliefs.visitadas else 0.0

            pen_reciente = 1.0 if vecino in self.reciente else 0.0
            pen_visitas = math.log1p(self.conteo_visitas.get(vecino, 0))

            peso_reciente_eff = self.peso_reciente * (2.0 if modo_escape else 1.0)
            peso_visitas_eff = self.peso_visitas * (1.5 if modo_escape else 1.0)

            umbral_eff = self.umbral_riesgo * (1.3 if modo_escape else 1.0)
            if umbral_eff > 0.95:
                umbral_eff = 0.95

            puntuacion = (
                - self.peso_riesgo * riesgo
                + self.peso_salida * p_salida
                + self.peso_explorar * no_visitada
                - peso_reciente_eff * pen_reciente
                - peso_visitas_eff * pen_visitas
            )

            candidatos.append((vecino, puntuacion, riesgo, no_visitada, pen_reciente, pen_visitas, umbral_eff))

        if not candidatos:
            return "BLOCKED"

        # 4) pick the best one by score
        umbral_eff = candidatos[0][6]
        opciones_seguras = []
        for candidato in candidatos:
            if candidato[2] <= umbral_eff + self.eps:
                opciones_seguras.append(candidato)

        def clave_mejor(c):
            return (c[1], -c[2], -c[4], c[3], -c[5])

        if opciones_seguras:
            mejor = max(opciones_seguras, key=clave_mejor)
        else:
            mejor = min(candidatos, key=lambda c: (c[2], c[4], c[5], -c[3], -c[1]))

        return self.accion(posicion, mejor[0])

    def accion(self, origen, destino) -> str:
        """
        Translates a move between two adjacent cells into an action.

        Args:
            - origen (tuple[int, int]): source cell (row, column).
            - destino (tuple[int, int]): adjacent destination cell (row, column).

        Returns:
            - accion (str): equivalent action ("UP", "DOWN", "LEFT" or "RIGHT").
        """
        fila_origen, col_origen = origen
        fila_dest, col_dest = destino

        if fila_dest == fila_origen - 1 and col_dest == col_origen:
            return "UP"
        if fila_dest == fila_origen + 1 and col_dest == col_origen:
            return "DOWN"
        if fila_dest == fila_origen and col_dest == col_origen - 1:
            return "LEFT"
        if fila_dest == fila_origen and col_dest == col_origen + 1:
            return "RIGHT"

        raise ValueError("Invalid move")

    def accion_granada(self, origen, destino) -> str:
        """
        Builds the grenade-throw action towards an adjacent cell.

        Args:
            - origen (tuple[int, int]): cell from which the grenade is thrown.
            - destino (tuple[int, int]): adjacent target cell.

        Returns:
            - accion (str): action with the grenade prefix ("GRENADE_UP", etc.).
        """
        movimiento = self.accion(origen, destino)
        return "GRANADA_" + movimiento

def elegir_movimiento_usuario(pos: tuple, beliefs: Beliefs, mundo: dict, estado: dict) -> str:
    """
    Asks the user for an action.
    Allows moving (W/A/S/D), throwing the grenade (G) and leaving (E) if the
    winning conditions are met.

    Args:
        - pos (tuple[int, int]): current position of the agent.
        - beliefs (Beliefs): agent beliefs with the F, P, D, M and S matrices.
        - mundo (dict): environment dictionary (includes N and the palace board).
        - estado (dict): current agent state (grenade, has_kurtz, etc.).

    Returns:
        - accion (str): action chosen by the user ("UP", "DOWN", "LEFT", "RIGHT",
          "EXIT" or "GRENADE_DIR").
    """
    N = mundo["N"]
    vecinos = neighbours(pos, N)

    mapa_mov = {"W": "UP", "S": "DOWN", "A": "LEFT", "D": "RIGHT"}
    direcciones = {"UP": (-1, 0), "DOWN": (1, 0), "LEFT": (0, -1), "RIGHT": (0, 1)}

    print("\n--- CHOOSE AN ACTION ---")
    print(f"Current position: {pos}")
    print("Options:")

    for k, accion in mapa_mov.items():
        di, dj = direcciones[accion]
        v = (pos[0] + di, pos[1] + dj)
        if v in vecinos:
            p_trampa = float(beliefs.F[v] + beliefs.P[v] + beliefs.D[v])
            p_sold   = float(beliefs.M[v])
            p_exit   = float(beliefs.S[v])
            print(f"  {k} ({accion}) -> {v} | "
                  f"P(trap)={p_trampa:.2f} | "
                  f"P(soldier)={p_sold:.2f} | "
                  f"P(exit)={p_exit:.2f}")

    if estado.get("granada", False):
        print("  G (GRENADE)")

    while True:
        t = input("Action (W/A/S/D or G): ").strip().upper()

        # GRENADE
        if t == "G":
            if not estado.get("granada", False):
                print("You have no grenade left.")
                continue

            dir_key = input("Grenade direction (W/A/S/D): ").strip().upper()
            if dir_key in mapa_mov:
                return f"GRANADA_{mapa_mov[dir_key]}"

            print("Invalid direction.")
            continue

        if t == "E":
            if "S" not in mundo["palacio"][pos]:
                print("You cannot leave: you are not on the exit.")
                continue

            if not estado.get("has_kurtz", False):
                print("You cannot leave: you have not found Kurtz yet.")
                continue

            return "EXIT"


        # NORMAL MOVEMENT
        if t in mapa_mov:
            return mapa_mov[t]

        print("Invalid input.")

def funcion_transicion(estado: dict, mundo: dict, accion: str):
    """
    Applies an action to the current state and returns the new state along with information
    about the outcome (move, death, victory, invalid action or wall bump).
    Handles movement, exit and grenade-throw actions.

    Args:
        - estado (dict): current agent state (position, flags and resources).
        - mundo (dict): environment information (palace board and size N).
        - accion (str): action to execute ("UP", "DOWN", "LEFT", "RIGHT", "EXIT" or "GRANADA_DIR").

    Returns:
        - nuevo (dict): updated state after applying the action.
        - info (dict): dictionary with outcome flags and, if applicable, a message.
    """
    palacio = mundo["palacio"]
    N = mundo["N"]

    nuevo = dict(estado)
    nuevo["ultima_accion_matar_soldado"] = False

    direcciones = {"UP": (-1,0), "DOWN": (1,0), "LEFT": (0,-1), "RIGHT": (0,1)}

    # ---------------- EXIT ----------------
    if accion == "EXIT":
        # you can only leave from a cell containing "S"
        celda = palacio[nuevo["agent_pos"]]
        if "S" not in celda:
            return nuevo, {"invalid_exit": True, "message": "You are not on the exit."}

        if not nuevo.get("has_kurtz", False):
            return nuevo, {"win": False, "message": "You cannot win without Kurtz. You must find him first."}

        return nuevo, {"win": True, "message": "Kurtz and you have left the palace together."}

    # ---------------- GRENADE ----------------
    if accion.startswith("GRANADA_"):
        if not nuevo.get("granada", False):
            return nuevo, {"message": "You have no grenade left."}

        dir_ = accion.split("_", 1)[1]
        if dir_ not in direcciones:
            return nuevo, {"invalid_action": True, "message": f"Invalid direction: {dir_}"}

        nuevo["granada"] = False

        di, dj = direcciones[dir_]
        i, j = nuevo["agent_pos"]
        target = (i + di, j + dj)

        if not (0 <= target[0] < N and 0 <= target[1] < N):
            return nuevo, {"grenade": True, "hit_wall": True, "message": "The grenade hits the wall and is wasted."}

        celda_t = palacio[target]
        if nuevo.get("soldado_vivo", True) and ("M" in celda_t):
            nuevo["soldado_vivo"] = False
            nuevo["ultima_accion_matar_soldado"] = True
            return nuevo, {"grenade": True, "killed_soldier": True, "message": "Soldier eliminated!"}

        return nuevo, {"grenade": True, "message": "The grenade explodes with no effect."}

    # ---------------- MOVEMENT ----------------
    if accion not in direcciones:
        return nuevo, {"invalid_action": True, "message": f"Invalid action: {accion}"}

    i, j = nuevo["agent_pos"]
    di, dj = direcciones[accion]
    ni, nj = i + di, j + dj

    if not (0 <= ni < N and 0 <= nj < N):
        return nuevo, {"hit_wall": True, "message": "You bump into a wall."}

    nuevo["agent_pos"] = (ni, nj)

    celda = palacio[(ni, nj)]

    # pick up Kurtz
    if (not nuevo.get("has_kurtz", False)) and ("CK" in celda):
        nuevo["has_kurtz"] = True
        return nuevo, {"moved": True, "picked_kurtz": True, "message": "You have found Kurtz. You now move together."}

    # death by traps
    if ("F" in celda) or ("P" in celda) or ("D" in celda):
        return nuevo, {"dead": True, "cause": "TRAP"}

    # death by soldier
    if nuevo.get("soldado_vivo", True) and ("M" in celda):
        return nuevo, {"dead": True, "cause": "SOLDIER"}

    return nuevo, {"moved": True}

def jugar_partida_bayes(console: Console) -> dict:
    """
    Runs a game controlled manually by the user.
    The agent updates its beliefs from the percepts and lets the user
    decide the action each turn until they win, die or get stuck.

    Args:
        - console (Console): Rich console used to render the game state.

    Returns:
        - resultado (dict): dictionary with the final result of the game
          (victory, death or deadlock) and the associated information.
    """

    #Initialise world and state
    mundo, estado = inicializar_palacio(N=6)
    beliefs = Beliefs(mundo["N"])

    try:
        perceptos = percept(estado, mundo)
        update_beliefs(beliefs, estado, mundo, perceptos)
    except ValueError:
        return {"blocked": True, "message": "Initial contradiction in beliefs."}

    while True:
        console.clear()
        entorno_palacio2.render_bayes(console, mundo, estado, beliefs)

        accion = elegir_movimiento_usuario(estado["agent_pos"], beliefs, mundo, estado)

        estado, info = funcion_transicion(estado, mundo, accion)

        if info.get("dead"):
            return {"dead": True, **info}

        if info.get("win"):
            return {"win": True, **info}

        try:
            perceptos = percept(estado, mundo)
            update_beliefs(beliefs, estado, mundo, perceptos)
        except ValueError:
            return {"blocked": True, "message": "Logical deadlock: contradiction in beliefs."}

def jugar_partida_bayes_greedy(console: Console, agente) -> dict:
    """
    Runs a full game with an automatic greedy agent.
    The agent decides its actions based on the probabilistic beliefs,
    updated from the percepts, until it wins, dies or gets stuck.

    Args:
        - console (Console): Rich console used to render the game state.
        - agente (object): automatic agent in charge of choosing the action each turn.

    Returns:
        - resultado (dict): dictionary with the final result of the game
          (victory, death or deadlock) and associated information.
    """
    mundo, estado = inicializar_palacio(N=6)
    beliefs = Beliefs(mundo["N"])

    try:
        perceptos = percept(estado, mundo)
        update_beliefs(beliefs, estado, mundo, perceptos)
    except ValueError:
        return {"blocked": True, "message": "Initial contradiction in beliefs."}

    while True:
        entorno_palacio2.render_bayes(console, mundo, estado, beliefs)

        accion = agente.decidir(estado, beliefs, mundo)
        time.sleep(0.3)

        if accion == "BLOCKED":
            return {"blocked": True, "message": "Deadlock: no selectable action."}

        estado, info = funcion_transicion(estado, mundo, accion)

        if info.get("dead"):
            return {"dead": True, **info}
        if info.get("win"):
            return {"win": True, **info}

        try:
            perceptos = percept(estado, mundo)
            update_beliefs(beliefs, estado, mundo, perceptos)
        except ValueError:
            return {"blocked": True, "message": "Logical deadlock: contradiction in beliefs."}

def main() -> None:
    """
    Main program flow.
    Shows the initial menu, handles navigation between game modes
    (instructions, Bayesian manual mode and greedy automatic mode) and
    controls the game loop until the user decides to quit.
    """
    console = Console()
    game_mode = bienvenida(console)

    while True:

        # 1) Instructions
        if game_mode == "1":
            instrucciones(console)
            game_mode = bienvenida(console)
            continue

        # 2) Manual mode
        elif game_mode == "2":
            
            info = jugar_partida_bayes(console)

            if info.get("dead"):
                pantalla_game_over(console, "YOU DIED", "red")
            elif info.get("win"):
                pantalla_game_over(console, "VICTORY", "green")
            elif info.get("blocked"):
                pantalla_game_over(console, "LOGICAL DEADLOCK", "yellow")

            time.sleep(1.5)
            opcion = menu_post_partida(console)

            if opcion == "1":      
                continue
            if opcion == "2":  
                game_mode = bienvenida(console)
                continue
            if opcion == "3": 
                return

        # 3) Automatic mode 
        elif game_mode == "3":
            agente = AgenteGreedy() 
            info = jugar_partida_bayes_greedy(console, agente)

            if info.get("dead"):
                pantalla_game_over(console, "YOU DIED", "red")
            elif info.get("win"):
                pantalla_game_over(console, "VICTORY", "green")
            elif info.get("blocked"):
                pantalla_game_over(console, "LOGICAL DEADLOCK", "yellow")

            time.sleep(1.2)
            opcion = menu_post_partida(console)

            if opcion == "1":
                continue
            if opcion == "2":
                game_mode = bienvenida(console)
                continue
            if opcion == "3":
                return

        elif game_mode == "4":
            return
        

if __name__ == "__main__":
    main()
