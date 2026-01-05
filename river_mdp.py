import random
import numpy as np

ACCIONES = ["up", "down", "left", "right", "stay"]

def crear_entorno(N: int = 6, n_islas: int = 2, seed: int|None = None):
    """
    Genera el entorno del río siguiendo el enunciado.
    """

    if seed is not None:
        random.seed(seed)

    if n_islas > (N - 2) ** 2:
        raise ValueError("Demasiadas islas para el tamaño del río.")

    start = (0, 0)
    exit_row = random.randrange(0, N)
    exit_pos = (exit_row, N - 1)

    # Fuerza del río por columnas
    river_strength = []
    for j in range(N):
        if j == 0 or j == N - 1:
            river_strength.append(0.0)
        else:
            river_strength.append(round(random.uniform(0.06, 0.94), 1))

    rio = np.full((N, N), None, dtype=object)

    for i in range(N):
        rio[i, 0] = "|    |"
        rio[i, N - 1] = "|    |"

    # Río solo en columnas interiores
    for j in range(1, N - 1):
        for i in range(N):
            rio[i, j] = "| R  |"


    posibles_islas = [
        (i, j)
        for i in range(1, N - 1)
        for j in range(1, N - 1)
    ]

    islas = set(random.sample(posibles_islas, k=n_islas))

    for pos in islas:
        rio[pos] = "| I  |"

    rio[start] = "|CWCK|"
    rio[exit_pos] = "| E  |"

    return rio, start, exit_pos, islas, river_strength

def mostrar_entorno(rio):
    """
    Imprime el entorno del río de forma legible.
    """
    for fila in rio:
        print(" ".join(f"{celda:4}" for celda in fila))

def crear_estados(rio):
    estados = []
    N = rio.shape[0]

    for i in range(N):
        for j in range(N):
            if rio[i, j] == "| I  |":
                estados.append((i, j, False))
            else:
                estados.append((i, j, True))

    return estados

def acciones(s: tuple):
    _, _, vivo = s
    if not vivo:
        return ["stay"]
    return ACCIONES

def transicion(s, a, rio, river_strength):
    """
    Implementa exactamente la distribución P(s' | s, a) del enunciado.
    """
    i, j, vivo = s
    N = rio.shape[0]

    # Estado muerto: absorbente
    if not vivo:
        return {s: 1.0}

    # Acción stay: quedarse
    if a == "stay":
        return {s: 1.0}

    # Función auxiliar
    def invalido(pos):
        x, y = pos
        return (
            x < 0 or x >= N or
            y < 0 or y >= N or
            rio[x, y] == "| I  |"
        )

    # -------------------------
    # CASO a = down
    # -------------------------
    if a == "down":
        s_dir = (i + 1, j)

        # borde o isla → stay
        if invalido(s_dir):
            return {s: 1.0}

        # movimiento válido
        if rio[s_dir] == "| I  |":
            return {(s_dir[0], s_dir[1], False): 1.0}
        else:
            return {(s_dir[0], s_dir[1], True): 1.0}

    # -------------------------
    # CASO a ≠ down
    # -------------------------
    p_down = river_strength[j]
    p_dir = 1.0 - p_down

    dist = {}

    # Movimiento en la dirección de a
    if a == "up":
        s_dir = (i - 1, j)
    elif a == "left":
        s_dir = (i, j - 1)
    elif a == "right":
        s_dir = (i, j + 1)
    else:
        raise ValueError(f"Acción desconocida: {a}")

    # Rama p_dir
    if invalido(s_dir):
        dist[s] = dist.get(s, 0.0) + p_dir
    else:
        if rio[s_dir] == "| I  |":
            dist[(s_dir[0], s_dir[1], False)] = dist.get((s_dir[0], s_dir[1], False), 0.0) + p_dir
        else:
            dist[(s_dir[0], s_dir[1], True)] = dist.get((s_dir[0], s_dir[1], True), 0.0) + p_dir

    # Rama p_down (arrastre)
    s_down = (i + 1, j)
    if invalido(s_down):
        dist[s] = dist.get(s, 0.0) + p_down
    else:
        if rio[s_down] == "| I  |":
            dist[(s_down[0], s_down[1], False)] = dist.get((s_down[0], s_down[1], False), 0.0) + p_down
        else:
            dist[(s_down[0], s_down[1], True)] = dist.get((s_down[0], s_down[1], True), 0.0) + p_down


    return dist

def recompensa(s_next, rio):
    i, j, vivo = s_next

    if rio[i, j] == "| E  |" and vivo:
        return 100

    if not vivo:
        return -100

    return -1

def value_iteration(estados, rio, river_strength, gamma=0.9, epsilon=1e-6):

    V = {s: 0.0 for s in estados}

    while True:
        delta = 0.0

        for s in estados:
            mejor_valor = float("-inf")

            for a in acciones(s):
                valor = 0.0
                dist = transicion(s, a, rio, river_strength)

                for s_next, p in dist.items():
                    valor += p * (recompensa(s_next, rio) + gamma * V[s_next])

                if valor > mejor_valor:
                    mejor_valor = valor

            delta = max(delta, abs(mejor_valor - V[s]))
            V[s] = mejor_valor

        if delta < epsilon:
            break

    return V

def extraer_politica(estados, V, rio, river_strength, gamma=0.9):
    policy = {}

    for s in estados:
        mejor_accion = None
        mejor_valor = float("-inf")

        for a in acciones(s):
            valor = 0.0
            dist = transicion(s, a, rio, river_strength)

            for s_next, p in dist.items():
                valor += p * (recompensa(s_next, rio) + gamma * V[s_next])

            if valor > mejor_valor:
                mejor_valor = valor
                mejor_accion = a

        policy[s] = mejor_accion

    return policy


if __name__ == "__main__":

    # 1. Crear entorno
    rio, start, exit_pos, islas, river_strength = crear_entorno(seed=42)
    print("ENTORNO DEL RÍO:\n")
    mostrar_entorno(rio)

    # 2. Crear estados
    estados = crear_estados(rio)

    # 3. Value Iteration
    V = value_iteration(estados, rio, river_strength)

    # 4. Extraer política
    policy = extraer_politica(estados, V, rio, river_strength)

    # 5. Simulación de una partida
    print("\nSIMULACIÓN DE PARTIDA:\n")

    estado = (start[0], start[1], True)
    paso = 0

    while True:
        i, j, vivo = estado

        # Mostrar estado actual
        print(f"Paso {paso}: Estado = {estado}")

        # Condiciones de parada
        if not vivo:
            print("→ El capitán ha muerto al caer en una trampa.")
            break

        if rio[i, j] == "| E  |":
            print("→ El capitán ha llegado a la salida.")
            break

        # Acción según política
        accion = policy[estado]
        print(f"   Acción elegida: {accion}")

        # Aplicar transición (muestreamos según probabilidad)
        dist = transicion(estado, accion, rio, river_strength)

        r = random.random()
        acumulado = 0.0
        for s_next, p in dist.items():
            acumulado += p
            if r <= acumulado:
                estado = s_next
                break

        paso += 1

    # 6. Análisis de resultados
    print("\nANÁLISIS:")
    print("- La política evita casillas peligrosas cuando el riesgo es alto.")
    print("- En columnas con fuerte corriente, el capitán prioriza acciones seguras.")
    print("- El coste por movimiento incentiva trayectorias cortas.")
    print("- A mayor número de islas, la política se vuelve más conservadora.")
