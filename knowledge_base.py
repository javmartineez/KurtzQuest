from itertools import combinations

class KnowledgeBase:
    """
    Knowledge base for logical deduction about the palace.
    Keeps the observed percepts and generates compatible worlds to infer the safety
    of cells and deduce the exit using the glow.
    """

    def __init__(self, N: int):
        """
        Initialises the knowledge base for an N x N palace.

        Args:
            - N (int): board size (N x N).
        """
        self.N = N
        self.visited: set[tuple[int, int]] = set()
        self.obs: dict[tuple[int, int], tuple[bool, bool, bool]] = {}
        self.soldier_dead = False

    def add_percept(self, pos, perceptos):
        """
        Records the percept observed at a position and updates the KB.

        Args:
            - pos (tuple[int, int]): position where the percept is observed.
            - perceptos (list[bool]): list of percepts in the expected order:
              [breeze, snore, glow, ..., scream].
        """
        brisa, ronquido, resplandor, *_resto, grito = perceptos
        self.visited.add(pos)
        self.obs[pos] = (brisa, ronquido, resplandor)
        if grito:
            self.soldier_dead = True

    def neighbours(self, celda: tuple[int, int]):
        """
        Returns the neighbouring cells.

        Args:
            - celda (tuple[int, int]): reference cell.

        Returns:
            - vecinos (list[tuple[int, int]]): neighbours within the board.
        """
        i, j = celda
        candidatos = [(i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)]
        return [(x, y) for x, y in candidatos if 0 <= x < self.N and 0 <= y < self.N]

    def compatible_worlds(self):
        """
        Generates the worlds compatible with the accumulated observations.
        A world is represented as (pits, soldier), where:
        - pits is a set of exactly 3 cells.
        - soldier is a cell, or None if the soldier is already dead.

        Returns:
            - worlds (generator): generator of (pits, soldier_pos) tuples.
        """
        celdas = [(i, j) for i in range(self.N) for j in range(self.N)]

        # 1) Initial candidates (not visited)
        candidatos_precipicio = [c for c in celdas if c not in self.visited]
        candidatos_soldado = [c for c in celdas if c not in self.visited]

        # 2) Filtering by breeze and snore
        prohibidos_precipicio = set()
        prohibidos_soldado = set()
        fronteras_requeridas_precipicio = []  # for each observation with breeze=True, at least one pit here
        fronteras_requeridas_soldado = []     # for each observation with snore=True, the soldier must be here

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

        # 3) Enumerating pits
        for precipicios in combinations(candidatos_precipicio, 3):
            precipicios = set(precipicios)

            valido = True
            for frontera in fronteras_requeridas_precipicio:
                if precipicios.isdisjoint(frontera):
                    valido = False
                    break
            if not valido:
                continue

            # 4) Enumerating the soldier if alive
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
        Determines whether the KB entails that a cell contains no pit.
        Returns True only if compatible worlds exist and the cell is not a pit in any of them.

        Args:
            - celda (tuple[int, int]): cell to evaluate.

        Returns:
            - no_precipicio (bool): True if the cell is not a pit in every compatible world.
        """
        hay_modelo = False
        for precipicios, _pos_soldado in self.compatible_worlds():
            hay_modelo = True
            if celda in precipicios:
                return False
        return hay_modelo

    def entails_no_soldier(self, celda):
        """
        Determines whether the KB entails that a cell does not contain the soldier.
        If the soldier is already dead, returns True.

        Args:
            - celda (tuple[int, int]): cell to evaluate.

        Returns:
            - no_soldado (bool): True if the soldier cannot be in that cell.
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
        Determines whether a cell is safe according to the KB (no pit and no soldier).

        Args:
            - celda (tuple[int, int]): cell to evaluate.

        Returns:
            - segura (bool): True if the KB entails that the cell is safe.
        """
        return self.entails_no_pit(celda) and self.entails_no_soldier(celda)

    def possible_pits_and_soldier(self):
        """
        Computes the cells that could contain a pit and those that could contain the soldier
        across all compatible worlds.

        Returns:
            - posibles_precipicios (set[tuple[int, int]]): cells that are a pit in some consistent world.
            - posibles_soldado (set[tuple[int, int]]): cells where the soldier appears in some consistent world.
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
        Returns the set made up of the cell and its adjacent neighbours.

        Args:
            - pos (tuple[int, int]): reference cell.

        Returns:
            - zona (set[tuple[int, int]]): {pos} | neighbours(pos).
        """
        return {pos} | set(self.neighbours(pos))

    def exit_candidates(self):
        """
        Gets the candidate exit cells using ONLY the glow.

        Returns:
            - candidatas (set[tuple[int, int]]): cells compatible with every glow observation.
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
        Computes the possible exit cells taking into account:
        - the glow constraints
        - the exit cannot coincide with pits or with the soldier (if alive).

        Returns:
            - posibles (set[tuple[int, int]]): cells that could be the exit in some consistent world.
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
        Determines whether the KB entails that the exit is exactly at the given cell.
        The exit is deduced if, for every compatible world, the set of possible
        exits always includes 'celda' and the intersection of all those exits
        is exactly {celda}.

        Args:
            - celda (tuple[int, int]): candidate exit cell.

        Returns:
            - implicada (bool): True if the exit is deduced with certainty to be at 'celda'.
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
        Returns the exit if it has been deduced with logical certainty.
        Returns:
            - salida (tuple[int, int] | None): exit cell if it has been
                deduced with certainty, None otherwise.
        """
        for c in self.exit_candidates():
            if self.entails_exit(c):
                return c
        return None
