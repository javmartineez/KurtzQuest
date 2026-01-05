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

def bienvenida(console: Console) -> str:
    console.clear()

    figlet = pyfiglet.Figlet(font="slant")
    titulo_ascii = figlet.renderText("BUSCANDO \nAL\nCORONEL KURTZ vol.2")

    titulo = Text(titulo_ascii, style="bold cyan", justify="center")
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

def instrucciones(console: Console):
    console.clear()

    titulo1 = Text("INSTRUCCIONES DE LA MISIÓN", style="bold cyan", justify="center")
    titulo2 = Text("CONTROLES", style="bold cyan", justify="center")

    narrativa = (
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

    input("\nPulsa ENTER para volver al menú...")

def inicializar_palacio(N: int = 6):

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

def pantalla_carga(console: Console, segundos: float = 1.0):
    """
    Muestra una pantalla de carga simulada mediante un spinner en consola.

    Args:
        - console (Console)
        - segundos (float): Duración de la pantalla de carga en segundos.
    """

    console.clear()
    with console.status("[bold]Preparando el palacio...[/bold]", spinner="dots"):
        time.sleep(segundos)

def pantalla_game_over(console: Console, texto: str, color: str):
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
    
    N = mundo["N"]

    palacio = mundo["palacio"]

    pos = estado["agent_pos"]
    vecinos = neighbours(pos, N)

    # IMPORTANTE: enunciado = celda actual O adyacentes
    zona = vecinos + [pos]

    # Si palacio guarda sets:
    e_S = any("S" in palacio[v] for v in zona)

    # Militar solo si sigue vivo (y está en celda/adyacente)
    e_M = estado["soldado_vivo"] and any("M" in palacio[v] for v in zona)

    # Trampas (celda/adyacentes)
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
    
    La función comprueba si desde la posición actual existen límites
    del mapa que impidan el movimiento en alguna de las cuatro direcciones
    (arriba, abajo, izquierda y derecha).
    
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
    i, j = pos
    cand = [(i-1, j), (i+1, j), (i, j-1), (i, j+1)]
    return [(x, y) for x, y in cand if 0 <= x < N and 0 <= y < N]

class Beliefs:
    def __init__(self, N):
        self.N = N
        self.F = self._prior()
        self.P = self._prior()
        self.D = self._prior()
        self.M = self._prior()
        self.S = self._prior()
        self.visitadas = set()

    def _prior(self):
        P = np.ones((self.N, self.N), dtype=float)
        P[0, 0] = 0.0
        P /= P.sum()
        return P

    def update(self, P, pos, vecinos, estimulo):
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

def renormalizar(P):
    s = P.sum()
    if s == 0:
        raise ValueError("Contradicción: renormalizar con masa 0")
    return P / s

def update_beliefs(beliefs, estado, mundo, perceptos):
    N = mundo["N"]
    pos = estado["agent_pos"]
    vecinos = neighbours(pos, N)

    e_F, e_P, e_D, e_M, e_S = perceptos[0], perceptos[1], perceptos[2], perceptos[3], perceptos[4]
    grito = perceptos[9]

    # 0) Hecho del mundo: si hay grito, el soldado deja de existir
    if grito:
        estado["soldado_vivo"] = False
        beliefs.M[:] = 0.0
    else:
        # Solo tiene sentido actualizar M si el soldado sigue vivo
        if estado.get("soldado_vivo", True):
            beliefs.update(beliefs.M, pos, vecinos, e_M)

    # 1) Update bayesiano del resto (siempre)
    beliefs.update(beliefs.F, pos, vecinos, e_F)
    beliefs.update(beliefs.P, pos, vecinos, e_P)
    beliefs.update(beliefs.D, pos, vecinos, e_D)
    beliefs.update(beliefs.S, pos, vecinos, e_S)

    # 2) Marcar visitadas
    beliefs.visitadas.add(pos)

    # 3) Restricción dura en visitadas (si sigues vivo, ahí no hay nada)
    for v in beliefs.visitadas:
        beliefs.F[v] = 0.0
        beliefs.P[v] = 0.0
        beliefs.D[v] = 0.0
        beliefs.M[v] = 0.0  # ok: si soldado existe, no puede estar en visitadas; si no existe, ya era 0

    # 4) Renormalizar (solo distribuciones que siguen existiendo)
    beliefs.F = renormalizar(beliefs.F)
    beliefs.P = renormalizar(beliefs.P)
    beliefs.D = renormalizar(beliefs.D)

    if estado.get("soldado_vivo", True) and not grito:
        beliefs.M = renormalizar(beliefs.M)
    # beliefs.S: tú ya decidiste no renormalizar aquí, bien

from collections import deque, defaultdict
import math


class AgenteGreedy:
    """
    Agente greedy robusto con:
    - función de riesgo basada en probabilidad de morir al entrar en la casilla vecina
    - memoria anti-bucle (historial reciente + contador de visitas por celda)
    - modo escape si detecta ciclo
    - uso opcional de granada contra soldado con probabilidad alta
    """

    def __init__(
        self,
        p_umbral: float = 0.20,        # umbral "aceptable" de riesgo al moverse
        w_risk: float = 10.0,          # peso del riesgo (alto = más cobarde)
        w_exit: float = 2.0,           # peso de buscar salida (solo si has_kurtz)
        w_explore: float = 0.6,        # bonus por explorar casillas no visitadas
        grenade_trigger: float = 0.55, # dispara granada si P(soldado vecino) >= esto
        eps: float = 1e-9,
        recent_len: int = 12,          # memoria corta para anti-ciclo
        loop_trigger: int = 4,         # si la pos actual aparece >= esto en recent -> "ciclo"
        w_recent: float = 2.5,         # penalización por volver a casillas del historial reciente
        w_visit: float = 0.8,          # penalización por casillas muy visitadas (log)
    ):
        self.p_umbral = p_umbral
        self.w_risk = w_risk
        self.w_exit = w_exit
        self.w_explore = w_explore
        self.grenade_trigger = grenade_trigger
        self.eps = eps

        self.recent = deque(maxlen=recent_len)
        self.visit_counts = defaultdict(int)

        self.loop_trigger = loop_trigger
        self.w_recent = w_recent
        self.w_visit = w_visit


    def tope(self, x: float) -> float:
        if x < 0.0:
            return 0.0
        if x > 1.0:
            return 1.0
        return x

    def decidir(self, estado: dict, beliefs, mundo: dict) -> str:
        # NOTA: depende de que existan estas funciones en tu código:
        # - neighbours(pos, N)
        # y que beliefs.* permitan indexar con tuplas (i,j).

        N = mundo["N"]
        pos = estado["agent_pos"]
        vecinos = neighbours(pos, N)

        has_kurtz = bool(estado.get("has_kurtz", False))
        soldado_vivo = bool(estado.get("soldado_vivo", True))
        granada = bool(estado.get("granada", False))

        # 0) Salir: solo si llevas a Kurtz y estás prácticamente seguro de estar en una salida
        if has_kurtz and float(beliefs.S[pos]) > 0.99:
            return "EXIT"

        # 1) Memoria: marca que estás decidiendo desde esta celda
        self.visit_counts[pos] += 1
        self.recent.append(pos)

        # 2) Detectar ciclo / estancamiento: pos aparece muchas veces en recent
        repeats_here = 0
        for p in self.recent:
            if p == pos:
                repeats_here += 1
        escape_mode = repeats_here >= self.loop_trigger

        # 3) Granada: si el soldado vive y hay vecino con M alta, lánzala
        if soldado_vivo and granada and vecinos:
            v_best = None
            p_best = 0.0
            for v in vecinos:
                pM = self.tope(float(beliefs.M[v]))
                if pM > p_best:
                    p_best, v_best = pM, v
            if v_best is not None and p_best >= self.grenade_trigger:
                return self._accion_granada(pos, v_best)

        # 4) Evaluar candidatos
        candidatos = []
        for v in vecinos:
            # Probabilidades base (clamp por robustez)
            p_trampa = self.tope(float(beliefs.F[v] + beliefs.P[v] + beliefs.D[v]))
            p_sold = self.tope(float(beliefs.M[v])) if soldado_vivo else 0.0

            # Riesgo de morir al ENTRAR en v: unión (asumiendo independencia)
            risk = 1.0 - (1.0 - p_trampa) * (1.0 - p_sold)
            risk = self.tope(risk)

            # Salida solo importa si puedes ganar (has_kurtz)
            p_exit = self.tope(float(beliefs.S[v])) if has_kurtz else 0.0

            # Bonus por explorar
            unvisited = 1.0 if v not in beliefs.visitadas else 0.0

            # Penalizaciones anti-bucle
            recent_pen = 1.0 if v in self.recent else 0.0
            visit_pen = math.log1p(self.visit_counts.get(v, 0))

            # En escape_mode aprietas más contra repetir y relajas el umbral
            w_recent_eff = self.w_recent * (2.0 if escape_mode else 1.0)
            w_visit_eff = self.w_visit * (1.5 if escape_mode else 1.0)

            p_umbral_eff = self.p_umbral * (1.3 if escape_mode else 1.0)
            if p_umbral_eff > 0.95:
                p_umbral_eff = 0.95

            score = (
                - self.w_risk * risk
                + self.w_exit * p_exit
                + self.w_explore * unvisited
                - w_recent_eff * recent_pen
                - w_visit_eff * visit_pen
            )

            candidatos.append((v, score, risk, unvisited, recent_pen, visit_pen, p_umbral_eff))

        if not candidatos:
            return "BLOCKED"

        # 5) Si hay opciones bajo el umbral, elegimos la mejor por score con desempates sanos
        p_umbral_eff = candidatos[0][6]
        seguras = []
        for c in candidatos:
            if c[2] <= p_umbral_eff + self.eps:
                seguras.append(c)

        def key_mejor(c):
            # c = (v, score, risk, unvisited, recent_pen, visit_pen, p_umbral_eff)
            # Preferencia:
            # 1) mayor score
            # 2) menor riesgo
            # 3) evitar volver a recent
            # 4) preferir no visitadas
            # 5) menos visitadas (visit_pen bajo)
            return (c[1], -c[2], -c[4], c[3], -c[5])

        if seguras:
            best = max(seguras, key=key_mejor)
        else:
            # 6) Si todo es peligroso: minimiza riesgo y rompe empates favoreciendo salir del ciclo
            # Orden:
            # 1) menor risk
            # 2) no volver a recent
            # 3) menos visitada
            # 4) preferir nueva
            # 5) mayor score
            best = min(candidatos, key=lambda c: (c[2], c[4], c[5], -c[3], -c[1]))

        return self._accion(pos, best[0])

    def _accion(self, origen, destino) -> str:
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

    def _accion_granada(self, origen, destino) -> str:
        mov = self._accion(origen, destino)
        return "GRENADE_" + mov



def elegir_movimiento_usuario(pos, beliefs, mundo, estado):
    N = mundo["N"]
    vecinos = neighbours(pos, N)

    # WASD → acción
    mov_map = {
        "W": "UP",
        "S": "DOWN",
        "A": "LEFT",
        "D": "RIGHT",
    }

    # acción → delta (solo para mostrar info)
    delta = {
        "UP": (-1, 0),
        "DOWN": (1, 0),
        "LEFT": (0, -1),
        "RIGHT": (0, 1),
    }

    print("\n--- ELIGE ACCIÓN ---")
    print(f"Posición actual: {pos}")
    print("Opciones:")

    for k, action in mov_map.items():
        di, dj = delta[action]
        v = (pos[0] + di, pos[1] + dj)
        if v in vecinos:
            p_trampa = float(beliefs.F[v] + beliefs.P[v] + beliefs.D[v])
            p_sold   = float(beliefs.M[v])
            p_exit   = float(beliefs.S[v])
            print(f"  {k} ({action}) -> {v} | "
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
            if dir_key in mov_map:
                return f"GRENADE_{mov_map[dir_key]}"

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
        if t in mov_map:
            return mov_map[t]

        print("Entrada inválida.")

def funcion_transicion(estado: dict, mundo: dict, accion: str):
    """
    Devuelve (nuevo_estado, info)
    info puede contener: moved, dead, win, hit_wall, invalid_exit, picked_kurtz, grenade, killed_soldier...
    """
    palacio = mundo["palacio"]
    N = mundo["N"]

    nuevo = dict(estado)
    nuevo["ultima_accion_matar_soldado"] = False

    MOVES = {"UP": (-1,0), "DOWN": (1,0), "LEFT": (0,-1), "RIGHT": (0,1)}

    # ---------------- EXIT ----------------
    if accion == "EXIT":
        # solo puedes salir si estás en una celda con "S"
        celda = palacio[nuevo["agent_pos"]]
        if "S" not in celda:
            return nuevo, {"invalid_exit": True, "message": "No estás en la salida."}

        if not nuevo.get("has_kurtz", False):
            return nuevo, {"win": False, "message": "No puedes ganar sin Kurtz. Debes encontrarlo primero."}

        return nuevo, {"win": True, "message": "Kurtz y tú habéis salido del palacio juntos."}

    # ---------------- GRENADE ----------------
    if accion.startswith("GRENADE_"):
        if not nuevo.get("granada", False):
            return nuevo, {"message": "Ya no tienes granada."}

        dir_ = accion.split("_", 1)[1]  # "UP"/"DOWN"/...
        if dir_ not in MOVES:
            return nuevo, {"invalid_action": True, "message": f"Dirección inválida: {dir_}"}

        # La granada se consume SIEMPRE al lanzarla (igual que en tu kurtz.py)
        nuevo["granada"] = False

        di, dj = MOVES[dir_]
        i, j = nuevo["agent_pos"]
        target = (i + di, j + dj)

        if not (0 <= target[0] < N and 0 <= target[1] < N):
            return nuevo, {"grenade": True, "hit_wall": True, "message": "La granada golpea la pared y se desperdicia."}

        # Si hay soldado en la celda objetivo y sigue vivo -> muere
        celda_t = palacio[target]
        if nuevo.get("soldado_vivo", True) and ("M" in celda_t):
            nuevo["soldado_vivo"] = False
            nuevo["ultima_accion_matar_soldado"] = True
            return nuevo, {"grenade": True, "killed_soldier": True, "message": "¡Soldado eliminado!"}

        # Si cae en CK o en otra casilla, no pasa nada (sin efectos colaterales)
        return nuevo, {"grenade": True, "message": "La granada explota sin efecto."}

    # ---------------- MOVE ----------------
    if accion not in MOVES:
        return nuevo, {"invalid_action": True, "message": f"Acción inválida: {accion}"}

    i, j = nuevo["agent_pos"]
    di, dj = MOVES[accion]
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

    # muerte por soldado (si sigue vivo)
    if nuevo.get("soldado_vivo", True) and ("M" in celda):
        return nuevo, {"dead": True, "cause": "SOLDIER"}

    return nuevo, {"moved": True}

def jugar_partida_bayes(console: Console) -> dict:
    """
    Partida manual Bayes.
    Devuelve info final:
      - {"dead": True, ...}
      - {"win": True, ...}
      - {"blocked": True, ...}  (si contradicción en creencias)
    """

    # 0) Inicializar mundo y estado
    mundo, estado = inicializar_palacio(N=6)  # o el N que quieras
    beliefs = Beliefs(mundo["N"])

    # 1) Primer percepto + update inicial (antes de mover)
    try:
        perceptos = percept(estado, mundo)
        update_beliefs(beliefs, estado, mundo, perceptos)
    except ValueError:
        # Contradicción desde el inicio (muy raro, pero posible si algo está mal)
        return {"blocked": True, "message": "Contradicción inicial en creencias."}

    while True:
        console.clear()

        # 2) Render (usa el que tengas)
        # Si estás usando entorno2.render_bayes:
        # entorno2.render_bayes(console, mundo, estado, beliefs)
        # Si tienes otro render, cámbialo aquí.
        entorno_palacio2.render_bayes(console, mundo, estado, beliefs)

        # 3) Elegir acción por usuario (UP/DOWN/LEFT/RIGHT, GRENADE_*, EXIT)
        accion = elegir_movimiento_usuario(estado["agent_pos"], beliefs, mundo, estado)

        # 4) Aplicar transición del mundo REAL
        estado, info = funcion_transicion(estado, mundo, accion)

        # 5) Si murió / ganó -> cortar
        if info.get("dead"):
            return {"dead": True, **info}

        if info.get("win"):
            return {"win": True, **info}

        # 6) Nuevo percepto + update bayesiano
        try:
            perceptos = percept(estado, mundo)
            update_beliefs(beliefs, estado, mundo, perceptos)
        except ValueError:
            # Tu update_beliefs lanza ValueError("Contradicción")
            return {"blocked": True, "message": "Bloqueo lógico: contradicción en creencias."}

def jugar_partida_bayes_greedy(console: Console, agente) -> dict:
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



def main():
    console = Console()
    game_mode = bienvenida(console)

    while True:

        # 1) Instrucciones
        if game_mode == "1":
            instrucciones(console)
            game_mode = bienvenida(console)
            continue

        # 2) Modo manual (usuario decide movimientos viendo mapas)
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

            if opcion == "1":      # rejugar mismo modo
                continue
            if opcion == "2":      # volver al menú principal
                game_mode = bienvenida(console)
                continue
            if opcion == "3":      # salir
                return


        elif game_mode == "3":
            agente = AgenteGreedy()     # <- pon el nombre real de tu agente automático
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
