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
    Muestra el menú principal del juego y solicita al usuario el modo de juego.

    Args:
        - console (Console): consola Rich utilizada para mostrar la interfaz.

    Returns:
        - game_mode (str): opción seleccionada por el usuario.
    """

    console.clear()

    figlet = pyfiglet.Figlet(font="slant")
    titulo_ascii = figlet.renderText("BUSCANDO \nAL\nCORONEL KURTZ")

    titulo = Text(titulo_ascii, style="bold cyan", justify="center")
    console.print(Panel(Align.center(titulo), border_style="cyan", padding=(1, 4)))

    #Panel de opciones de juego
    opciones = (
        "[bold cyan]1.[/bold cyan] [bold]¿Cómo jugar?[/bold]  [dim]→ reglas y controles[/dim]\n"
        "[bold cyan]2.[/bold cyan] [bold]Modo de juego Manual[/bold]  [dim]→ tú eliges acciones[/dim]\n"
        "[bold cyan]3.[/bold cyan] [bold]Modo por algoritmos[/bold]  [dim]→ BFS[/dim]\n"
        "[bold cyan]4.[/bold cyan] [bold]Salir[/bold]"
    )

    console.print(
        Panel(
            Align.left(Text.from_markup(opciones)),
            title="[bold]Menú principal[/bold]",
            title_align="left",
            border_style="cyan",
            padding=(1, 4),
        )
    )

    while True:
        game_mode = input("Escoge un modo [1/2/3/4]: ").strip()

        if game_mode in {"1", "2", "3", "4"}:
            return game_mode
        
        console.print("[bold red]Entrada inválida.[/bold red] Escribe 1, 2, 3 o 4.")

def instrucciones(console: Console) -> None:
    """
    Muestra en pantalla las instrucciones de la misión y los controles del juego.

    Args:
        - console (Console): consola Rich utilizada para mostrar los paneles de texto.
    """

    console.clear()

    titulo1 = Text("INSTRUCCIONES DE LA MISIÓN", style="bold cyan", justify="center")
    titulo2 = Text("CONTROLES", style="bold cyan", justify="center")

    narrativa = (
        "Tu misión es clara y no admite errores.\n"
        "Debes adentrarte en el palacio y encontrar al [bold magenta]Coronel Kurtz (CK)[/bold magenta], "
        "cuya ubicación es completamente desconocida. Una vez lo encuentres, deberéis "
        "[bold]salir juntos y con vida[/bold] del palacio.\n\n"
        "Cuando localices al coronel, tu figura, el [bold orange1]Capitán Willard (CW)[/bold orange1],"
        "pasará a mostrarse en [bold magenta]morado[/bold magenta], "
        "indicando que ya no caminas solo.\n\n"
        "Pero mantente alerta.\n"
        "El palacio está en ruinas y plagado de peligros. Algunas habitaciones esconden "
        "[bold red]precipicios[/bold red] mortales dado el mal estado del palacio. "
        "Otras pueden albergar a un [bold yellow]soldado enemigo[/bold yellow] que acabará contigo.\n\n"
        "Dispones de una única [bold]granada[/bold]. Úsala con cabeza: solo puede lanzarse "
        "a una habitación contigua (arriba, abajo, izquierda o derecha). Un error y estarás indefenso.\n\n"
        "Las habitaciones por las que ya hayas pasado quedarán marcadas en "
        "[bold blue]azul[/bold blue], para que no pierdas la noción de por donde has pasado. "
        "La [bold green]salida[/bold green] del palacio se distingue claramente de color verde pero recuerda, "
        "si intentas salir sin el coronel, habrás fracasado.\n"
        "[bold]Buena suerte, soldado.[/bold]"
    )

    controles = (
        "Utiliza [bold cyan]W/A/S/D[/bold cyan] para moverte arriba/izquierda/abajo/derecha respectivamente.\n"
        "Utiliza [bold cyan]G[/bold cyan] para lanzar la granada. Tras lanzarla, deberás especificar "
        "la dirección del lanzamiento mediante W/A/S/D\n"
        "Tras encontrar la [bold green]salida[/bold green], utiliza la [bold cyan]E[/bold cyan] para salir"
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
            Text.from_markup(narrativa),
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

    console.input("\nPulsa ENTER para volver al menú...")

def pantalla_carga(console: Console, segundos: float = 1.0) -> None:
    """
    Muestra una pantalla de carga simulada mediante un spinner en consola.

    Args:
        - console (Console)
        - segundos (float): Duración de la pantalla de carga en segundos.
    """

    console.clear()
    with console.status("[bold]Preparando el palacio...[/bold]", spinner="dots"):
        time.sleep(segundos)

def inicializar_palacio(console: Console, N: int = N) -> tuple[dict, dict]:
    """
    Inicializa el entorno completo del palacio y el estado inicial del agente.
    La función se encarga de mostrar la bienvenida y la pantalla de carga,
    generar de forma aleatoria el mapa del palacio junto con la posición
    de sus elementos clave (soldado, Coronel Kurtz y salida) e inicializar
    el estado del Capitán Willard.
    
    Args:
        - console (Console): consola Rich utilizada para mostrar la interfaz.
        - N (int): Tamaño del palacio (N x N). Por defecto, se utiliza el
          valor global N.
    
    Returns:
        - mundo (dict): Diccionario que representa el estado objetivo del
                        mundo, incluyendo el mapa del palacio, las posiciones del soldado,
                        del Coronel Kurtz, de la salida y el tamaño del entorno.
        - estado_0 (dict): Diccionario que representa el estado inicial del
                           agente, incluyendo su posición, si ha encontrado al Coronel Kurtz,
                           si el soldado sigue vivo, la disponibilidad de la granada y si la
                           última acción fue la eliminación del soldado.
    """

    pantalla_carga(console)

    # Ideal: que esto devuelva un world dict/dataclass
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
    Muestra la pantalla final de la partida.

    Args:
        - console (Console): consola Rich utilizada para renderizar la pantalla.
        - texto (str): texto principal que se mostrará en formato ASCII.
        - color (str): color utilizado para el texto y el borde del panel.
    """

    console.clear()
    fig = pyfiglet.Figlet(font="doom")
    ascii_art = fig.renderText(texto)

    console.print(
        Panel(
            Align.center(Text(ascii_art, style=f"bold {color}")),
            border_style=color,
            padding=(1, 4),
        )
    )

def menu_post_partida(console: Console) -> str:
    """
    Muestra el menú posterior a la partida y solicita una acción al usuario.

    Args:
        - console (Console): consola Rich utilizada para mostrar las opciones.

    Returns:
        - opcion (str): opción seleccionada por el usuario.
    """

    opciones = (
        "[bold cyan]1.[/bold cyan] Reintentar\n"
        "[bold green]2.[/bold green] Volver al menú principal\n"
        "[bold red]3.[/bold red] Salir"
    )
    console.print(
        Panel(
            Align.left(Text.from_markup(opciones)),
            title="[bold]¿Qué quieres hacer ahora?[/bold]",
            title_align="left",
            border_style="cyan",
            padding=(1, 4),
        )
    )

    while True:
        opcion = console.input("Elige [1/2/3]: ").strip()
        if opcion in {"1", "2", "3"}:
            return opcion
        console.print("[bold red]Entrada inválida.[/bold red] Escribe 1, 2 o 3.")

def funcion_transicion(estado: dict, mundo: dict, accion: str):
    """
    Aplica una acción al estado actual y devuelve el nuevo estado junto con información sobre el
    nuevo estado.

    Args:
        - estado (dict): estado actual del agente (posición, inventario, flags).
        - mundo (dict): información del entorno (mapa, posiciones de elementos, tamaño).
        - accion (str): acción a ejecutar ("UP", "DOWN", "LEFT", "RIGHT", "EXIT" o "GRANADA_DIR").

    Returns:
        - estado_next (dict): estado resultante tras aplicar la acción.
        - info (dict): diccionario con flags y mensajes del resultado de la transición.
    """

    palacio = mundo["palacio"]
    N = mundo["N"]
    pos_soldado = mundo["pos_soldado"]
    pos_kurtz = mundo["pos_kurtz"]
    direcciones = {"UP": (-1,0), "DOWN": (1,0), "LEFT": (0,-1), "RIGHT": (0,1)}


    estado_next = dict(estado)                                #estado al que vamos a realizar la transicion

    estado_next["ultima_accion_matar_soldado"] = False

    # ---------------- SALIR DEL PALACIO ----------------
    if accion == "EXIT":
        if estado_next["agent_pos"] != mundo["pos_salida"]:
            return estado_next, {"invalid_exit": True, "message": "Para poder salir debes estar en la salida"}

        if not estado_next["has_kurtz"]:                      #En caso de estar en la salida pero no haber encontrado a CK
            return estado_next, {"win": False, "message": "Primero debes encontrar al Coronel Kurtz"}

        return estado_next, {"win": True, "message": "El Coronel Kurtz y tú habéis salido del palacio juntos."}


    # ---------------- GRANADA ----------------
    if accion.startswith("GRANADA_"):
        if not estado_next["granada"]:
            return estado_next, {"message": "Ya no tienes granada."}
        
        estado_next["granada"] = False

        dir_granada = accion.replace("GRANADA_", "")
        di, dj = direcciones[dir_granada]

        i, j = estado_next["agent_pos"]
        target = (i + di, j + dj)

        # Si se lanza fuera del tablero
        if not (0 <= target[0] < N and 0 <= target[1] < N):
            return estado_next, {"granada": True, "pared": True, "message": "Has lanzado la granada fuera del palacio"}

        # Si se lanza al soldado y este está vivo
        if estado_next["soldado_vivo"] and target == pos_soldado:
            estado_next["soldado_vivo"] = False
            estado_next["ultima_accion_matar_soldado"] = True
            return estado_next, {"killed_soldier": True, "message": "¡Soldado eliminado!"}
        
        # Si por error cae en Kurtz, no pasa nada
        if target == pos_kurtz:
            return estado_next, {"granada": True, "message": "Has lanzado la granada al Coronel Kurtz. Tranquilo, se cubrió a tiempo."}

        # Si cae en cualquier otra casilla, no pasa nada
        return estado_next, {"granada": True, "message": "Tu granada no ha dado en ningún blanco"}
    

    # ---------------- MOVIMIENTO ----------------
    i, j = estado_next["agent_pos"]
    di, dj = direcciones[accion]
    ni, nj = i + di, j + dj

    if not (0 <= ni < N and 0 <= nj < N):
        return estado_next, {"pared": True, "message": "Te chocas con una pared."}

    estado_next["agent_pos"] = (ni, nj)

    # recoger a Kurtz
    if (not estado_next["has_kurtz"]) and (estado_next["agent_pos"] == pos_kurtz):
        estado_next["has_kurtz"] = True
        return estado_next, {"moved": True, "con_kurtz": True, "message": "Has encontrado a Kurtz. Ahora vais juntos."}


    # muerte por precipicio
    if palacio[ni, nj] == "P":
        return estado_next, {"dead": True, "causa": "P"}

    # muerte por soldado
    if estado_next["soldado_vivo"] and (estado_next["agent_pos"] == pos_soldado):
        return estado_next, {"dead": True, "causa": "S"}


    return estado_next, {"moved": True}

def escoger_accion(estado: dict, kb: KnowledgeBase) -> str:
    """
    Solicita al usuario una acción a partir del estado actual del juego.
    La función muestra información deducida por la base de conocimiento,
    pero permite al usuario elegir libremente cualquier acción.

    Args:
        - estado (dict): estado actual del agente (posición, inventario y flags).
        - kb (KnowledgeBase): base de conocimiento con las deducciones lógicas del entorno.

    Returns:
        - accion (str): acción seleccionada por el usuario.
    """

    mapa_mov = {"W": "UP", "S": "DOWN", "A": "LEFT", "D": "RIGHT"}
    direcciones = {"UP": (-1,0), "DOWN": (1,0), "LEFT": (0,-1), "RIGHT": (0,1)}

    pos = estado["agent_pos"]
    vecinos = kb.neighbours(pos)

    # Conjunto de movimientos permitidos
    seguras = {v for v in vecinos if kb.is_safe(v)}

    tecla_a_destino = {}
    for k, mov in mapa_mov.items():
        di, dj = direcciones[mov]
        dest = (pos[0] + di, pos[1] + dj)
        if dest in vecinos:  # está dentro del tablero
            tecla_a_destino[k] = dest

    teclas_mov_ok = list(tecla_a_destino.keys())

    print("\nAcciones: W/A/S/D mover | E salir | G granada")
    print(f"Habitaciones seguras: {sorted(seguras)}")

    # Si no hay movimientos permitidos
    if not teclas_mov_ok:
        print("[AVISO] La KB no puede demostrar ningún movimiento seguro ahora mismo.")
        print("Solo puedes usar granada (G) o salir (E si estás en la salida).")

    while True:
        t = input("Acción: ").strip().upper()

        if t in mapa_mov:
            if t not in teclas_mov_ok:
                print("Movimiento NO permitido")
                continue
            return mapa_mov[t]

        # salir (sin filtro de seguridad)
        # salir: solo lo permito si la KB lo puede probar (o al menos si exit_pos coincide)
        if t == "E":
            exit_pos = kb.known_exit()
            if not estado.get("has_kurtz", False):
                print("No puedes salir: todavía no has encontrado a Kurtz.")
                continue
            if exit_pos is None:
                print("No puedes salir: la KB aún no ha deducido la salida.")
                continue
            if estado["agent_pos"] != exit_pos:
                print("No puedes salir: no estás en la salida")
                continue
            return "EXIT"

        # granada (sin filtro de seguridad)
        if t == "G":
            dir_key = input("Dirección granada (W/A/S/D): ").strip().upper()
            if dir_key in mapa_mov:
                return "GRANADA_" + mapa_mov[dir_key]
            print("Dirección inválida.")
            continue

        print("Entrada inválida.")
        
def percept(estado: dict, kb: KnowledgeBase, mundo: dict) -> list[bool]:
    """
    Genera el percepto del Capitán Willard en el estado actual del entorno.
    A partir de la posición actual del agente, del mapa del palacio y del
    estado del mundo, la función calcula los perceptos disponibles
    para el agente: presencia de brisa, ronquido, resplandor, contacto con
    paredes y percepción de un grito tras eliminar al soldado enemigo.
    
    Args:
        - estado (dict): Diccionario que representa el estado actual del
                         agente.
        - mundo (dict): Diccionario que representa el estado objetivo del
                        mundo.
    
    Returns:
        - perceptos (list[bool]): Lista de valores booleanos que representa
                                  el percepto del agente en el siguiente orden:
                                  [Brisa, Ronquido, Resplandor, Pared_arriba, Pared_abajo,
                                  Pared_izquierda, Pared_derecha, Grito].
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
    Determina la presencia de paredes alrededor de una posición dada.

    Args:
        - pos (tuple[int, int]): Posición actual (fila, columna) del agente.
        - N (int): Tamaño del palacio (N x N).
    
    Returns:
        - pared_arriba (bool)
        - pared_abajo (bool)
        - pared_izquierda (bool)
        - pared_derecha (bool)
    """

    i, j = pos

    pared_arriba = (i == 0)
    pared_abajo = (i == N - 1)
    pared_izq = (j == 0)
    pared_der = (j == N - 1)

    return pared_arriba, pared_abajo, pared_izq, pared_der

class AgenteManual:
    """
    Agente manual guiado por las deducciones de la base de conocimiento.
    """

    def decidir(self, estado: dict, kb: KnowledgeBase, seguras=None) -> str:
        """
        Devuelve la acción elegida manualmente por el usuario.

        Args:
            - estado (dict): estado actual del agente.
            - kb (KnowledgeBase): base de conocimiento utilizada para informar al usuario.
            - seguras (set | None): parámetro ignorado, incluido por compatibilidad
              con el AgenteBFS

        Returns:
            - accion (str): acción seleccionada por el usuario.
        """

        return escoger_accion(estado, kb)

class AgenteBFS:
    """
    Agente automático que utiliza búsqueda en anchura (BFS) guiada por
    las deducciones de la base de conocimiento para explorar el palacio,
    encontrar a Kurtz y salir con vida.
    """

    def __init__(self):
        """
        Inicializa el agente BFS y sus estructuras internas de control.
        """
        self.plan = []                 # Plan actual de acciones
        self.historial = []            # Historial de posiciones visitadas
        self.salidas_fallidas = set()  # Salidas intentadas sin éxito
        self.bloqueos = set()          # Celdas marcadas como callejón sin salida

    def decidir(self, estado: dict, kb: KnowledgeBase, seguras: set) -> str:
        """
        Decide la siguiente acción a ejecutar utilizando BFS y backtracking.
        Prioriza salir del palacio una vez encontrado Kurtz y, en caso contrario,
        explora celdas seguras no visitadas.

        Args:
            - estado (dict): estado actual del agente.
            - kb (KnowledgeBase): base de conocimiento del agente.
            - seguras (set): conjunto de celdas deducidas como seguras.

        Returns:
            - accion (str): acción decidida por el agente.
        """
        posicion = estado["agent_pos"]
        seguras = set(seguras)

        # 0) Actualizar historial sin duplicar
        if not self.historial or self.historial[-1] != posicion:
            self.historial.append(posicion)

        # 1) Ejecutar plan pendiente
        if self.plan:
            return self.plan.pop(0)

        # 2) Si ya se ha encontrado a Kurtz, priorizar salida
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

        # 3) Explorar celdas seguras no visitadas
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

        # 5) Último recurso: moverse a una segura adyacente
        for vecino in kb.neighbours(posicion):
            if vecino in seguras:
                return self.accion(posicion, vecino)

        return "BLOCKED"

    def buscar_retroceso(self, kb: KnowledgeBase):
        """
        Busca en el historial la celda más reciente desde la cual exista
        alguna celda segura no visitada.

        Args:
            - kb (KnowledgeBase): base de conocimiento del agente.

        Returns:
            - celda (tuple[int, int] | None): celda candidata para backtracking.
        """
        visitadas = set(kb.visited)
        for celda in reversed(self.historial):
            for vecino in kb.neighbours(celda):
                if vecino not in visitadas and kb.is_safe(vecino):
                    return celda
        return None

    def bfs(self, inicio, objetivos, kb: KnowledgeBase, permitidas: set):
        """
        Realiza una búsqueda en anchura desde una celda inicial hasta
        cualquiera de los objetivos permitidos.

        Args:
            - inicio (tuple[int, int]): posición inicial.
            - objetivos (list[tuple[int, int]]): celdas objetivo.
            - kb (KnowledgeBase): base de conocimiento.
            - permitidas (set): celdas por las que se permite transitar.

        Returns:
            - plan (list[str]): secuencia de acciones para alcanzar el objetivo,
              o lista vacía si no existe camino.
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
        Reconstruye el plan de acciones a partir del diccionario de padres.

        Args:
            - objetivo (tuple[int, int]): celda objetivo alcanzada.
            - padres (dict): diccionario de predecesores.

        Returns:
            - plan (list[str]): lista de acciones a ejecutar.
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
        Traduce un movimiento entre dos celdas adyacentes a una acción.

        Args:
            - origen (tuple[int, int]): celda origen.
            - destino (tuple[int, int]): celda destino.

        Returns:
            - accion (str): acción correspondiente al movimiento.
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

        raise ValueError("Movimiento no válido")

def jugar_partida(console: Console, agente) -> dict:
    """
    Ejecuta el bucle principal de una partida: percibe, actualiza la KB, renderiza el estado,
    solicita/decide una acción y aplica la transición hasta que el jugador gane, muera o quede bloqueado.

    Args:
        - console (Console): consola Rich utilizada para mostrar el juego.
        - agente (object): agente que decide la acción en cada turno (manual o automático).

    Returns:
        - info (dict): diccionario con el resultado final de la partida (victoria, muerte o bloqueo)
                       y mensajes asociados si aplica.
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
                    "message": "Bloqueo lógico: no hay celdas seguras accesibles desde la posición actual."
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
            agente.plan = []  # por si acaso

def main() -> None:
    """
    Ejecuta el flujo principal del juego: muestra el menú inicial, inicia partidas en los distintos modos
    y gestiona la navegación entre menús hasta que el usuario salga.
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
                pantalla_game_over(console, "HAS MUERTO", "red")
            elif info.get("win"):
                pantalla_game_over(console, "VICTORIA", "green")

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
                pantalla_game_over(console, "HAS MUERTO", "red")
            elif info.get("win"):
                pantalla_game_over(console, "VICTORIA", "green")
            elif info.get("blocked"):
                pantalla_game_over(console, "BLOQUEO  LOGICO", "yellow")


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



