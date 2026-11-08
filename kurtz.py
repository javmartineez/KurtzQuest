import entorno_palacio1
from knowledge_base import KnowledgeBase
from rich.panel import Panel
from rich.align import Align
from rich.console import Console
from rich.text import Text
from collections import deque
import time
import pyfiglet


N = 6

def bienvenida(console: Console) -> str:
    """
    Shows the main menu and asks the user for the game mode.

    Args:
        - console (Console): Rich console used to display the interface.

    Returns:
        - game_mode (str): option selected by the user.
    """

    console.clear()

    figlet = pyfiglet.Figlet(font="slant")
    titulo = figlet.renderText("FINDING \nCOLONEL\nKURTZ")

    titulo = Text(titulo, style="bold cyan", justify="center")
    console.print(Panel(Align.center(titulo), border_style="cyan", padding=(1, 4)))

    #Game options panel
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
        "Your mission is clear and leaves no room for mistakes.\n"
        "You must enter the palace and find [bold magenta]Colonel Kurtz (CK)[/bold magenta], "
        "whose location is completely unknown. Once you find him, you must both "
        "[bold]get out of the palace together and alive[/bold].\n\n"
        "When you locate the colonel, your character, [bold orange1]Captain Willard (CW)[/bold orange1], "
        "will be shown in [bold magenta]purple[/bold magenta], "
        "showing that you are no longer walking alone.\n\n"
        "But stay alert.\n"
        "The palace is in ruins and full of dangers. Some rooms hide "
        "deadly [bold red]pits[/bold red] due to the poor state of the palace. "
        "Others may hold an [bold yellow]enemy soldier[/bold yellow] who will finish you off.\n\n"
        "You have a single [bold]grenade[/bold]. Use it wisely: it can only be thrown "
        "into an adjacent room (up, down, left or right). One mistake and you will be defenceless.\n\n"
        "The rooms you have already been through are marked in "
        "[bold blue]blue[/bold blue], so you do not lose track of where you have been. "
        "The palace [bold green]exit[/bold green] is clearly shown in green but remember, "
        "if you try to leave without the colonel, you will have failed.\n"
        "[bold]Good luck, soldier.[/bold]"
    )

    controles = (
        "Use [bold cyan]W/A/S/D[/bold cyan] to move up/left/down/right respectively.\n"
        "Use [bold cyan]G[/bold cyan] to throw the grenade. After pressing it, you must specify "
        "the throwing direction with W/A/S/D\n"
        "Once you find the [bold green]exit[/bold green], press [bold cyan]E[/bold cyan] to leave"
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

def inicializar_palacio(console: Console, N: int = N) -> tuple[dict, dict]:
    """
    Initialises the palace environment and the agent's initial state.

    Args:
        - console (Console): Rich console used to display the interface.
        - N (int): size of the palace (N x N). Defaults to the
          global value N.

    Returns:
        - mundo (dict): dictionary representing the true state of the
                        world, including the palace map, the positions of the soldier,
                        Colonel Kurtz and the exit, and the size of the environment.
        - estado_0 (dict): dictionary representing the agent's initial
                           state, including its position, whether it has found Colonel Kurtz,
                           whether the soldier is still alive, grenade availability and whether
                           the last action killed the soldier.
    """

    pantalla_carga(console)

    # Ideally this would return a world dict/dataclass
    palacio, pos_soldado, pos_kurtz, pos_salida = entorno_palacio1.crear_entorno(N)

    estado_0 = {
        "agent_pos": (0, 0),
        "has_kurtz": False,
        "soldado_vivo": True,
        "granada": True,
        "ultima_accion_matar_soldado": False
    }

    mundo = {
        "palacio": palacio,
        "pos_soldado": pos_soldado,
        "pos_kurtz": pos_kurtz,
        "pos_salida": pos_salida,
        "N": N
    }

    return mundo, estado_0

def pantalla_game_over(console: Console, texto: str, color: str) -> None:
    """
    Shows the end-of-game screen.

    Args:
        - console (Console): Rich console used to render the screen.
        - texto (str): main text displayed as ASCII art.
        - color (str): colour used for the text and the panel border.
    """

    console.clear()
    figlet = pyfiglet.Figlet(font="doom")
    ascii_art = figlet.renderText(texto)

    console.print(
        Panel(
            Align.center(Text(ascii_art, style=f"bold {color}")),
            border_style=color,
            padding=(1, 4),
        )
    )

def menu_post_partida(console: Console) -> str:
    """
    Shows the post-game menu and asks the user for an action.

    Args:
        - console (Console): Rich console used to display the options.

    Returns:
        - opcion (str): option selected by the user.
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
        opcion = console.input("Choose [1/2/3]: ").strip()
        if opcion in {"1", "2", "3"}:
            return opcion
        console.print("[bold red]Invalid input.[/bold red] Type 1, 2 or 3.")

def funcion_transicion(estado: dict, mundo: dict, accion: str):
    """
    Applies an action to the current state and returns the new state along with information about
    the new state.

    Args:
        - estado (dict): current agent state (position, inventory, flags).
        - mundo (dict): environment information (map, element positions, size).
        - accion (str): action to execute ("UP", "DOWN", "LEFT", "RIGHT", "EXIT" or "GRANADA_DIR").

    Returns:
        - estado_next (dict): resulting state after applying the action.
        - info (dict): dictionary with flags and messages describing the outcome of the transition.
    """

    palacio = mundo["palacio"]
    N = mundo["N"]
    pos_soldado = mundo["pos_soldado"]
    pos_kurtz = mundo["pos_kurtz"]
    direcciones = {"UP": (-1,0), "DOWN": (1,0), "LEFT": (0,-1), "RIGHT": (0,1)}


    estado_next = dict(estado)                                #state we are transitioning to

    estado_next["ultima_accion_matar_soldado"] = False

    # ---------------- LEAVING THE PALACE ----------------
    if accion == "EXIT":
        if estado_next["agent_pos"] != mundo["pos_salida"]:
            return estado_next, {"invalid_exit": True, "message": "You must be on the exit to leave"}

        if not estado_next["has_kurtz"]:                      #On the exit but CK has not been found yet
            return estado_next, {"win": False, "message": "You must find Colonel Kurtz first"}

        return estado_next, {"win": True, "message": "Colonel Kurtz and you have left the palace together."}


    # ---------------- GRENADE ----------------
    if accion.startswith("GRANADA_"):
        if not estado_next["granada"]:
            return estado_next, {"message": "You have no grenade left."}

        estado_next["granada"] = False

        dir_granada = accion.replace("GRANADA_", "")
        di, dj = direcciones[dir_granada]

        i, j = estado_next["agent_pos"]
        target = (i + di, j + dj)

        # Thrown outside the board
        if not (0 <= target[0] < N and 0 <= target[1] < N):
            return estado_next, {"granada": True, "pared": True, "message": "You threw the grenade out of the palace"}

        # Thrown at the soldier while alive
        if estado_next["soldado_vivo"] and target == pos_soldado:
            estado_next["soldado_vivo"] = False
            estado_next["ultima_accion_matar_soldado"] = True
            return estado_next, {"killed_soldier": True, "message": "Soldier eliminated!"}

        # If it lands on Kurtz, nothing happens
        if target == pos_kurtz:
            return estado_next, {"granada": True, "message": "You threw the grenade at Colonel Kurtz. Don't worry, he took cover in time."}

        # If it lands on any other cell, nothing happens
        return estado_next, {"granada": True, "message": "Your grenade did not hit anything"}


    # ---------------- MOVEMENT ----------------
    i, j = estado_next["agent_pos"]
    di, dj = direcciones[accion]
    ni, nj = i + di, j + dj

    if not (0 <= ni < N and 0 <= nj < N):
        return estado_next, {"pared": True, "message": "You bump into a wall."}

    estado_next["agent_pos"] = (ni, nj)

    # pick up Kurtz
    if (not estado_next["has_kurtz"]) and (estado_next["agent_pos"] == pos_kurtz):
        estado_next["has_kurtz"] = True
        return estado_next, {"moved": True, "con_kurtz": True, "message": "You have found Kurtz. You now move together."}


    # death by pit
    if palacio[ni, nj] == "P":
        return estado_next, {"dead": True, "causa": "P"}

    # death by soldier
    if estado_next["soldado_vivo"] and (estado_next["agent_pos"] == pos_soldado):
        return estado_next, {"dead": True, "causa": "S"}


    return estado_next, {"moved": True}

def escoger_accion(estado: dict, kb: KnowledgeBase) -> str:
    """
    Asks the user for an action based on the current game state.
    The function shows the information deduced by the knowledge base.

    Args:
        - estado (dict): current agent state (position, inventory and flags).
        - kb (KnowledgeBase): knowledge base with the logical deductions about the environment.

    Returns:
        - accion (str): action selected by the user.
    """

    mapa_mov = {"W": "UP", "S": "DOWN", "A": "LEFT", "D": "RIGHT"}
    direcciones = {"UP": (-1,0), "DOWN": (1,0), "LEFT": (0,-1), "RIGHT": (0,1)}

    pos = estado["agent_pos"]
    vecinos = kb.neighbours(pos)

    # Set of allowed moves
    seguras = {v for v in vecinos if kb.is_safe(v)}

    tecla_a_destino = {}
    for k, mov in mapa_mov.items():
        di, dj = direcciones[mov]
        dest = (pos[0] + di, pos[1] + dj)
        if dest in vecinos:  # inside the board
            tecla_a_destino[k] = dest

    teclas_mov_ok = list(tecla_a_destino.keys())

    print("\nActions: W/A/S/D move | E exit | G grenade")
    print(f"Safe rooms: {sorted(seguras)}")

    # If there are no allowed moves
    if not teclas_mov_ok:
        print("[WARNING] The KB cannot prove any safe move right now.")
        print("You can only use the grenade (G) or leave (E if you are on the exit).")

    while True:
        t = input("Action: ").strip().upper()

        if t in mapa_mov:
            if t not in teclas_mov_ok:
                print("Move NOT allowed")
                continue
            return mapa_mov[t]

        if t == "E":
            exit_pos = kb.known_exit()
            if not estado.get("has_kurtz", False):
                print("You cannot leave: you have not found Kurtz yet.")
                continue
            if exit_pos is None:
                print("You cannot leave: the KB has not deduced the exit yet.")
                continue
            if estado["agent_pos"] != exit_pos:
                print("You cannot leave: you are not on the exit")
                continue
            return "EXIT"

        if t == "G":
            dir_key = input("Grenade direction (W/A/S/D): ").strip().upper()
            if dir_key in mapa_mov:
                return "GRANADA_" + mapa_mov[dir_key]
            print("Invalid direction.")
            continue

        print("Invalid input.")

def percept(estado: dict, kb: KnowledgeBase, mundo: dict) -> list[bool]:
    """
    Computes the percepts available to the agent: presence of breeze,
    snore, glow, contact with walls and hearing a scream
    after killing the enemy soldier.

    Args:
        - estado (dict): dictionary representing the agent's current
                         state.
        - mundo (dict): dictionary representing the true state of the
                        world.
        - kb (KnowledgeBase): the agent's knowledge base

    Returns:
        - perceptos (list[bool]): list of booleans representing
                                  the agent's percept in the following order:
                                  [Breeze, Snore, Glow, Wall_up, Wall_down,
                                  Wall_left, Wall_right, Scream].
    """

    palacio = mundo["palacio"]
    pos_salida = mundo["pos_salida"]
    pos_soldado = mundo["pos_soldado"]

    pos = estado["agent_pos"]
    vecinos = kb.neighbours(pos)

    brisa = any(palacio[v] == "P" for v in vecinos)
    ronquido = estado["soldado_vivo"] and any(v == pos_soldado for v in vecinos)
    resplandor = (pos == pos_salida) or (pos_salida in vecinos)

    pared_arriba, pared_abajo, pared_izq, pared_der = comprobar_paredes(pos, mundo["N"])

    grito = estado["ultima_accion_matar_soldado"]

    perceptos = [brisa, ronquido, resplandor, pared_arriba, pared_abajo, pared_izq, pared_der, grito]

    return perceptos

def comprobar_paredes(pos: tuple[int, int], N: int) -> tuple[bool, bool, bool, bool]:
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

class AgenteManual:
    """
    Manual agent guided by the knowledge base deductions.
    """

    def decidir(self, estado: dict, kb: KnowledgeBase, seguras=None) -> str:
        """
        Returns the action chosen manually by the user.

        Args:
            - estado (dict): current agent state.
            - kb (KnowledgeBase): knowledge base used to inform the user.
            - seguras (set | None): ignored parameter, included for compatibility
              with AgenteBFS

        Returns:
            - accion (str): action selected by the user.
        """

        return escoger_accion(estado, kb)

class AgenteBFS:
    """
    Automatic agent that uses breadth-first search (BFS) guided by
    the knowledge base deductions to explore the palace,
    find Kurtz and get out alive.
    """

    def __init__(self):
        """
        Initialises the BFS agent and its internal control structures.
        """
        self.plan = []                 # Current action plan
        self.historial = []            # History of visited positions
        self.salidas_fallidas = set()  # Exits tried without success
        self.bloqueos = set()          # Cells marked as dead ends

    def decidir(self, estado: dict, kb: KnowledgeBase, seguras: set) -> str:
        """
        Decides the next action using BFS and backtracking.
        Prioritises leaving the palace once Kurtz has been found and, otherwise,
        explores unvisited safe cells.

        Args:
            - estado (dict): current agent state.
            - kb (KnowledgeBase): the agent's knowledge base.
            - seguras (set): set of cells deduced to be safe.

        Returns:
            - accion (str): action chosen by the agent.
        """
        posicion = estado["agent_pos"]
        seguras = set(seguras)

        # 0) Update history without duplicates
        if not self.historial or self.historial[-1] != posicion:
            self.historial.append(posicion)

        # 1) Execute pending plan
        if self.plan:
            return self.plan.pop(0)

        # 2) If Kurtz has been found, prioritise the exit
        if estado.get("has_kurtz", False):
            salida = kb.known_exit()
            if salida is not None:
                if posicion == salida and posicion not in self.salidas_fallidas:
                    return "EXIT"

                plan = self.bfs(
                    posicion,
                    [salida],
                    kb,
                    permitidas=set(kb.visited) | seguras
                )
                if plan:
                    self.plan = plan
                    return self.plan.pop(0)

        # 3) Explore unvisited safe cells
        objetivos = [c for c in seguras if c not in kb.visited]
        if objetivos:
            plan = self.bfs(
                posicion,
                objetivos,
                kb,
                permitidas=set(kb.visited) | seguras
            )
            if plan:
                self.plan = plan
                return self.plan.pop(0)

        # 4) Backtracking
        celda_retroceso = self.buscar_retroceso(kb)
        if celda_retroceso is not None and celda_retroceso != posicion:
            plan = self.bfs(
                posicion,
                [celda_retroceso],
                kb,
                permitidas=set(kb.visited) | seguras
            )
            if plan:
                self.plan = plan
                return self.plan.pop(0)

        if len(self.historial) >= 2:
            self.bloqueos.add(posicion)
            self.historial.pop()
            anterior = self.historial[-1]

            if anterior in self.bloqueos:
                return "BLOCKED"

            plan = self.bfs(
                posicion,
                [anterior],
                kb,
                permitidas=set(kb.visited) | seguras
            )
            if plan:
                self.plan = plan
                return self.plan.pop(0)

        # 5) Last resort: move to an adjacent safe cell
        for vecino in kb.neighbours(posicion):
            if vecino in seguras:
                return self.accion(posicion, vecino)

        return "BLOCKED"

    def buscar_retroceso(self, kb: KnowledgeBase):
        """
        Searches the history for the most recent cell from which there is
        some unvisited safe cell.

        Args:
            - kb (KnowledgeBase): the agent's knowledge base.

        Returns:
            - celda (tuple[int, int] | None): candidate cell for backtracking.
        """
        visitadas = set(kb.visited)
        for celda in reversed(self.historial):
            for vecino in kb.neighbours(celda):
                if vecino not in visitadas and kb.is_safe(vecino):
                    return celda
        return None

    def bfs(self, inicio, objetivos, kb: KnowledgeBase, permitidas: set):
        """
        Performs a breadth-first search from a starting cell to
        the goals.

        Args:
            - inicio (tuple[int, int]): starting position.
            - objetivos (list[tuple[int, int]]): goal cells.
            - kb (KnowledgeBase): knowledge base.
            - permitidas (set): cells that may be traversed.

        Returns:
            - plan (list[str]): sequence of actions to reach the goal,
              or an empty list if there is no path.
        """
        objetivos = set(objetivos)
        permitidas = set(permitidas)

        cola = deque([inicio])
        padres = {inicio: None}

        while cola:
            actual = cola.popleft()

            if actual in objetivos:
                return self.reconstruir_plan(actual, padres)

            for vecino in kb.neighbours(actual):
                if vecino in permitidas and vecino not in padres:
                    padres[vecino] = actual
                    cola.append(vecino)

        return []

    def reconstruir_plan(self, objetivo, padres):
        """
        Rebuilds the action plan from the parents dictionary.

        Args:
            - objetivo (tuple[int, int]): goal cell reached.
            - padres (dict): dictionary of predecessors.

        Returns:
            - plan (list[str]): list of actions to execute.
        """
        camino = []
        actual = objetivo

        while padres[actual] is not None:
            camino.append((padres[actual], actual))
            actual = padres[actual]

        camino.reverse()
        return [self.accion(a, b) for a, b in camino]

    def accion(self, origen, destino) -> str:
        """
        Translates a move between two adjacent cells into an action.

        Args:
            - origen (tuple[int, int]): source cell.
            - destino (tuple[int, int]): destination cell.

        Returns:
            - accion (str): action corresponding to the move.
        """
        oi, oj = origen
        di, dj = destino

        if di == oi - 1 and dj == oj:
            return "UP"
        if di == oi + 1 and dj == oj:
            return "DOWN"
        if di == oi and dj == oj - 1:
            return "LEFT"
        if di == oi and dj == oj + 1:
            return "RIGHT"

        raise ValueError("Invalid move")

def jugar_partida(console: Console, agente) -> dict:
    """
    Runs the main game loop: perceive, update the KB, render the state,
    request/decide an action and apply the transition until the player wins, dies or gets stuck.

    Args:
        - console (Console): Rich console used to display the game.
        - agente (object): agent that decides the action each turn (manual or automatic).

    Returns:
        - info (dict): dictionary with the final result of the game (victory, death or deadlock)
                       and associated messages if any.
    """

    mundo, estado = inicializar_palacio(console)
    N = mundo["N"]
    kb = KnowledgeBase(N)

    while True:
        perceptos = percept(estado, kb, mundo)
        kb.add_percept(estado["agent_pos"], perceptos)

        pos = estado["agent_pos"]
        vecinos = kb.neighbours(pos)
        seguras = {v for v in vecinos if kb.is_safe(v)}
        possible_pits, possible_soldier = kb.possible_pits_and_soldier()
        exit_pos = kb.known_exit()

        console.clear()
        entorno_palacio1.render(
            console,
            N=N,
            pos_agente=pos,
            has_kurtz=estado.get("has_kurtz", False),
            visited=kb.visited,
            safe=seguras,
            possible_pits=possible_pits,
            possible_soldier=possible_soldier,
            show_exit_if_known=True,
            exit_pos=exit_pos,
        )

        accion = agente.decidir(estado, kb, seguras)
        if accion == "BLOCKED":
            return {"blocked": True,
                    "message": "Logical deadlock: no safe cells are reachable from the current position."
                    }
        estado, info = funcion_transicion(estado, mundo, accion)

        if isinstance(agente, AgenteBFS):
            time.sleep(0.3)


        if info.get("message"):
            console.print(f"[bold]{info['message']}[/bold]")

        if info.get("dead") or info.get("win"):
            return info

        if info.get("invalid_exit") and hasattr(agente, "salidas_fallidas"):
            agente.salidas_fallidas.add(estado["agent_pos"])
            agente.plan = []  # just in case

def main() -> None:
    """
    Runs the main game flow: shows the initial menu, starts games in the different modes
    and handles navigation between menus until the user quits.
    """
    console = Console()
    game_mode = bienvenida(console)

    while True:

        if game_mode == "1":
            instrucciones(console)
            game_mode = bienvenida(console)
            continue

        elif game_mode == "2":
            agente = AgenteManual()
            info = jugar_partida(console, agente)

            if info.get("dead"):
                pantalla_game_over(console, "YOU DIED", "red")
            elif info.get("win"):
                pantalla_game_over(console, "VICTORY", "green")

            time.sleep(1.5)
            opcion = menu_post_partida(console)

            if opcion == "1":
                continue
            if opcion == "2":
                game_mode = bienvenida(console)
                continue
            if opcion == "3":
                return

        elif game_mode == "3":
            agente = AgenteBFS()
            info = jugar_partida(console, agente)

            if info.get("dead"):
                pantalla_game_over(console, "YOU DIED", "red")
            elif info.get("win"):
                pantalla_game_over(console, "VICTORY", "green")
            elif info.get("blocked"):
                pantalla_game_over(console, "LOGICAL  DEADLOCK", "yellow")


            time.sleep(1)
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



