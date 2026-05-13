from collections import deque
import random, re


class Board:
    def __init__(self, dim_size) -> None:
        self.dim_size = dim_size
        self.num_bombs = self.gen_number_bomb()
        self.board = self.make_new_board()
        self.assign_values_to_board()
        self.dug = set()  # it will keep track of dug location like (0,0) etc.
        self.flagged = set()  # it will keep track of flagged bomb locations like (0,0) etc.
        self.visible_board = [[' ' for _ in range(self.dim_size)] for _ in range(self.dim_size)]

    def gen_number_bomb(self):
        x = self.dim_size
        base = max(1, 0.5 * x**2 - 7 * x + 30)
        return int(base + random.randint(1, round(x/2)))

    def make_new_board(self):

        board = [[None for _ in range(self.dim_size)] for _ in range(self.dim_size)]

        #plant the bombs
        bombs_planted = 0

        while bombs_planted < self.num_bombs:
            loc = random.randint(0, self.dim_size**2 - 1)
            row = loc // self.dim_size
            col = loc % self.dim_size

            if board[row][col] == '*':
                #this means we've already planted the boms at this location so keep going
                continue

            board[row][col] = '*' # plant the bomb
            bombs_planted += 1
        
        return board

    def assign_values_to_board(self):

        for r in range(self.dim_size):
            for c in range(self.dim_size):
                if self.board[r][c] == '*':
                    # if this ia already a bomb, we don't want to calculate anything
                    continue
                self.board[r][c] = self.get_num_neighboring_bombs(r,c)
    
    def get_num_neighboring_bombs(self, row,col):
        num_neighboring_bombs = 0
        for dr in range(-1, 2):
            for dc in range(-1, 2):
                nr, nc = row + dr, col + dc
                if 0 <= nr < self.dim_size and 0 <= nc < self.dim_size:
                    if (nr, nc) != (row, col) and self.board[nr][nc] == '*':
                        num_neighboring_bombs += 1

        return num_neighboring_bombs

    def dig(self, row, col):
        """Dig at (row,col). Retourne un dict:
            { 'safe': bool, 'dug': [(r,c),...], 'won': bool }
        Si une bombe est touchée, 'safe' sera False et 'dug' contiendra toutes les cases révélées pour affichage.
        """
        # validate coords
        if row < 0 or row >= self.dim_size or col < 0 or col >= self.dim_size:
            return {'safe': True, 'dug': [], 'won': self.is_won()}  # nothing happens

        # if already dug, nothing to do
        if (row, col) in self.dug:
            return {'safe': True, 'dug': [], 'won': self.is_won()}

        # If bomb
        if self.board[row][col] == '*':
            # reveal everything
            all_cells = [(r, c) for r in range(self.dim_size) for c in range(self.dim_size)]
            # set dug to all so get_view reveals bombs
            self.dug.update(all_cells)
            return {'safe': False, 'dug': all_cells, 'won': False}

        # Otherwise, BFS reveal
        prev_dug = set(self.dug)
        queue = deque([(row, col)])

        while queue:
            r, c = queue.popleft()

            if (r, c) in self.dug:
                continue

            self.dug.add((r, c))

            if self.board[r][c] == 0:
                for dr in range(-1, 2):
                    for dc in range(-1, 2):
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < self.dim_size and 0 <= nc < self.dim_size:
                            if (nr, nc) not in self.dug:
                                queue.append((nr, nc))

        newly_dug = list(self.dug - prev_dug)
        won = self.is_won()
        return {'safe': True, 'dug': newly_dug, 'won': won}

    def toggle_flag(self, row, col):
        """Toggle flag. Retourne dict: { 'flagged': bool, 'coord': (row,col) }"""
        if row < 0 or row >= self.dim_size or col < 0 or col >= self.dim_size:
            return {'flagged': False, 'coord': (row, col)}
        if (row, col) in self.dug:
            return {'flagged': False, 'coord': (row, col)}
        if (row, col) in self.flagged:
            self.flagged.remove((row, col))
            return {'flagged': False, 'coord': (row, col)}
        else:
            self.flagged.add((row, col))
            return {'flagged': True, 'coord': (row, col)}

    def is_dug(self, row, col):
        return (row, col) in self.dug

    def is_flagged(self, row, col):
        return (row, col) in self.flagged

    def is_won(self):
        return len(self.dug) == self.dim_size**2 - self.num_bombs

    def get_cell_value(self, row, col):
        return self.board[row][col]

    def get_view(self):
        """Retourne une matrice 2D représentant l'état visible pour l'UI:
            - ' ' pour non découvert
            - 'F' pour drapeau
            - int or '*' pour cases découvertes
        """
        view = [[' ' for _ in range(self.dim_size)] for _ in range(self.dim_size)]
        for r in range(self.dim_size):
            for c in range(self.dim_size):
                if (r, c) in self.flagged:
                    view[r][c] = 'F'
                elif (r, c) in self.dug:
                    val = self.board[r][c]
                    view[r][c] = '*' if val == '*' else val
                else:
                    view[r][c] = ' '
        return view

    def evaluate_difficulty(self):
        """Évalue la difficulté d'une grille de mines et renvoie un pourcentage (0-100).

        Le score tient compte de:
        - la densité de bombes par rapport à la taille de la grille,
        - le regroupement des bombes,
        - la proximité moyenne entre bombes,
        - et surtout une normalisation selon la taille du plateau pour éviter un score quasi constant.
        """
        bombs = [(r, c) for r in range(self.dim_size) for c in range(self.dim_size) if self.board[r][c] == '*']
        bomb_count = len(bombs)
        total_cells = self.dim_size * self.dim_size
        if total_cells == 0:
            return 0

        density = bomb_count / total_cells

        # Taille du plateau -> facteur d'ajustement
        # petits boards = plus faciles à lire, grands boards = plus difficiles
        board_size_factor = min(self.dim_size / 16.0, 1.0)

        # Cas limites
        if bomb_count == 0:
            return 0
        if bomb_count == total_cells:
            return 100

        # Clustering en 8-voisins
        visited = set()
        clusters = []

        def neighbors8(rr, cc):
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = rr + dr, cc + dc
                    if 0 <= nr < self.dim_size and 0 <= nc < self.dim_size:
                        yield (nr, nc)

        bomb_set = set(bombs)
        for b in bombs:
            if b in visited:
                continue
            stack = [b]
            cluster = []
            while stack:
                cur = stack.pop()
                if cur in visited:
                    continue
                visited.add(cur)
                if cur in bomb_set:
                    cluster.append(cur)
                    for nb in neighbors8(*cur):
                        if nb not in visited and nb in bomb_set:
                            stack.append(nb)
            clusters.append(cluster)

        cluster_sizes = sorted((len(c) for c in clusters), reverse=True)
        largest_cluster = cluster_sizes[0] if cluster_sizes else 0
        largest_cluster_ratio = largest_cluster / bomb_count if bomb_count else 0.0

        # Distance moyenne au plus proche voisin
        import math
        if bomb_count <= 1:
            avg_nn = float('inf')
        else:
            total_nn = 0.0
            for i, (r, c) in enumerate(bombs):
                min_d = None
                for j, (r2, c2) in enumerate(bombs):
                    if i == j:
                        continue
                    d = abs(r - r2) + abs(c - c2)
                    if min_d is None or d < min_d:
                        min_d = d
                total_nn += (min_d if min_d is not None else 0)
            avg_nn = total_nn / bomb_count

        # Normalisation par taille de grille: sur une grande grille, la même densité est moins "serrée"
        density_target = 0.08 + (0.12 * board_size_factor)  # 8% à 20% selon la taille
        density_score = min(density / max(density_target, 0.01), 1.0)

        # Grande grille + gros cluster = difficulté plus élevée
        cluster_score = largest_cluster_ratio

        # Plus les bombes sont proches, plus c'est difficile
        max_possible = max(self.dim_size, 1)
        nn_score = 1.0 - min(avg_nn / max_possible, 1.0) if not math.isinf(avg_nn) else 0.0

        # Ajustement global par taille du plateau
        # petit board -> score un peu réduit; grand board -> score un peu augmenté
        size_boost = 0.75 + (0.5 * board_size_factor)  # 0.75 .. 1.25

        score = (0.45 * density_score + 0.35 * cluster_score + 0.20 * nn_score) * size_boost
        score = max(0.0, min(1.0, score))

        return int(round(score * 100))

    def __str__(self) -> str:
        # Create a string representation of the board

        for row, col in self.dug:
            self.visible_board[row][col] = str(self.board[row][col])

        # Create the string representation
        string_rep = '    +' + '-' * (self.dim_size * 4 - 1) + '+\n'
        for row_idx, row in enumerate(self.visible_board):
            if row_idx <= 9:
                string_rep += f'  {row_idx} | ' + ' | '.join(str(cell) for cell in row) + ' |\n'
            else:
                string_rep += f' {row_idx} | ' + ' | '.join(str(cell) for cell in row) + ' |\n'
            string_rep += '    +' + '-' * (self.dim_size * 4 - 1) + '+\n'

        # Add column indices
        indices_row = ' ' * 4
        for idx in range(self.dim_size):
            indices_row += f'{idx:>{3}} '
        indices_row += '\n'

        return indices_row + string_rep


def bomb_count_for_size(dim_size):
    """Retourne un nombre de bombes simple basé sur la taille du plateau.

    La formule prend une base liée à la taille de la grille et ajoute un aléatoire entre 1 et 6.
    """
    base = max(1, dim_size // 2)
    return base + random.randint(1, 6)


def play(dim_size=10, num_bombs=5):
    #Step 1: create the board and plant the bombs
    board = Board(dim_size,num_bombs)
    #Step 2: show the user the board and ask for where they want to dig
    #Step 3a: if location is bomb, show game over message
    #Step 3b: if location is not a bomb, dig recursively until each square is at least next to a bomb
    #Step 4: repeat step2 and Step 3a/b until there are no more places to dig -> Victory  
    safe = True
    bombs_marked = sum(r.count('X') for r in board.visible_board)

    while len(board.dug) < board.dim_size**2 - (num_bombs-bombs_marked):
        print("Bombs left = " + str(num_bombs-bombs_marked))
        print(board)

        user_input = re.split(',(\\s)*', input("Where would you like to dig? Input as row,col: "))
        row, col = int(user_input[0]), int(user_input[-1])

        if row < 0 or row >= board.dim_size or col < 0 or col >= board.dim_size:
            print("Invalid Location. Try again.")
            continue

        result = board.dig(row,col)
        safe = result['safe']

        if not safe:
            #dug a bomb
            break # game over
        
        print("Bombs left = " + str(num_bombs-bombs_marked))
        print(board)

        #flag a bomb
        if num_bombs-bombs_marked > 0:
            flag_a_bomb = 'Y'
        else:
            flag_a_bomb = 'N'

        while flag_a_bomb == 'Y':
            if num_bombs-bombs_marked > 0:
                flag_a_bomb = input("Do you want to flag a bomb? Input Y/N: ").upper()
            else:
                flag_a_bomb = 'N'
            if flag_a_bomb != 'Y':
                break
            
            user_input = re.split(',(\\s)*', input("Where would you like to flag a bomb? Input as row,col: "))
            row, col = int(user_input[0]), int(user_input[-1])

            if row < 0 or row >= board.dim_size or col < 0 or col >= board.dim_size:
                print("Invalid Location. Try again.")
                continue
            if (row, col) in board.dug:
                print("This location is already dug. Try again.")
                continue
            
            if board.board[row][col] != '*':
                print("You marked the wrong location. This is not a bomb.")
                safe = False
                break
            board.dug.add((row,col))
            bombs_marked+=1
            
            
            print("Bombs left = " + str(num_bombs-bombs_marked))
            print(board)
        
        if not safe:
            #dug a bomb
            break # game over


    if safe:
        print("CONGRATULATIONS!!!! YOU ARE VICTORIOUS!")
    else:
        print("SORRY GAME OVER :(")

        board.dug = [(r,c) for r in range(board.dim_size) for c in range(board.dim_size)]
        print(board)


def main():
    from gui import run_gui
    run_gui()


if __name__ == '__main__':
    main()
