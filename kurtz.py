import entorno
from knowledge_base import KnowledgeBase
import search_algorithms as search
from rich.panel import Panel
from rich.align import Align
from rich.console import Console
from rich.text import Text 
import time
import pyfiglet

N = 6

def bienvenida(console: Console) -> str:
    console.clear()

    figlet = pyfiglet.Figlet(font="slant")
    titulo_ascii = figlet.renderText("BUSCANDO \nAL\nCORONEL KURTZ")

    titulo = Text(titulo_ascii, style="bold cyan", justify="center")
    console.print(Panel(Align.center(titulo), border_style="cyan", padding=(1, 4)))

    # Panel de opciones (lo que quieres)
    opciones = (
        "[bold cyan]1.[/bold cyan] [bold]¿Cómo jugar?[/bold]  [dim]→ reglas y controles[/dim]\n"
        "[bold cyan]2.[/bold cyan] [bold]Modo de juego Manual[/bold]  [dim]→ tú eliges acciones[/dim]\n"
        "[bold cyan]3.[/bold cyan] [bold]Modo por algoritmos[/bold]  [dim]→ BFS-DFS-Greedy-A*[/dim]\n"
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
        console.print("[bold red]Entrada inválida.[/bold red] Escribe 1, 2 o 3.")

def instrucciones(console: Console):
    console.clear()

    titulo1 = Text("INSTRUCCIONES DE LA MISIÓN", style="bold cyan", justify="center")
    titulo2 = Text("CONTROLES", style="bold cyan", justify="center")

    narrativa = (
        "Tu misión es clara y no admite errores.\n"
        "Debes adentrarte en el palacio y encontrar al [bold magenta]Coronel Kurtz (CK)[/bold magenta], "
        "cuya ubicación es completamente desconocida. Una vez lo encuentres, deberéis "
        "[bold]salir juntos y con vida[/bold] del palacio.\n\n"
        "Cuando localices al coronel, lo sabrás de inmediato: tu figura, el "
        "[bold orange1]Capitán Willard (CW)[/bold orange1], pasará a mostrarse en [bold magenta]morado[/bold magenta], "
        "indicando que ya no caminas solo.\n\n"
        "Pero mantente alerta.\n"
        "El palacio está en ruinas y plagado de peligros. Algunas habitaciones esconden "
        "[bold red]precipicios[/bold red] mortales dado el mal estado del palacio. "
        "Otras pueden albergar a un [bold yellow]soldado enemigo[/bold yellow] que acabará contigo.\n\n"
        "Dispones de una única [bold]granada[/bold]. Úsala con cabeza: solo puede lanzarse "
        "a una habitación contigua (arriba, abajo, izquierda o derecha). Un error y estarás indefenso.\n\n"
        "Las habitaciones por las que ya hayas pasado quedarán marcadas en "
        "[bold blue]azul[/bold blue], para que nunca pierdas la noción de tu recorrido. "
        "La [bold green]salida[/bold green] del palacio se distingue claramente de color verde pero recuerda:"
        "Si intentas salir sin el coronel, habrás fracasado.\n"
        "Respira hondo. Observa. Deduce.\n"
        "[bold]Buena suerte, soldado.[/bold]"
    )

    controles = (
        "Utiliza [bold cyan]W/A/S/D[/bold cyan] para moverte arriba/izquierda/abajo/derecha respectivamente.\n"
        "Utiliza [bold cyan]G[/bold cyan] para lanzar la granada. Tras lanzarla, deberás especificar"
        "en qué direccion mediante W/A/S/D\n"
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

    input("\nPulsa ENTER para volver al menú...")

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

def inicializar_palacio(N: int = N):
    """
    Inicializa el entorno completo del palacio y el estado inicial del agente.
    La función se encarga de mostrar la bienvenida y la pantalla de carga,
    generar de forma aleatoria el mapa del palacio junto con la posición
    de sus elementos clave (soldado, Coronel Kurtz y salida), inicializar
    el estado del Capitán Willard y renderizar el estado inicial del entorno
    por pantalla.
    
    Args:
        - N (int): Tamaño del palacio (N x N). Por defecto, se utiliza el
          valor global definido para el tamaño del entorno.
    
    Returns:
        - console (Console): Objeto de consola de Rich utilizado para la
                             visualización del entorno y los mensajes del juego.
        - mundo (dict): Diccionario que representa el estado objetivo del
                        mundo, incluyendo el mapa del palacio, las posiciones del soldado,
                        del Coronel Kurtz, de la salida y el tamaño del entorno.
        - estado_0 (dict): Diccionario que representa el estado inicial del
                           agente, incluyendo su posición, si ha encontrado al Coronel Kurtz,
                           si el soldado sigue vivo, la disponibilidad de la granada y si la
                           última acción fue la eliminación del soldado.
    """

    console = Console()
    pantalla_carga(console)

    # Ideal: que esto devuelva un world dict/dataclass
    palacio, pos_soldado, pos_kurtz, pos_salida = entorno.crear_entorno(N)

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

    return console, mundo, estado_0

def pantalla_game_over(console, texto: str, color: str):
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

def menu_post_partida(console) -> str:
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

def funcion_transicion(estado: dict, mundo: dict, accion: str):
    palacio = mundo["palacio"]
    N = mundo["N"]
    pos_soldado = mundo["pos_soldado"]
    pos_kurtz = mundo["pos_kurtz"]
    pos_salida = mundo["pos_salida"]
    palacio = mundo["palacio"]


    nuevo = dict(estado)

    # por defecto, no hay grito este turno
    nuevo["ultima_accion_matar_soldado"] = False

    # ---------------- EXIT ----------------
    if accion == "EXIT":
        if nuevo["agent_pos"] != mundo["pos_salida"]:
            return nuevo, {"invalid_exit": True, "message": "No estás en la salida."}

        if not nuevo["has_kurtz"]:
            # Está en salida pero sin Kurtz: NO gana
            return nuevo, {"win": False, "message": "No puedes ganar sin Kurtz. Debes encontrarlo primero."}

        return nuevo, {"win": True, "message": "El Coronel Kurtz y tú habéis salido del palacio juntos."}


    # ---------------- GRENADE ----------------
    if accion.startswith("GRENADE_"):
        if not nuevo["granada"]:
            return nuevo, {"message": "Ya no tienes granada."}

        # La granada se consume SIEMPRE al lanzarla
        nuevo["granada"] = False

        dir_ = accion.replace("GRENADE_", "")
        di, dj = {"UP": (-1,0), "DOWN": (1,0), "LEFT": (0,-1), "RIGHT": (0,1)}[dir_]

        i, j = nuevo["agent_pos"]
        target = (i + di, j + dj)

        # Si tiras fuera del tablero: fallo y ya está (pero gastada)
        if not (0 <= target[0] < N and 0 <= target[1] < N):
            return nuevo, {"grenade": True, "hit_wall": True, "message": "La granada golpea la pared y se desperdicia."}

        # Efecto contra soldado SOLO si está en la celda objetivo y está vivo
        if nuevo["soldado_vivo"] and target == pos_soldado:
            nuevo["soldado_vivo"] = False
            nuevo["ultima_accion_matar_soldado"] = True
            return nuevo, {"killed_soldier": True, "message": "¡Soldado eliminado! Oyes un grito."}
        
        # Si por error cae en Kurtz, no pasa nada
        if target == pos_kurtz:
            return nuevo, {"grenade": True, "message": "Kurtz se cubre a tiempo. No sufre daño."}

        # Si cae en cualquier otra casilla, no pasa nada
        return nuevo, {"grenade": True, "message": "La granada explota sin efecto."}

    # ---------------- MOVE ----------------
    i, j = nuevo["agent_pos"]
    di, dj = {"UP": (-1,0), "DOWN": (1,0), "LEFT": (0,-1), "RIGHT": (0,1)}[accion]
    ni, nj = i + di, j + dj

    if not (0 <= ni < N and 0 <= nj < N):
        return nuevo, {"hit_wall": True, "message": "Te chocas con una pared."}

    nuevo["agent_pos"] = (ni, nj)

        # recoger a Kurtz si llegas a su casilla
    if (not nuevo["has_kurtz"]) and (nuevo["agent_pos"] == pos_kurtz):
        nuevo["has_kurtz"] = True
        return nuevo, {"moved": True, "picked_kurtz": True, "message": "Has encontrado a Kurtz. Ahora vais juntos."}


    # muere por precipicio
    if palacio[ni, nj] == "P":
        return nuevo, {"dead": True, "cause": "P"}

    # muere por soldado vivo
    if nuevo["soldado_vivo"] and (nuevo["agent_pos"] == pos_soldado):
        return nuevo, {"dead": True, "cause": "S"}


    return nuevo, {"moved": True}

def escoger_accion(estado: dict, kb: KnowledgeBase) -> str:
    """
    El usuario elige la acción, pero SOLO se permiten movimientos hacia celdas seguras
    (certeza KB) o celdas ya visitadas.
    """
    mapa_mov = {"W": "UP", "S": "DOWN", "A": "LEFT", "D": "RIGHT"}
    delta = {"UP": (-1,0), "DOWN": (1,0), "LEFT": (0,-1), "RIGHT": (0,1)}

    pos = estado["agent_pos"]
    vecinos = kb.neighbors(pos)

    # Conjunto de movimientos permitidos: visitadas o seguras por KB
    seguras = {v for v in vecinos if kb.is_safe(v)}
    visitadas = kb.visited

    aconsejadas = seguras | (set(vecinos) & visitadas)

    # Mapa: tecla -> destino
    tecla_a_destino = {}
    for k, mov in mapa_mov.items():
        di, dj = delta[mov]
        dest = (pos[0] + di, pos[1] + dj)
        if dest in vecinos:  # está dentro del tablero
            tecla_a_destino[k] = dest

    teclas_mov_ok = list(tecla_a_destino.keys())

    print("\nAcciones: W/A/S/D mover | E salir | G granada")
    print(f"Habitaciones seguras: {sorted(seguras)}")

    # Si no hay movimientos permitidos, lo digo claro (esto puede pasar)
    if not teclas_mov_ok:
        print("[AVISO] La KB no puede demostrar ningún movimiento seguro ahora mismo.")
        print("Solo puedes usar granada (G) o salir (E si estás en la salida).")

    while True:
        t = input("Acción: ").strip().upper()

        # mover (solo si está permitido)
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
                return "GRENADE_" + mapa_mov[dir_key]
            print("Dirección inválida.")
            continue

        print("Entrada inválida.")

def percept(estado: dict, kb: KnowledgeBase, mundo: dict):
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
    vecinos = kb.neighbors(pos)

    brisa = any(palacio[v] == "P" for v in vecinos)
    ronquido = estado["soldado_vivo"] and any(v == pos_soldado for v in vecinos)
    resplandor = (pos == pos_salida) or (pos_salida in vecinos)

    pared_arriba, pared_abajo, pared_izq, pared_der = comprobar_paredes(pos, mundo["N"])

    grito = estado["ultima_accion_matar_soldado"]

    perceptos = [brisa, ronquido, resplandor, pared_arriba, pared_abajo, pared_izq, pared_der, grito]

    return perceptos

def comprobar_paredes(pos, N):
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

def main():
    console = Console()
    game_mode = bienvenida(console)

    while True:

        if game_mode == "1":
            instrucciones(console)
            game_mode = bienvenida(console)
            continue

        elif game_mode == "2":
            console, mundo, estado = inicializar_palacio()

            N = mundo["palacio"].shape[0]
            kb = KnowledgeBase(N)

            fin = None  # "dead" | "win"

            while True:
                perceptos = percept(estado, kb, mundo)
                kb.add_percept(estado["agent_pos"], perceptos)

                pos = estado["agent_pos"]
                vecinos = kb.neighbors(pos)
                seguras = {v for v in vecinos if kb.is_safe(v)}
                possible_pits, possible_soldier = kb.possible_pits_and_soldier()
                exit_pos = kb.known_exit()

                console.clear()
                entorno.render(
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

                accion = escoger_accion(estado, kb)
                estado, info = funcion_transicion(estado, mundo, accion)

                if info.get("message"):
                    console.print(f"[bold]{info['message']}[/bold]")

                if info.get("dead"):
                    fin = "dead"
                    break

                if info.get("win"):
                    fin = "win"
                    break

            # ---- AQUÍ está la UX que te faltaba ----
            if fin == "dead":
                pantalla_game_over(console, "HAS MUERTO", "red")
            elif fin == "win":
                pantalla_game_over(console, "VICTORIA", "green")

            time.sleep(1.5)
            opcion = menu_post_partida(console)

            if opcion == "1":
                continue              # reintentar (vuelve a inicializar_palacio)
            if opcion == "2":
                game_mode = bienvenida(console)  # menú principal
                continue
            if opcion == "3":
                return 
            
        elif game_mode == "4":
            return



if __name__ == "__main__":
    main()



