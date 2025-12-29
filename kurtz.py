import entorno
from knowledge_base import KnowledgeBase
from rich.panel import Panel
from rich.align import Align
from rich.console import Console
from rich.text import Text 
import time

N = 6

def bienvenida(console: Console):
    """
    Función de bienvenida. Proporciona instrucciones al usuario 
    haciendo uso de la librería Rich 
        Args: 
        - console (Console): objeto de consola de Rich utilizado para la
                             visualización de los distintos paneles y elementos.
    """

    console.clear()
    titulo = Align.center("[bold cyan]BUSCANDO AL CORONEL KURTZ[/bold cyan]")
    console.print(Panel(titulo, border_style="cyan"))

    console.print("\n[bold]Instrucciones rápidas[/bold]")
    console.print("• Te mueves por el palacio mediante W/A/S/D, buscando a [bold magenta]CK[/bold magenta] (Coronel Kurtz).")
    console.print("• Evita [bold yellow]P[/bold yellow] (precipicios) y [bold red]S[/bold red] (soldado enemigo).")
    console.print("• Encuentra la [bold green]E[/bold green] (salida) tras localizar a Kurtz.\n")

    input("Pulsa ENTER para comenzar...")


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
    bienvenida(console)
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

    permitidas = seguras | (set(vecinos) & visitadas)

    # Mapa: tecla -> destino
    tecla_a_destino = {}
    for k, mov in mapa_mov.items():
        di, dj = delta[mov]
        dest = (pos[0] + di, pos[1] + dj)
        if dest in vecinos:  # está dentro del tablero
            tecla_a_destino[k] = dest

    teclas_mov_ok = [k for k, dest in tecla_a_destino.items() if dest in permitidas]

    print("\nAcciones: W/A/S/D mover (solo seguras) | E salir | G granada")
    print(f"Posición: {pos}")
    print(f"Vecinos: {vecinos}")
    print(f"Seguras (KB): {sorted(seguras)}")
    print(f"Movimientos permitidos: {[ (k, tecla_a_destino[k]) for k in teclas_mov_ok ]}")

    # Si no hay movimientos permitidos, lo digo claro (esto puede pasar)
    if not teclas_mov_ok:
        print("[AVISO] La KB no puede demostrar ningún movimiento seguro ahora mismo.")
        print("Solo puedes usar granada (G) o salir (E si estás en la salida).")

    while True:
        t = input("Acción: ").strip().upper()

        # mover (solo si está permitido)
        if t in mapa_mov:
            if t not in teclas_mov_ok:
                print("Movimiento NO permitido: la KB no lo considera seguro (o no está visitado).")
                continue
            return mapa_mov[t]

        # salir (sin filtro de seguridad)
        if t == "E":
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


def render_estado(console, mundo, estado, perceptos, mensaje=None):
    """
    Renderiza el estado actual del juego y los perceptos del agente.
    Limpia la consola, dibuja el mapa del palacio con la posición
    actual del Capitán Willard, muestra un panel con los perceptos percibidos
    en el estado actual e informa sobre el estado relevante del agente
    (disponibilidad de granada y estado del soldado enemigo).
    
    Args:
        - console (Console)
        - mundo (dict)
        - estado (dict)
        - perceptos (list[bool])
        - mensaje (str, optional): Mensaje informativo del turno a mostrar
          por pantalla. Por defecto es None.
    """

    console.clear()

    # Dibuja el tablero con tu render
    entorno.render(console, mundo["palacio"], mundo["pos_salida"], estado["agent_pos"], estado["has_kurtz"])

    # Panel de perceptos
    nombres = ["Brisa","Ronquido","Resplandor","Pared↑","Pared↓","Pared←","Pared→","Grito"]
    t = Text()
    for n, v in zip(nombres, perceptos):
        t.append(f"{n}: {'Sí' if v else 'No'}\n")

    console.print(Panel(t, title="Perceptos", border_style="cyan"))

    # Estado útil
    console.print(
        f"[bold]Granada:[/bold] {'Sí' if estado['granada'] else 'No'}   "
        f"[bold]Soldado vivo:[/bold] {'Sí' if estado['soldado_vivo'] else 'No'}"
    )

    # Mensaje del turno (si existe)
    if mensaje:
        console.print(Panel(mensaje, border_style="yellow"))

from rich.console import Console

# asumo:
# - from knowledge_base import KnowledgeBase
# - from entorno import render_conocimiento
# - inicializar_palacio(), percept(), funcion_transicion()

def main():
    console = Console()

    console, mundo, estado = inicializar_palacio()

    N = mundo["palacio"].shape[0]  # 6
    kb= KnowledgeBase(N)

    # bucle principal
    while True:
        # 1) perceptos del mundo real (SOLO aquí se usa mundo real)
        perceptos = percept(estado, kb, mundo)

        # 2) actualizar KB (razonamiento parte de aquí)
        kb.add_percept(estado["agent_pos"], perceptos)

        # 3) deducciones para UI y recomendaciones
        pos = estado["agent_pos"]
        vecinos = kb.neighbors(pos)

        seguras = {v for v in vecinos if kb.is_safe(v)}
        possible_pits, possible_soldier = kb.possible_pits_and_soldier()

        # 4) render LEGAL (sin revelar P/S/CK reales)
        entorno.render(
            console=console,
            N=N,
            pos_agente=pos,
            has_kurtz=estado.get("has_kurtz", False),
            visited=kb.visited,
            safe=seguras,
            possible_pits=possible_pits,
            possible_soldier=possible_soldier,
            show_exit_if_known=False,
            exit_pos=None,
        )

        # 5) elegir acción: tú mandas, KB aconseja
        accion = escoger_accion(estado, kb)

        # 6) transición del mundo real
        estado, info = funcion_transicion(estado, mundo, accion)

        # 7) mensajes post-acción (opcionales)
        if info.get("message"):
            console.print(f"[bold]{info['message']}[/bold]")

        if info.get("dead"):
            console.print("[bold red]Has muerto.[/bold red]")
            break

        if info.get("win"):
            console.print("[bold green]Has ganado.[/bold green]")
            break




if __name__ == "__main__":
    main()



