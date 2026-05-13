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
        self.show_main_menu()

    def show_main_menu(self):
        """Display the main menu with size selector and game mode buttons."""
        self.game_active = False
        self.board = None
        self.cells = []
        self.board_frame = None
        self.clear_window()

        main_frame = tk.Frame(self.root)
        main_frame.pack(expand=True)

        # Title
        tk.Label(main_frame, text="MINESWEEPER", font=("Arial", 24, "bold")).pack(pady=20)

        # Size selector frame
        size_frame = tk.Frame(main_frame)
        size_frame.pack(pady=10)

        tk.Label(size_frame, text="Board Size:", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        self.size_var = tk.IntVar(value=10)
        for size in [8, 10, 12, 16]:
            tk.Radiobutton(size_frame, text=str(size), variable=self.size_var, value=size).pack(side=tk.LEFT, padx=5)

        # Buttons frame
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=20)

        tk.Button(
            button_frame,
            text="Start Game",
            command=self.start_game,
            width=15,
            height=2,
            font=("Arial", 12),
            bg="#4CAF50",
            fg="white",
        ).pack(pady=10)

        tk.Button(
            button_frame,
            text="Other Game Mode (Coming Soon)",
            command=lambda: messagebox.showinfo("Info", "Coming soon!"),
            width=15,
            height=2,
            font=("Arial", 12),
            state=tk.DISABLED,
        ).pack(pady=10)

    def start_game(self):
        """Initialize a new game board with selected size."""
        dim_size = self.size_var.get()
        num_bombs = max(1, round(dim_size ** 2 * 0.12))  # 12% of the board as bombs
        self.board = Board(dim_size, num_bombs)
        self.game_active = True
        self.show_game_board()

    def show_game_board(self):
        """Display the game board interface."""
        self.clear_window()

        # Header frame with info and back button
        header_frame = tk.Frame(self.root)
        header_frame.pack(pady=10)

        tk.Label(header_frame, text=f"Bombs to mark: {self.board.num_bombs}", font=("Arial", 12)).pack(side=tk.LEFT, padx=20)
        tk.Button(header_frame, text="Back to Menu", command=self.show_main_menu).pack(side=tk.LEFT, padx=20)

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

        self.update_board_display()

    def on_cell_click(self, row, col):
        """Forward left click to backend and update view from backend response."""
        if not self.game_active or self.board is None:
            return

        result = self.board.dig(row, col)

        # result: { 'safe': bool, 'dug': [...], 'won': bool }
        if not result.get('safe', True):
            # backend already revealed all cells
            messagebox.showwarning("Game Over", "You hit a bomb! Game Over.")
            self.game_active = False
        elif result.get('won'):
            messagebox.showinfo("Victory", "Congratulations! You won!")
            self.game_active = False

        self.update_board_display()

    def on_right_click(self, row, col):
        """Forward right click (flag) to backend and update view."""
        if not self.game_active or self.board is None:
            return

        result = self.board.toggle_flag(row, col)
        # result: { 'flagged': bool, 'coord': (r,c) }
        # no business logic here, UI will reflect backend state
        self.update_board_display()

    def update_board_display(self):
        """Render the board using backend's `get_view()` only."""
        if not self.board or not self.cells:
            return

        view = self.board.get_view()

        number_colors = {
            1: "blue",
            2: "green",
            3: "red",
            4: "purple",
            5: "brown",
            6: "teal",
            7: "black",
            8: "gray",
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
                    widget.config(text=str(val), bg="white", fg=color, state=tk.DISABLED, relief=tk.SUNKEN, disabledforeground=color)

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
