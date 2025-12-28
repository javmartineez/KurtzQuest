import numpy as np 
from rich.table import Table
from rich.console import Console
from rich.text import Text

def crear_entorno(N:int = 6):
    """
    Función encargada de crear la matriz Numpy que servirá 
    como tablero de juego. 

    Args: 
        - N(int): valor de dimensiones del tablero establecido 
                a 6x6 como valor predeterminado. 

    Returns: 
        - palacio(np.array): matriz-tablero con los distintos elementos 
                             calculados e incluidos en sus posiciones
                             correspondientes.
    """

    NUM_TRAMPAS = 3
    NUM_SOLDADOS = 1

    palacio = np.full((N,N), None, dtype=object)                                              

    indices_posibles = np.arange(1, N * N)                                                              # del 1 al 35 - el (0,0) siempre debe ser la casilla inicial
    indices = np.random.choice(indices_posibles, 
                               size=NUM_TRAMPAS + NUM_SOLDADOS + 2, 
                               replace=False)    #Escogemos posiciones aleatorias para las trampas (asegurando que no estén en la misma casilla y que el (0,0) no sea una de ellas)
    posiciones_random = [(i // N, i % N) for i in indices]   
    
    pos_soldado = posiciones_random[0]  
    pos_kurtz = posiciones_random[1]
    pos_salida = posiciones_random[2]
    
    palacio[0,0] = "CW"
    palacio[pos_kurtz] = "CK"  
    palacio[pos_soldado] = "S"          

    for p in posiciones_random[3:]:
        palacio[p] = "P"

    return palacio, pos_soldado, pos_kurtz, pos_salida


def render(palacio, pos_salida):
    console = Console()
    table = Table(show_header=False, box=None)

    N = palacio.shape[0]
    for _ in range(N):
        table.add_column(justify="center", width=4)

    for i in range(N):
        row = []
        for j in range(N):

            # CASILLA INICIAL (0,0): CW en naranja
            if (i, j) == (0, 0):
                cell = Text("CW", style="bold orange1")

            # CASILLA SALIDA: punto verde
            elif (i, j) == pos_salida:
                cell = Text("·", style="bold green")

            # RESTO DE CASILLAS
            else:
                v = palacio[i, j]
                if v is None:
                    cell = Text("·", style="dim")
                else:
                    cell = Text(str(v))

            row.append(cell)

        table.add_row(*row)

    console.print(table)

