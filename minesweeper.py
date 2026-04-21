from collections import deque
import random, re

class Board:
    def __init__(self, dim_size, num_bombs) -> None:
        self.dim_size = dim_size
        self.num_bombs = num_bombs
        self.board = self.make_new_board()
        self.assign_values_to_board()
        self.dug = set() # it will keep track of dug location like (0,0) etc.
        self.visible_board = [[' ' for _ in range(self.dim_size)] for _ in range(self.dim_size)]

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
        # iterate through each of the neighbouring positions and sum number of bombs
        # top left: (row-1,col-1)
        # top middle: (row-1,col)
        # top right: (row-1,col+1)
        # left: (row,col-1)
        # right: (row,col+1)
        # bottom left: (row+1,col-1)
        # bottom middle: (row+1,col)
        # bottom right: (row+1,col+1)

        
        # min and max will make sure we don't go out of bound

        num_neighboring_bombs = 0
        for dr in range(-1, 2):
            for dc in range(-1, 2):
                nr, nc = row + dr, col + dc
                if 0 <= nr < self.dim_size and 0 <= nc < self.dim_size:
                    if (nr, nc) != (row, col) and self.board[nr][nc] == '*':
                        num_neighboring_bombs += 1

        return num_neighboring_bombs

    def dig(self, row, col):
        # Recursive Call
        # self.dug.add((row,col))

        # if self.board[row][col] == '*':# you dig the bomb
        #     return False
        # elif self.board[row][col] > 0:# there is neighboring bomb -> finish dig
        #     return True
        
        # # no neighboring bomb, dig recursively until there is one
        # for r in range(max(0, row-1), min(self.dim_size-1, (row+1))+1):
        #     for c in range(max(0, col-1), min(self.dim_size-1, (col+1))+1):
        #         if (r,c) in self.dug:
        #             continue # don't dig where you've already dug
        
        #         self.dig(r,c)
                
        # return True


        # Queue for BFS
        if self.board[row][col] == '*':
            return False #you dig a bomb
        

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
                            queue.append((nr, nc))

        return True
    
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

        safe = board.dig(row,col)

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

if __name__ == '__main__':
    play()