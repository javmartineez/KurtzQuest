import random 
import numpy as np 
import entorno
from rich.panel import Panel
from rich.align import Align
from rich.console import Console
import time


N = 6

def bienvenida(console:Console):
    console.clear()

    titulo = Align.center("[bold cyan]BUSCANDO AL CORONEL KURTZ[/bold cyan]")
    console.print(Panel(titulo, border_style="cyan"))

    console.print("\n[bold]Instrucciones rápidas[/bold]")
    console.print("• Te mueves por el palacio buscando a [bold magenta]CK[/bold magenta] (Coronel Kurtz).")
    console.print("• Evita [bold yellow]P[/bold yellow] (precipicios) y [bold red]S[/bold red] (soldado enemigo).")
    console.print("• Encuentra la [bold green]E[/bold green] (salida) tras localizar a Kurtz.\n")

    input("Pulsa ENTER para comenzar...")

def pantalla_carga(console:Console, segundos:float = 1):
    console.clear()
    with console.status("[bold]Preparando el palacio...[/bold]", spinner="dots"):
        time.sleep(segundos)

def inicializar_palacio(N:int = 6):
    console = Console()

    bienvenida(console)
    pantalla_carga(console)

    palacio, pos_salida = entorno.crear_entorno(N)
    entorno.render(palacio, pos_salida)

def seleccionar_accion(palacio):

    #1. Comprobamos percepciones para generar lista percepts(s)
    pass


if __name__ == "__main__":
    inicializar_palacio()
