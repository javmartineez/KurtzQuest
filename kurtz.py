import entorno
from rich.panel import Panel
from rich.align import Align
from rich.console import Console
from rich.text import Text 
import time

N = 6

def bienvenida(console: Console):
    console.clear()
    titulo = Align.center("[bold cyan]BUSCANDO AL CORONEL KURTZ[/bold cyan]")
    console.print(Panel(titulo, border_style="cyan"))

    console.print("\n[bold]Instrucciones rápidas[/bold]")
    console.print("• Te mueves por el palacio mediante W/A/S/D, buscando a [bold magenta]CK[/bold magenta] (Coronel Kurtz).")
    console.print("• Evita [bold yellow]P[/bold yellow] (precipicios) y [bold red]S[/bold red] (soldado enemigo).")
    console.print("• Encuentra la [bold green]E[/bold green] (salida) tras localizar a Kurtz.\n")

    input("Pulsa ENTER para comenzar...")

def pantalla_carga(console: Console, segundos: float = 1.0):
    console.clear()
    with console.status("[bold]Preparando el palacio...[/bold]", spinner="dots"):
        time.sleep(segundos)

def inicializar_palacio(N: int = N):
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

    # Ideal: pasar console a render
    entorno.render(console, palacio, pos_salida, estado_0["agent_pos"], estado_0["has_kurtz"])

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
            palacio[pos_soldado] = None 
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
        palacio[pos_kurtz] = None
        return nuevo, {"moved": True, "picked_kurtz": True, "message": "Has encontrado a Kurtz. Ahora vais juntos."}


    # muere por precipicio
    if palacio[ni, nj] == "P":
        return nuevo, {"dead": True, "cause": "P"}

    # muere por soldado vivo
    if nuevo["soldado_vivo"] and palacio[ni, nj] == "S":
        return nuevo, {"dead": True, "cause": "S"}

    return nuevo, {"moved": True}

def escoger_accion(estado: dict, mundo: dict, perceptos: list[bool]) -> str:
    mapa_mov = {"W": "UP", "S": "DOWN", "A": "LEFT", "D": "RIGHT"}

    # puedes seguir mostrando opciones recomendadas, pero NO bloquees
    print("\nAcciones: W/A/S/D mover | E salir | G granada")

    while True:
        t = input("Acción: ").strip().upper()

        # mover
        if t in mapa_mov:
            return mapa_mov[t]

        # salir
        if t == "E":
            return "EXIT"

        # granada
        if t == "G":
            dir_key = input("Dirección granada (W/A/S/D): ").strip().upper()
            if dir_key in mapa_mov:
                return "GRENADE_" + mapa_mov[dir_key]

            print("Dirección inválida.")
            continue

        print("Entrada inválida.")

def percept(estado: dict, mundo: dict):

    palacio = mundo["palacio"]
    pos_salida = mundo["pos_salida"]

    pos = estado["agent_pos"]
    vecinos = calcular_vecinos(pos, mundo["N"])

    brisa = any(palacio[v] == "P" for v in vecinos)
    ronquido = estado["soldado_vivo"] and any(palacio[v] == "S" for v in vecinos)
    resplandor = (pos == pos_salida) or (pos_salida in vecinos)

    pared_arriba, pared_abajo, pared_izq, pared_der = comprobar_paredes(pos, mundo["N"])

    grito = estado["ultima_accion_matar_soldado"]

    perceptos = [brisa, ronquido, resplandor, pared_arriba, pared_abajo, pared_izq, pared_der, grito]

    return perceptos

def calcular_vecinos(pos, N):
    i, j = pos
    candidatos = [(i-1, j), (i+1, j), (i, j-1), (i, j+1)]
    return [(ni, nj) for ni, nj in candidatos if 0 <= ni < N and 0 <= nj < N]

def comprobar_paredes(pos, N):
    i, j = pos

    pared_arriba = (i == 0)
    pared_abajo = (i == N - 1)
    pared_izq = (j == 0)
    pared_der = (j == N - 1)

    return pared_arriba, pared_abajo, pared_izq, pared_der

def render_estado(console, mundo, estado, perceptos, mensaje=None):
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

def main():
    console = Console()

    console, mundo, estado = inicializar_palacio()
    perceptos = percept(estado, mundo)

    while True:
        perceptos = percept(estado, mundo)
        render_estado(console, mundo, estado, perceptos)

        accion = escoger_accion(estado, mundo, perceptos)  # W/A/S/D, G+dir, E
        estado, info = funcion_transicion(estado, mundo, accion)

        if info.get("message"):
            render_estado(console, mundo, estado, perceptos, mensaje=info["message"])

        if info.get("dead"):
            console.print("[bold red]Has muerto.[/bold red]")
            break

        if info.get("win"):
            console.print("[bold green]Has ganado.[/bold green]")
            break



if __name__ == "__main__":
    main()



