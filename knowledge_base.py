from itertools import combinations

class KnowledgeBase:
    def __init__(self, N: int):
        self.N = N
        self.visited: set[tuple[int,int]] = set()
        self.obs: dict[tuple[int,int], tuple[bool,bool,bool]] = {}  # (breeze, snore, glow)
        self.soldier_dead = False

    def add_percept(self, pos, perceptos):
        brisa, ronq, respl, *_rest, grito = perceptos
        self.visited.add(pos)
        self.obs[pos] = (brisa, ronq, respl)
        if grito:
            self.soldier_dead = True

    def neighbors(self, c):
        i,j = c
        cand = [(i-1,j),(i+1,j),(i,j-1),(i,j+1)]
        return [(x,y) for x,y in cand if 0 <= x < self.N and 0 <= y < self.N]

    def _candidate_cells(self):
        return [(i,j) for i in range(self.N) for j in range(self.N) if (i,j) not in self.visited]

    def consistent_worlds(self):
        # Devuelve generador de mundos consistentes:
        # world = (pits_set, soldier_pos or None)
        cells = [(i,j) for i in range(self.N) for j in range(self.N)]

        # 1) candidatos iniciales
        cand_pit = [c for c in cells if c not in self.visited]
        cand_soldier = [c for c in cells if c not in self.visited]

        # 2) filtrado rápido por "no brisa" / "no ronquido"
        forbidden_pit = set()
        forbidden_soldier = set()
        required_pit_frontiers = []     # lista de sets: en cada obs con brisa True, al menos uno aquí
        required_soldier_frontiers = [] # similar

        for c, (brisa, ronq, _respl) in self.obs.items():
            nbs = set(self.neighbors(c))
            if not brisa:
                forbidden_pit |= nbs
            else:
                required_pit_frontiers.append(nbs)

            if not self.soldier_dead:
                if not ronq:
                    forbidden_soldier |= nbs
                else:
                    required_soldier_frontiers.append(nbs)

        cand_pit = [c for c in cand_pit if c not in forbidden_pit]
        cand_soldier = [c for c in cand_soldier if c not in forbidden_soldier]

        # 3) enumeración de precipicios (exactamente 3)
        for pits in combinations(cand_pit, 3):
            pits = set(pits)

            # satisface todas las brisas True?
            ok = True
            for frontier in required_pit_frontiers:
                if pits.isdisjoint(frontier):
                    ok = False
                    break
            if not ok:
                continue

            # 4) enumeración del soldado si vive
            if self.soldier_dead:
                yield (pits, None)
            else:
                for s in cand_soldier:
                    if s in pits:
                        continue

                    ok2 = True
                    for frontier in required_soldier_frontiers:
                        if s not in frontier:
                            ok2 = False
                            break
                    if ok2:
                        yield (pits, s)

    def entails_no_pit(self, cell):
        found_model = False
        for pits, _s in self.consistent_worlds():
            found_model = True
            if cell in pits:
                return False
        return found_model  # True si hay modelos y en todos NO hay pit

    def entails_no_soldier(self, cell):
        if self.soldier_dead:
            return True
        found_model = False
        for _pits, s in self.consistent_worlds():
            found_model = True
            if s == cell:
                return False
        return found_model

    def is_safe(self, cell):
        return self.entails_no_pit(cell) and self.entails_no_soldier(cell)

    def possible_pits_and_soldier(self):
        poss_pits = set()
        poss_soldier = set()
        for pits, s in self.consistent_worlds():
            poss_pits |= pits
            if s is not None:
                poss_soldier.add(s)
        return poss_pits, poss_soldier
