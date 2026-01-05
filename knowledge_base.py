from itertools import combinations

class KnowledgeBase:
    """
    Base de conocimiento para deducción lógica del palacio.
    Mantiene perceptos observados y genera mundos compatibles para inferir seguridad
    de celdas y deducir la salida usando el resplandor.
    """

    def __init__(self, N: int):
        """
        Inicializa la base de conocimiento para un palacio de tamaño N x N.

        Args:
            - N (int): tamaño del tablero (N x N).
        """
        self.N = N
        self.visited: set[tuple[int, int]] = set()
        self.obs: dict[tuple[int, int], tuple[bool, bool, bool]] = {}
        self.soldier_dead = False

    def add_percept(self, pos, perceptos):
        """
        Registra el percepto observado en una posición y actualiza la KB.

        Args:
            - pos (tuple[int, int]): posición donde se observa el percepto.
            - perceptos (list[bool]): lista de perceptos con el orden esperado:
              [brisa, ronquido, resplandor, ..., grito].
        """
        brisa, ronquido, resplandor, *_resto, grito = perceptos
        self.visited.add(pos)
        self.obs[pos] = (brisa, ronquido, resplandor)
        if grito:
            self.soldier_dead = True

    def neighbours(self, celda: tuple[int, int]):
        """
        Devuelve las celdas vecinas.

        Args:
            - celda (tuple[int, int]): celda de referencia.

        Returns:
            - vecinos (list[tuple[int, int]]): vecinos dentro del tablero.
        """
        i, j = celda
        candidatos = [(i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)]
        return [(x, y) for x, y in candidatos if 0 <= x < self.N and 0 <= y < self.N]

    def compatible_worlds(self):
        """
        Genera mundos compatibles con las observaciones acumuladas.
        Un mundo se representa como (precipicios, soldado), donde:
        - precipicios es un conjunto de exactamente 3 celdas.
        - soldado es una celda o None si el soldado ya está muerto.

        Returns:
            - worlds (generator): generador de tuplas (precipicios, pos_soldado).
        """
        celdas = [(i, j) for i in range(self.N) for j in range(self.N)]

        # 1) Candidatos iniciales (no visitados)
        candidatos_precipicio = [c for c in celdas if c not in self.visited]
        candidatos_soldado = [c for c in celdas if c not in self.visited]

        # 2) Filtrado de brisa y ronquido
        prohibidos_precipicio = set()
        prohibidos_soldado = set()
        fronteras_requeridas_precipicio = []  # en cada observación con brisa=True, al menos un precipicio aquí
        fronteras_requeridas_soldado = []     # en cada observación con ronquido=True, el soldado debe estar aquí

        for celda, (brisa, ronquido, _resplandor) in self.obs.items():
            vecinos = set(self.neighbours(celda))

            if not brisa:
                prohibidos_precipicio |= vecinos
            else:
                fronteras_requeridas_precipicio.append(vecinos)

            if not self.soldier_dead:
                if not ronquido:
                    prohibidos_soldado |= vecinos
                else:
                    fronteras_requeridas_soldado.append(vecinos)

        candidatos_precipicio = [c for c in candidatos_precipicio if c not in prohibidos_precipicio]
        candidatos_soldado = [c for c in candidatos_soldado if c not in prohibidos_soldado]

        # 3) Enumeración de precipicios
        for precipicios in combinations(candidatos_precipicio, 3):
            precipicios = set(precipicios)

            valido = True
            for frontera in fronteras_requeridas_precipicio:
                if precipicios.isdisjoint(frontera):
                    valido = False
                    break
            if not valido:
                continue

            # 4) Enumeración del soldado si vive
            if self.soldier_dead:
                yield (precipicios, None)
            else:
                for pos_soldado in candidatos_soldado:
                    if pos_soldado in precipicios:
                        continue

                    valido_soldado = True
                    for frontera in fronteras_requeridas_soldado:
                        if pos_soldado not in frontera:
                            valido_soldado = False
                            break

                    if valido_soldado:
                        yield (precipicios, pos_soldado)

    def entails_no_pit(self, celda):
        """
        Determina si la KB implica que una celda no contiene precipicio.
        Devuelve True solo si existen mundos compatibles y en todos ellos la celda no es precipicio.

        Args:
            - celda (tuple[int, int]): celda a evaluar.

        Returns:
            - no_precipicio (bool): True si en todos los mundos compatibles la celda no es precipicio.
        """
        hay_modelo = False
        for precipicios, _pos_soldado in self.compatible_worlds():
            hay_modelo = True
            if celda in precipicios:
                return False
        return hay_modelo

    def entails_no_soldier(self, celda):
        """
        Determina si la KB implica que una celda no contiene al soldado.
        Si el soldado ya está muerto, devuelve True.

        Args:
            - celda (tuple[int, int]): celda a evaluar.

        Returns:
            - no_soldado (bool): True si el soldado no puede estar en esa celda.
        """
        if self.soldier_dead:
            return True

        hay_modelo = False
        for _precipicios, pos_soldado in self.compatible_worlds():
            hay_modelo = True
            if pos_soldado == celda:
                return False
        return hay_modelo

    def is_safe(self, celda: tuple[int, int]):
        """
        Determina si una celda es segura según la KB (sin precipicio y sin soldado).

        Args:
            - celda (tuple[int, int]): celda a evaluar.

        Returns:
            - segura (bool): True si la KB implica que la celda es segura.
        """
        return self.entails_no_pit(celda) and self.entails_no_soldier(celda)

    def possible_pits_and_soldier(self):
        """
        Calcula las celdas que podrían contener precipicio y las que podrían contener al soldado
        según todos los mundos compatibles.

        Returns:
            - posibles_precipicios (set[tuple[int, int]]): celdas que son pit en algún mundo consistente.
            - posibles_soldado (set[tuple[int, int]]): celdas donde el soldado aparece en algún mundo consistente.
        """
        posibles_precipicios = set()
        posibles_soldado = set()

        for precipicios, pos_soldado in self.compatible_worlds():
            posibles_precipicios |= precipicios
            if pos_soldado is not None:
                posibles_soldado.add(pos_soldado)

        return posibles_precipicios, posibles_soldado

    def _neigh_plus_self(self, pos):
        """
        Devuelve el conjunto formado por la celda y sus vecinos adyacentes.

        Args:
            - pos (tuple[int, int]): celda de referencia.

        Returns:
            - zona (set[tuple[int, int]]): {pos} | vecinos(pos).
        """
        return {pos} | set(self.neighbours(pos))

    def exit_candidates(self):
        """
        Obtiene las celdas candidatas a ser la salida usando SOLO el resplandor.

        Returns:
            - candidatas (set[tuple[int, int]]): celdas compatibles con todas las observaciones de resplandor.
        """
        todas = {(i, j) for i in range(self.N) for j in range(self.N)}
        candidatas = set(todas)

        for pos, (_b, _r, resplandor) in self.obs.items():
            zona = self._neigh_plus_self(pos)
            if resplandor:
                candidatas &= zona
            else:
                candidatas -= zona

        return candidatas

    def possible_exits(self):
        """
        Calcula las posibles celdas de salida considerando:
        - restricciones por resplandor
        - la salida no puede coincidir con precipicios ni con el soldado (si vive).

        Returns:
            - posibles (set[tuple[int, int]]): celdas que podrían ser salida en algún mundo consistente.
        """
        candidatas_resplandor = self.exit_candidates()
        posibles = set()

        for precipicios, pos_soldado in self.compatible_worlds():
            salidas = set(candidatas_resplandor) - set(precipicios)
            if pos_soldado is not None:
                salidas.discard(pos_soldado)

            if salidas:
                posibles |= salidas

        return posibles

    def entails_exit(self, celda):
        """
        Determina si la KB implica que la salida está exactamente en la celda indicada.
        La salida queda deducida si, para todos los mundos compatibles, el conjunto de
        salidas posibles siempre incluye 'celda' y la intersección de todas esas salidas
        es únicamente {celda}.

        Args:
            - celda (tuple[int, int]): celda candidata a ser la salida.

        Returns:
            - implicada (bool): True si la salida queda deducida con certeza en 'celda'.
        """

        candidatas_resplandor = set(self.exit_candidates())

        interseccion = None
        hay_modelo = False

        for precipicios, pos_soldado in self.compatible_worlds():
            salidas = set(candidatas_resplandor) - set(precipicios)
            if pos_soldado is not None:
                salidas.discard(pos_soldado)

            if not salidas:
                continue

            hay_modelo = True

            if interseccion is None:
                interseccion = set(salidas)
            else:
                interseccion &= salidas

            if celda not in interseccion:
                return False

        return hay_modelo and interseccion == {celda}


    def known_exit(self):
        """
        Devuelve la salida si está deducida con certeza lógica.
        Returns:
            - salida (tuple[int, int] | None): celda de la salida si ha sido
                deducida con certeza, None en caso contrario.
        """
        for c in self.exit_candidates():
            if self.entails_exit(c):
                return c
        return None
