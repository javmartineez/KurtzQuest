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
    Muestra el menú principal del juego y solicita al usuario el modo de juego.

    Args:
        - console (Console): consola Rich utilizada para mostrar la interfaz.

    Returns:
        - game_mode (str): opción seleccionada por el usuario.
    """
    console.clear()

    figlet = pyfiglet.Figlet(font="slant")
    titulo = figlet.renderText("BUSCANDO \nAL\nCORONEL KURTZ vol.2")

    titulo = Text(titulo, style="bold cyan", justify="center")
    console.print(Panel(Align.center(titulo), border_style="cyan", padding=(1, 4)))

    # Panel de opciones (lo que quieres)
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

    instrucciones = (
        "[bold cyan]SEGUNDA FASE:[/bold cyan] Razonamiento bajo incertidumbre\n"
        "Debes encontrar al [bold magenta]Coronel Kurtz (CK)[/bold magenta] y salir con vida del palacio, "
        "pero en esta fase, el entorno es incierto y solo dispones de información parcial, obtenida a través de tus percepciones.\n\n"
        "Para ayudarte a decidir, el sistema muestra simultáneamente [bold]cuatro mapas[/bold]:\n\n"
        "[bold cyan]1. Mapa de exploración[/bold cyan]\n"
        "Muestra las habitaciones por las que ya has pasado. "
        "Las celdas visitadas quedan marcadas para que puedas seguir tu recorrido.\n"
        "[bold cyan]2. Mapa de trampas[/bold cyan]\n"
        "Representa la [bold]probabilidad de que una habitación contenga una trampa mortal[/bold] "
        "El color indica el riesgo: cuanto más intenso, mayor es la probabilidad de toparse con una.\n"
        "[bold cyan]3. Mapa del soldado[/bold cyan]\n"
        "Indica la [bold]probabilidad de encontrarte con el soldado enemigo[/bold] en cada habitación. "
        "Recuerda que el soldado es letal si está vivo, pero puedes eliminarlo usando la granada.\n"
        "[bold cyan]4. Mapa de la salida[/bold cyan]\n"
        "Muestra la [bold]probabilidad de que una habitación sea la salida del palacio[/bold]. "
        "A medida que exploras y percibes el entorno, este mapa se va refinando.\n\n"
        "Tu objetivo sigue siendo el mismo: encontrar a Kurtz y salir con vida. "
        "[bold]Buena suerte, capitán.[/bold]"
    )

    controles = (
        "Utiliza [bold cyan]W/A/S/D[/bold cyan] para moverte arriba/izquierda/abajo/derecha respectivamente.\n"
        "Utiliza [bold cyan]G[/bold cyan] para lanzar la granada. Tras lanzarla, deberás especificar "
        "la direccion del lanzamiento mediante W/A/S/D\n"
        "Tras encontrar la salida, utiliza la [bold cyan]E[/bold cyan] para salir"
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

def inicializar_palacio(N: int = 6):
    """
    Inicializa el entorno del palacio generando el tablero y 
    el estado inicial del agente, y mostrando una pantalla de 
    carga previa al inicio de la partida.

    Args:
        - N (int): tamaño del palacio (N x N). Por defecto, 6.

    Returns:
        - mundo (dict): diccionario que contiene el tablero del palacio
                        y el tamaño del entorno.
        - estado_0 (dict): estado inicial del agente, incluyendo posición,
                           estado del soldado, granada y flags internos.
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
    Muestra una pantalla tras finalizar la partida.

    Args:
        - console (Console): consola Rich utilizada para renderizar la pantalla.
        - texto (str): texto principal que se mostrará en formato ASCII.
        - color (str): color utilizado para el texto y el borde del panel.
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
    Muestra el menú posterior a una partida y solicita al usuario qué hacer a continuación:
    reintentar, volver al menú principal o salir del programa.

    Args:
        - console (Console): consola Rich utilizada para mostrar el panel de opciones.

    Returns:
        - opcion (str): opción elegida por el usuario ("1", "2" o "3").
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
        x = input("Elige [1/2/3]: ").strip()
        if x in {"1", "2", "3"}:
            return x
        console.print("[bold red]Entrada inválida.[/bold red] Escribe 1, 2 o 3.")

def percept(estado: dict, mundo: dict) -> list[bool]:
    """
    Calcula el percepto del agente a partir de su posición actual, detectando la 
    presencia de elementos (F, P, D, M, S) en la zona formada por la celda actual
    y sus vecinos, además de paredes y el grito tras matar al soldado.

    Args:
        - estado (dict): estado actual del agente (posición, flags y estado del soldado).
        - mundo (dict): información del entorno (tablero y tamaño N).

    Returns:
        - perceptos (list[bool]): lista de booleanos con el siguiente orden:
          [e_F, e_P, e_D, e_M, e_S, pared_arriba, pared_abajo, pared_izq, pared_der, grito].
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

def neighbours(pos: tuple[int, int], N: int) -> list[tuple[int, int]]:
    """
    Devuelve las celdas vecinas válidas (arriba, abajo, izquierda y derecha)
    de una posición dada dentro del tablero.

    Args:
        - pos (tuple[int, int]): posición actual (fila, columna).
        - N (int): tamaño del palacio (N x N).

    Returns:
        - vecinos (list[tuple[int, int]]): lista de celdas vecinas dentro de los límites del tablero.
    """
    i, j = pos
    cand = [(i-1, j), (i+1, j), (i, j-1), (i, j+1)]
    return [(x, y) for x, y in cand if 0 <= x < N and 0 <= y < N]

class Beliefs:
    """
    Mantiene distribuciones de probabilidad (matrices N x N) para cada tipo de elemento
    del palacio (F, P, D, M, S) y el conjunto de celdas visitadas por el agente.
    """

    def __init__(self, N):
        """
        Inicializa las creencias con un prior uniforme sobre el tablero, excluyendo
        la celda inicial (0,0), que se asume segura.

        Args:
            - N (int): tamaño del palacio (N x N).
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
        Genera un prior uniforme sobre todas las celdas del tablero salvo la inicial (0,0).

        Returns:
            - prior (np.ndarray): matriz N x N normalizada con probabilidad cero en (0,0).
        """
        P = np.ones((self.N, self.N), dtype=float)
        P[0, 0] = 0.0
        P /= P.sum()
        return P

    def update(self, P, pos, vecinos, estimulo):
        """
        Actualiza una distribución de probabilidad en función de un estímulo observado.
        Si el estímulo es True, el elemento debe estar en la zona (celda actual o vecinos).
        Si el estímulo es False, el elemento no puede estar en esa zona.
        Tras aplicar la restricción, renormaliza la matriz.

        Args:
            - P (np.ndarray): matriz de probabilidades a actualizar.
            - pos (tuple[int, int]): posición actual del agente.
            - vecinos (list[tuple[int, int]]): vecinos de la posición actual.
            - estimulo (bool): indica si el estímulo asociado al elemento está presente.
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
            raise ValueError("Contradicción")
        P /= s

def renormalizar(P: np.ndarray) -> np.ndarray:
    """
    Renormaliza una matriz de probabilidades para que su suma total sea 1.
    Si la masa total es 0, lanza una excepción por contradicción.

    Args:
        - P (np.ndarray): matriz de probabilidades a renormalizar.

    Returns:
        - P_norm (np.ndarray): matriz renormalizada con suma total 1.
    """
    s = P.sum()
    if s == 0:
        raise ValueError("Contradicción: renormalizar con masa 0")
    return P / s

def update_beliefs(beliefs: Beliefs, estado: dict, mundo: dict, perceptos: list) -> None:
    """
    Actualiza las creencias bayesianas del agente a partir del percepto observado,
    aplicando restricciones de presencia/ausencia sobre F, P, D, M y S en la zona
    (celda actual + vecinos), gestionando el caso de muerte del soldado y dando
    probabilidad cero a celdas visitadas.

    Args:
        - beliefs (Beliefs): estructura que contiene las distribuciones de probabilidad del agente.
        - estado (dict): estado actual del agente (posición, flags y estado del soldado).
        - mundo (dict): información del entorno (incluye N y el tablero).
        - perceptos (list[bool]): lista de perceptos en el orden:
          [e_F, e_P, e_D, e_M, e_S, pared_arriba, pared_abajo, pared_izq, pared_der, grito].
    """

    N = mundo["N"]
    pos = estado["agent_pos"]
    vecinos = neighbours(pos, N)

    e_F, e_P, e_D, e_M, e_S = perceptos[0], perceptos[1], perceptos[2], perceptos[3], perceptos[4]
    grito = perceptos[9]

    #si hay grito, el soldado deja de existir
    if grito:
        estado["soldado_vivo"] = False
        beliefs.M[:] = 0.0
    else:
        # Solo tiene sentido actualizar M si el soldado sigue vivo
        if estado.get("soldado_vivo", True):
            beliefs.update(beliefs.M, pos, vecinos, e_M)

    beliefs.update(beliefs.F, pos, vecinos, e_F)
    beliefs.update(beliefs.P, pos, vecinos, e_P)
    beliefs.update(beliefs.D, pos, vecinos, e_D)
    beliefs.update(beliefs.S, pos, vecinos, e_S)

    beliefs.visitadas.add(pos)

    #Si se está vivo, la probabilidad de peligro es 0
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
    Agente greedy que selecciona movimientos maximizando una puntuación que combina:
    - riesgo estimado de morir al entrar en una celda (trampas + soldado)
    - preferencia por explorar celdas no visitadas
    - preferencia por acercarse a la salida cuando ya se ha encontrado a Kurtz
    - penalización por bucles
    Además, puede lanzar la granada si detecta alta probabilidad de soldado en un vecino.
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
        Inicializa el agente greedy y sus parámetros de decisión.

        Args:
            - p_umbral (float): umbral "aceptable" de riesgo al moverse (si hay opciones por debajo, se priorizan).
            - w_risk (float): peso del riesgo en la puntuación (más alto = más conservador).
            - w_exit (float): peso de la probabilidad de salida (solo se aplica si has_kurtz es True).
            - w_explore (float): bonus por explorar celdas no visitadas.
            - grenade_trigger (float): umbral para lanzar granada si P(soldado vecino) lo supera.
            - eps (float): tolerancia numérica para comparar riesgos con el umbral.
            - recent_len (int): longitud de memoria corta para detectar y penalizar ciclos.
            - loop_trigger (int): número de apariciones de la posición actual en la memoria reciente para activar modo escape.
            - w_recent (float): penalización por volver a celdas del historial reciente.
            - w_visit (float): penalización por visitar celdas demasiadas veces (logarítmica).
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
        Acota un valor al intervalo [0, 1] para evitar probabilidades inválidas.

        Args:
            - x (float): valor a acotar.

        Returns:
            - x_acotado (float): valor dentro de [0, 1].
        """
        if x < 0.0:
            return 0.0
        if x > 1.0:
            return 1.0
        return x

    def decidir(self, estado: dict, beliefs, mundo: dict) -> str:
        """
        Decide la siguiente acción en base a las creencias (beliefs) y al estado actual.
        Prioridades principales:
        - salir si ya tienes a Kurtz y la probabilidad de salida en la celda es casi 1
        - lanzar granada si hay alta probabilidad de soldado en una celda adyacente
        - elegir el vecino con mejor puntuación, evitando ciclos
        Si no hay vecinos válidos, devuelve "BLOCKED".

        Args:
            - estado (dict): estado del agente (posiciones y flags: has_kurtz, soldado_vivo, granada).
            - beliefs (Beliefs): estructura con matrices de probabilidad F/P/D/M/S y conjunto visitadas.
            - mundo (dict): información del entorno (incluye el tamaño N).

        Returns:
            - accion (str): acción seleccionada ("UP", "DOWN", "LEFT", "RIGHT", "EXIT" o "GRENADE_DIR").
        """
        N = mundo["N"]
        posicion = estado["agent_pos"]
        vecinos = neighbours(posicion, N)

        tiene_kurtz = bool(estado.get("has_kurtz", False))
        soldado_vivo = bool(estado.get("soldado_vivo", True))
        tiene_granada = bool(estado.get("granada", False))

        # 0) Salir si ya puedes ganar y estás prácticamente seguro de estar en salida
        if tiene_kurtz and float(beliefs.S[posicion]) > 0.99:
            return "EXIT"

        # 1) Memoria
        self.conteo_visitas[posicion] += 1
        self.reciente.append(posicion)

        repeticiones_aqui = 0
        for p in self.reciente:
            if p == posicion:
                repeticiones_aqui += 1
        modo_escape = repeticiones_aqui >= self.disparador_bucle

        # 2) Granada
        if soldado_vivo and tiene_granada and vecinos:
            mejor_vecino = None
            mejor_prob = 0.0

            for vecino in vecinos:
                p_militar = self.tope(float(beliefs.M[vecino]))
                if p_militar > mejor_prob:
                    mejor_prob, mejor_vecino = p_militar, vecino

            if mejor_vecino is not None and mejor_prob >= self.umbral_granada:
                return self.accion_granada(posicion, mejor_vecino)

        # 3) Evaluar candidatos
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

        # 4) elegir la mejor por score
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
        Traduce un movimiento entre dos celdas adyacentes a una acción.

        Args:
            - origen (tuple[int, int]): celda de origen (fila, columna).
            - destino (tuple[int, int]): celda destino adyacente (fila, columna).

        Returns:
            - accion (str): acción equivalente ("UP", "DOWN", "LEFT" o "RIGHT").
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

        raise ValueError("Movimiento no válido")

    def accion_granada(self, origen, destino) -> str:
        """
        Construye la acción de lanzamiento de granada hacia una celda adyacente.

        Args:
            - origen (tuple[int, int]): celda desde la que se lanza la granada.
            - destino (tuple[int, int]): celda objetivo adyacente.

        Returns:
            - accion (str): acción con prefijo de granada ("GRENADE_UP", etc.).
        """
        movimiento = self.accion(origen, destino)
        return "GRANADA_" + movimiento

def elegir_movimiento_usuario(pos: tuple, beliefs: Beliefs, mundo: dict, estado: dict) -> str:
    """
    Solicita al usuario una acción.
    Permite movimiento (W/A/S/D), lanzar granada (G) y salir (E) si se cumplen
    las condiciones de victoria.

    Args:
        - pos (tuple[int, int]): posición actual del agente.
        - beliefs (Beliefs): creencias del agente con matrices F, P, D, M y S.
        - mundo (dict): diccionario del entorno (incluye N y el tablero palacio).
        - estado (dict): estado actual del agente (granada, has_kurtz, etc.).

    Returns:
        - accion (str): acción elegida por el usuario ("UP", "DOWN", "LEFT", "RIGHT",
          "EXIT" o "GRENADE_DIR").
    """
    N = mundo["N"]
    vecinos = neighbours(pos, N)

    mapa_mov = {"W": "UP", "S": "DOWN", "A": "LEFT", "D": "RIGHT"}
    direcciones = {"UP": (-1, 0), "DOWN": (1, 0), "LEFT": (0, -1), "RIGHT": (0, 1)}

    print("\n--- ELIGE ACCIÓN ---")
    print(f"Posición actual: {pos}")
    print("Opciones:")

    for k, accion in mapa_mov.items():
        di, dj = direcciones[accion]
        v = (pos[0] + di, pos[1] + dj)
        if v in vecinos:
            p_trampa = float(beliefs.F[v] + beliefs.P[v] + beliefs.D[v])
            p_sold   = float(beliefs.M[v])
            p_exit   = float(beliefs.S[v])
            print(f"  {k} ({accion}) -> {v} | "
                  f"P(trampa)={p_trampa:.2f} | "
                  f"P(soldado)={p_sold:.2f} | "
                  f"P(salida)={p_exit:.2f}")

    if estado.get("granada", False):
        print("  G (GRANADA)")

    while True:
        t = input("Acción (W/A/S/D o G): ").strip().upper()

        # GRANADA
        if t == "G":
            if not estado.get("granada", False):
                print("No te queda granada.")
                continue

            dir_key = input("Dirección granada (W/A/S/D): ").strip().upper()
            if dir_key in mapa_mov:
                return f"GRANADA_{mapa_mov[dir_key]}"

            print("Dirección inválida.")
            continue

        if t == "E":
            if "S" not in mundo["palacio"][pos]:
                print("No puedes salir: no estás en la salida.")
                continue

            if not estado.get("has_kurtz", False):
                print("No puedes salir: todavía no has encontrado a Kurtz.")
                continue

            return "EXIT"


        # MOVIMIENTO NORMAL
        if t in mapa_mov:
            return mapa_mov[t]

        print("Entrada inválida.")

def funcion_transicion(estado: dict, mundo: dict, accion: str):
    """
    Aplica una acción al estado actual y devuelve el nuevo estado junto con información
    del resultado (movimiento, muerte, victoria, acción inválida o choque con pared).
    Gestiona acciones de movimiento, salida y lanzamiento de granada.

    Args:
        - estado (dict): estado actual del agente (posición, flags y recursos).
        - mundo (dict): información del entorno (tablero del palacio y tamaño N).
        - accion (str): acción a ejecutar ("UP", "DOWN", "LEFT", "RIGHT", "EXIT" o "GRANADA_DIR").

    Returns:
        - nuevo (dict): estado actualizado tras aplicar la acción.
        - info (dict): diccionario con flags del resultado y, si aplica, un mensaje.
    """
    palacio = mundo["palacio"]
    N = mundo["N"]

    nuevo = dict(estado)
    nuevo["ultima_accion_matar_soldado"] = False

    direcciones = {"UP": (-1,0), "DOWN": (1,0), "LEFT": (0,-1), "RIGHT": (0,1)}

    # ---------------- SALIDA ----------------
    if accion == "EXIT":
        # solo se puede salir si estás en una celda con "S"
        celda = palacio[nuevo["agent_pos"]]
        if "S" not in celda:
            return nuevo, {"invalid_exit": True, "message": "No estás en la salida."}

        if not nuevo.get("has_kurtz", False):
            return nuevo, {"win": False, "message": "No puedes ganar sin Kurtz. Debes encontrarlo primero."}

        return nuevo, {"win": True, "message": "Kurtz y tú habéis salido del palacio juntos."}

    # ---------------- GRANADA ----------------
    if accion.startswith("GRANADA_"):
        if not nuevo.get("granada", False):
            return nuevo, {"message": "Ya no tienes granada."}

        dir_ = accion.split("_", 1)[1]
        if dir_ not in direcciones:
            return nuevo, {"invalid_action": True, "message": f"Dirección inválida: {dir_}"}

        nuevo["granada"] = False

        di, dj = direcciones[dir_]
        i, j = nuevo["agent_pos"]
        target = (i + di, j + dj)

        if not (0 <= target[0] < N and 0 <= target[1] < N):
            return nuevo, {"grenade": True, "hit_wall": True, "message": "La granada golpea la pared y se desperdicia."}

        celda_t = palacio[target]
        if nuevo.get("soldado_vivo", True) and ("M" in celda_t):
            nuevo["soldado_vivo"] = False
            nuevo["ultima_accion_matar_soldado"] = True
            return nuevo, {"grenade": True, "killed_soldier": True, "message": "¡Soldado eliminado!"}

        return nuevo, {"grenade": True, "message": "La granada explota sin efecto."}

    # ---------------- MOVIMIENTO ----------------
    if accion not in direcciones:
        return nuevo, {"invalid_action": True, "message": f"Acción inválida: {accion}"}

    i, j = nuevo["agent_pos"]
    di, dj = direcciones[accion]
    ni, nj = i + di, j + dj

    if not (0 <= ni < N and 0 <= nj < N):
        return nuevo, {"hit_wall": True, "message": "Te chocas con una pared."}

    nuevo["agent_pos"] = (ni, nj)

    celda = palacio[(ni, nj)]

    # recoger a Kurtz
    if (not nuevo.get("has_kurtz", False)) and ("CK" in celda):
        nuevo["has_kurtz"] = True
        return nuevo, {"moved": True, "picked_kurtz": True, "message": "Has encontrado a Kurtz. Ahora vais juntos."}

    # muerte por trampas
    if ("F" in celda) or ("P" in celda) or ("D" in celda):
        return nuevo, {"dead": True, "cause": "TRAP"}

    # muerte por soldado
    if nuevo.get("soldado_vivo", True) and ("M" in celda):
        return nuevo, {"dead": True, "cause": "SOLDIER"}

    return nuevo, {"moved": True}

def jugar_partida_bayes(console: Console) -> dict:
    """
    Ejecuta una partida con control manual del usuario.
    El agente actualiza sus creencias a partir de los perceptos y permite al usuario
    decidir la acción en cada turno hasta ganar, morir o quedar bloqueado.

    Args:
        - console (Console): consola Rich utilizada para renderizar el estado del juego.

    Returns:
        - resultado (dict): diccionario con el resultado final de la partida
          (victoria, muerte o bloqueo) y la información asociada.
    """

    #Inicializar mundo y estado
    mundo, estado = inicializar_palacio(N=6)
    beliefs = Beliefs(mundo["N"])

    try:
        perceptos = percept(estado, mundo)
        update_beliefs(beliefs, estado, mundo, perceptos)
    except ValueError:
        return {"blocked": True, "message": "Contradicción inicial en creencias."}

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
            return {"blocked": True, "message": "Bloqueo lógico: contradicción en creencias."}

def jugar_partida_bayes_greedy(console: Console, agente) -> dict:
    """
    Ejecuta una partida completa con un agente automático greedy.
    El agente decide las acciones en función de las creencias probabilísticas,
    actualizadas a partir de los perceptos, hasta ganar, morir o quedar bloqueado.

    Args:
        - console (Console): consola Rich utilizada para renderizar el estado del juego.
        - agente (object): agente automático encargado de decidir la acción en cada turno.

    Returns:
        - resultado (dict): diccionario con el resultado final de la partida
          (victoria, muerte o bloqueo) e información asociada.
    """
    mundo, estado = inicializar_palacio(N=6)
    beliefs = Beliefs(mundo["N"])

    try:
        perceptos = percept(estado, mundo)
        update_beliefs(beliefs, estado, mundo, perceptos)
    except ValueError:
        return {"blocked": True, "message": "Contradicción inicial en creencias."}

    while True:
        entorno_palacio2.render_bayes(console, mundo, estado, beliefs)

        accion = agente.decidir(estado, beliefs, mundo)
        time.sleep(0.3)

        if accion == "BLOCKED":
            return {"blocked": True, "message": "Bloqueo: sin acción seleccionable."}

        estado, info = funcion_transicion(estado, mundo, accion)

        if info.get("dead"):
            return {"dead": True, **info}
        if info.get("win"):
            return {"win": True, **info}

        try:
            perceptos = percept(estado, mundo)
            update_beliefs(beliefs, estado, mundo, perceptos)
        except ValueError:
            return {"blocked": True, "message": "Bloqueo lógico: contradicción en creencias."}

def main() -> None:
    """
    Función del flujo principal del programa.
    Muestra el menú inicial, gestiona la navegación entre modos de juego
    (instrucciones, modo manual bayesiano y modo automático greedy) y
    controla el ciclo de partidas hasta que el usuario decide salir.
    """
    console = Console()
    game_mode = bienvenida(console)

    while True:

        # 1) Instrucciones
        if game_mode == "1":
            instrucciones(console)
            game_mode = bienvenida(console)
            continue

        # 2) Modo manual
        elif game_mode == "2":
            
            info = jugar_partida_bayes(console)

            if info.get("dead"):
                pantalla_game_over(console, "HAS MUERTO", "red")
            elif info.get("win"):
                pantalla_game_over(console, "VICTORIA", "green")
            elif info.get("blocked"):
                pantalla_game_over(console, "BLOQUEO LÓGICO", "yellow")

            time.sleep(1.5)
            opcion = menu_post_partida(console)

            if opcion == "1":      
                continue
            if opcion == "2":  
                game_mode = bienvenida(console)
                continue
            if opcion == "3": 
                return

        # 3) Modo automático 
        elif game_mode == "3":
            agente = AgenteGreedy() 
            info = jugar_partida_bayes_greedy(console, agente)

            if info.get("dead"):
                pantalla_game_over(console, "HAS MUERTO", "red")
            elif info.get("win"):
                pantalla_game_over(console, "VICTORIA", "green")
            elif info.get("blocked"):
                pantalla_game_over(console, "BLOQUEO LÓGICO", "yellow")

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
