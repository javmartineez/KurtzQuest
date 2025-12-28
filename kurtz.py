import entorno
from rich.panel import Panel
from rich.align import Align
from rich.console import Console
import time

N = 6

def bienvenida(console: Console):
    console.clear()
    titulo = Align.center("[bold cyan]BUSCANDO AL CORONEL KURTZ[/bold cyan]")
    console.print(Panel(titulo, border_style="cyan"))

    console.print("\n[bold]Instrucciones rápidas[/bold]")
    console.print("• Te mueves por el palacio buscando a [bold magenta]CK[/bold magenta] (Coronel Kurtz).")
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

    # Ideal: pasar console a render
    entorno.render(palacio, pos_salida)

    estado_0 = {
        "agent_pos": (0, 0),
        "kurtz": False,
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


def funcion_transicion(estado, accion):
    pass


def percept(estado: dict, mundo: dict):

    palacio = mundo["palacio"]
    pos_salida = mundo["pos_salida"]

    pos = estado["agent_pos"]
    vecinos = calcular_adyacentes(pos, N)

    brisa = any(palacio[v] == "P" for v in vecinos)
    ronquido = estado["soldado_vivo"] and any(palacio[v] == "S" for v in vecinos)
    resplandor = (pos == pos_salida) or (pos_salida in vecinos)

    pared_arriba, pared_abajo, pared_izq, pared_der = comprobar_paredes(pos, N)

    perceptos = [brisa, ronquido, resplandor, pared_arriba, pared_abajo, pared_izq, pared_der]

    return perceptos


def calcular_adyacentes(pos, N):
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


    




if __name__ == "__main__":
    console, mundo, estado = inicializar_palacio()
    perceptos = percept(estado, mundo)
    print(perceptos)
    
