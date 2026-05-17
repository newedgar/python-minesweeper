import tkinter as tk
from tkinter import messagebox
from minesweeper import Board


class MinesweeperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Minesweeper")
        self.root.geometry("800x800")
        self.board = None
        self.cells = []
        self.game_active = False
        self.board_frame = None
        self.mode = 'single'  # 'single' or 'multi'
        self.current_player = 1
        self.turn_label = None
        self.difficulty = 0
        self.show_main_menu()
        self.remaining_bomb= None

    def show_main_menu(self):
        """Display the main menu with size selector and game mode buttons."""
        self.game_active = False
        self.board = None
        self.cells = []
        self.board_frame = None
        self.mode = 'single'
        self.current_player = 1
        self.turn_label = None
        self.difficulty = 0
        self.clear_window()
        self.remaining_bomb = None

        main_frame = tk.Frame(self.root)
        main_frame.pack(expand=True)

        # Title
        tk.Label(main_frame, text="MINESWEEPER", font=("Arial", 24, "bold")).pack(pady=20)

        # Size selector frame
        size_frame = tk.Frame(main_frame)
        size_frame.pack(pady=10)

        tk.Label(size_frame, text="Board Size:", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        self.size_var = tk.IntVar(value=10)
        for size in [8, 10, 12, 14]:
            tk.Radiobutton(size_frame, text=str(size), variable=self.size_var, value=size).pack(side=tk.LEFT, padx=5)

        # Buttons frame
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=20)

        tk.Button(
            button_frame,
            text="Start Single Player",
            command=self.start_single_player,
            width=20,
            height=2,
            font=("Arial", 12),
            bg="#4CAF50",
            fg="white",
        ).pack(pady=8)

        tk.Button(
            button_frame,
            text="Start Two Players",
            command=self.start_two_players,
            width=20,
            height=2,
            font=("Arial", 12),
            bg="#2196F3",
            fg="white",
        ).pack(pady=8)


    def start_single_player(self):
        self.mode = 'single'
        self.current_player = 1
        self._start_game()

    def start_two_players(self):
        self.mode = 'multi'
        self.current_player = 1
        self._start_game()

    def _start_game(self):
        """Common game start routine."""
        dim_size = self.size_var.get()
        self.board = Board(dim_size)
        self.game_active = True
        self.difficulty = self.board.evaluate_difficulty()
        self.show_game_board()

    def show_game_board(self):
        """Display the game board interface."""
        self.clear_window()

        # Header frame with info and back button
        header_frame = tk.Frame(self.root)
        header_frame.pack(pady=10)

        self.remaining_bomb = tk.Label(header_frame, text=f"Bombs to mark: {self.board.get_remaining_bomb()}", font=("Arial", 12))
        self.remaining_bomb.pack(side=tk.LEFT, padx=20)

        tk.Button(header_frame, text="Back to Menu", command=self.show_main_menu).pack(side=tk.LEFT, padx=20)

        tk.Button(
            header_frame,
            text="Hint",
            command=self.on_hint_click,
            width=10,
            font=("Arial", 12),
            bg="#FFC107",
            fg="black",
        ).pack(side=tk.LEFT, padx=20)

        tk.Button(
            header_frame,
            text="Solve",
            command=self.on_solve_click,
            width=10,
            font=("Arial", 12),
            bg="#9C27B0",
            fg="white",
        ).pack(side=tk.LEFT, padx=20)

        self.board_frame = tk.Frame(self.root)
        self.board_frame.pack()

        self.cells = []
        for r in range(self.board.dim_size):
            row_cells = []
            for c in range(self.board.dim_size):
                cell = tk.Button(
                    self.board_frame,
                    width=4,
                    height=2,
                    font=("Arial", 10, "bold"),
                    command=lambda row=r, col=c: self.on_cell_click(row, col),
                )
                cell.grid(row=r, column=c, padx=1, pady=1)
                # right-click for flagging
                cell.bind("<Button-3>", lambda e, row=r, col=c: self.on_right_click(row, col))
                row_cells.append(cell)
            self.cells.append(row_cells)

        # Turn label at the bottom
        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(pady=8)
        self.turn_label = tk.Label(bottom_frame, text=self._turn_text(), font=("Arial", 12, "bold"))
        self.turn_label.pack()
        self.difficulty_label = tk.Label(bottom_frame, text= "Difficulty : "+str(self.difficulty)+" %", font=("Arial", 12, "bold"))
        self.difficulty_label.pack()

        self.update_board_display()


    def _turn_text(self):
        if self.mode == 'multi' and self.game_active:
            return f"Player {self.current_player}'s turn"
        elif self.mode == 'multi' and not self.game_active:
            return "Game over"
        else:
            return "Single Player"

    def _advance_turn(self):
        if self.mode != 'multi':
            return
        self.current_player = 2 if self.current_player == 1 else 1
        if self.turn_label:
            self.turn_label.config(text=self._turn_text())

    def _update_remaining_bomb_label(self):
        if self.remaining_bomb and self.board:
            self.remaining_bomb.config(text=f"Bombs to mark: {self.board.get_remaining_bomb()}")

    def on_cell_click(self, row, col):
        """Forward left click to backend and update view from backend response."""
        if not self.game_active or self.board is None:
            return

        result = self.board.dig(row, col)

        # result: { 'safe': bool, 'dug': [...], 'won': bool }
        if not result.get('safe', True):
            # backend already revealed all cells
            messagebox.showwarning("Game Over", f"Player {self.current_player} hit a bomb! Game Over.")
            self.game_active = False
            # update view once to reveal bombs
            self.update_board_display()
            if self.turn_label:
                self.turn_label.config(text="Game over")
            return
        elif result.get('won'):
            messagebox.showinfo("Victory", f"Player {self.current_player} wins! Congratulations!")
            self.game_active = False
            self.update_board_display()
            if self.turn_label:
                self.turn_label.config(text="Game over")
            return

        # If some cells were actually dug, consider it a valid move and advance turn in multi
        if self.mode == 'multi' and result.get('dug'):
            if len(result.get('dug')) > 0:
                self._advance_turn()

        self.update_board_display()

    def on_right_click(self, row, col):
        """Forward right click (flag) to backend and update view."""
        if not self.game_active or self.board is None:
            return

        prev_flagged = self.board.is_flagged(row, col)
        result = self.board.toggle_flag(row, col)
        # result: { 'flagged': bool, 'coord': (r,c) }
        # If flag state changed, count as a move in multi
        if self.mode == 'multi' and result.get('flagged') != prev_flagged:
            self._advance_turn()

        self.update_board_display()

    def on_hint_click(self):
        """
        Ask the bot to make exactly one move, then update the display.
        """
        if not self.game_active or self.board is None:
            return

        result = self.board.hint()

        if not result.get("moved"):
            messagebox.showinfo(
                "Hint",
                "No safe logical move found."
            )
            return

        if not result.get("safe", True):
            messagebox.showwarning(
                "Game Over",
                "The bot hit a bomb! Game Over."
            )
            self.game_active = False
            self.update_board_display()

            if self.turn_label:
                self.turn_label.config(text="Game over")

            return

        if result.get("won"):
            messagebox.showinfo(
                "Victory",
                "The bot found the winning move!"
            )
            self.game_active = False
            self.update_board_display()

            if self.turn_label:
                self.turn_label.config(text="Game over")

            return

        if self.mode == "multi":
            self._advance_turn()

        self.update_board_display()

    def on_solve_click(self):
        """
        Ask the bot to solve the board as much as possible.
        """
        if not self.game_active or self.board is None:
            return

        solved = self.board.solve_basic_bot()

        self.update_board_display()

        if solved:
            messagebox.showinfo(
                "Victory",
                "The bot solved the puzzle!"
            )
            self.game_active = False

            if self.turn_label:
                self.turn_label.config(text="Game over")
        else:
            messagebox.showinfo(
                "Solver Stopped",
                "The bot could not solve the whole puzzle."
            )
    def update_board_display(self):
        """Render the board using backend's `get_view()` only."""
        if not self.board or not self.cells:
            return

        view = self.board.get_view()

        number_colors = {
            1: "green",
            2: "blue",
            3: "orange",
            4: "purple",
            5: "red",
            6: "red",
            7: "black",
            8: "black",
        }

        for r in range(self.board.dim_size):
            for c in range(self.board.dim_size):
                widget = self.cells[r][c]
                if not widget.winfo_exists():
                    continue

                val = view[r][c]
                # Backend view: ' ' (undiscovered), 'F' (flag), int or '*' for discovered
                if val == ' ':
                    widget.config(text="", bg="#cccccc", fg="black", state=tk.NORMAL, relief=tk.RAISED)
                elif val == 'F':
                    widget.config(text="🚩", bg="#ffcccc", fg="black", state=tk.NORMAL, relief=tk.RAISED)
                elif val == '*':
                    # revealed bomb
                    widget.config(text="💣", bg="white", fg="black", state=tk.DISABLED, relief=tk.SUNKEN, disabledforeground="black")
                else:
                    # number
                    color = number_colors.get(val, "black")
                    display_text = "" if val == 0 else str(val)
                    widget.config(text=display_text, bg="white", fg=color, state=tk.DISABLED, relief=tk.SUNKEN, disabledforeground=color)

        # update turn label
        if self.turn_label:
            self.turn_label.config(text=self._turn_text())
        self._update_remaining_bomb_label()

    def clear_window(self):
        """Clear all widgets from the window."""
        for widget in self.root.winfo_children():
            widget.destroy()


def run_gui():
    """Launch the Minesweeper GUI application."""
    root = tk.Tk()
    MinesweeperGUI(root)
    root.mainloop()


if __name__ == '__main__':
    run_gui()
