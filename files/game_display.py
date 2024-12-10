# display.py
# Game code inspired by @Kite

# Import necessary modules
from tkinter import Frame, Label, CENTER, Button
import game_ai
import game_functions

# Constants for game visuals and settings
EDGE_LENGTH = 400  # Size of the game window
CELL_COUNT = 4  # Number of tiles in a row/column
CELL_PAD = 10  # Padding between tiles

# Keyboard controls
UP_KEY = "'w'"
DOWN_KEY = "'s'"
LEFT_KEY = "'a'"
RIGHT_KEY = "'d'"
AI_PLAY_KEY = "'1'"

# Fonts and colours
LABEL_FONT = ("Verdana", 40, "bold")
SCORE_FONT = ("Verdana", 20, "bold")

GAME_COLOUR = "#bbada0"
EMPTY_COLOUR = "#cdc1b4"

# Background colours for tiles
TILE_COLOURS = {
    2: "#eee4da",
    4: "#ede0c8",
    8: "#f2b179",
    16: "#f59563",
    32: "#f67c5f",
    64: "#f65e3b",
    128: "#edcf72",
    256: "#edcc61",
    512: "#edc850",
    1024: "#edc53f",
    2048: "#edc22e",
    4096: "#3c3a32",  # Default darker colour for subsequent tiles
    8192: "#3c3a32",
    16384: "#3c3a32",
}

# Text colours for tiles
LABEL_COLOURS = {
    2: "#776e65",
    4: "#776e65",
    8: "#f9f6f2",
    16: "#f9f6f2",
    32: "#f9f6f2",
    64: "#f9f6f2",
    128: "#f9f6f2",
    256: "#f9f6f2",
    512: "#f9f6f2",
    1024: "#f9f6f2",
    2048: "#f9f6f2",
    4096: "#f9f6f2",  # Consistent text colour for subsequent tiles
    8192: "#f9f6f2",
    16384: "#f9f6f2",
}

class Display(Frame):
    """
    Main class for the 2048 game interface using Tkinter.
    Handles grid initialization, user input, AI interaction, and game rendering.
    """

    def __init__(self):
        super().__init__()
        self.grid()
        self.master.title('2048')
        self.master.bind("<Key>", self.key_press)  # Bind key press events

        # Command mapping for key inputs
        self.commands = {
            UP_KEY: self.move_up_command,
            DOWN_KEY: self.move_down_command,
            LEFT_KEY: self.move_left_command,
            RIGHT_KEY: self.move_right_command,
        }

        # Initialize game variables
        self.grid_cells = []  # List to store tile widgets
        self.score = 0  # Current score
        self.highest_score = 0  # Highest score achieved
        self.ai_playing = False  # Flag to track AI playing status
        self.build_grid()  # Build the game grid layout
        self.init_matrix()  # Initialize the game matrix
        self.draw_grid_cells()  # Render the initial grid
        self.mainloop()  # Start the Tkinter event loop

    def build_grid(self):
        """
        Creates the game layout, including the grid, score labels, and control buttons.
        """
        # Create the main frame
        background = Frame(self, bg=GAME_COLOUR, width=EDGE_LENGTH, height=100)
        background.grid()

        # Create the highest score display
        self.highest_score_label = Label(
            self, text=f"Highest: {self.highest_score}",
            font=SCORE_FONT, bg=GAME_COLOUR, fg="black"
        )
        self.highest_score_label.place(x=EDGE_LENGTH - 160, y=10)

        # Create the score display
        self.score_label = Label(
            self, text=f"Score: {self.score}",
            font=SCORE_FONT, bg=GAME_COLOUR, fg="black"
        )
        self.score_label.place(x=EDGE_LENGTH - 160, y=50)

        # Create a Reset button
        self.reset_button = Button(
            self, text="Reset", font=SCORE_FONT, bg="red", fg="white",
            command=self.reset_game  # Reset the game when clicked
        )
        self.reset_button.place(x=EDGE_LENGTH + 230, y=40)

        # Create the game grid
        grid_frame = Frame(self, bg=GAME_COLOUR, width=EDGE_LENGTH, height=EDGE_LENGTH)
        grid_frame.grid(row=1, column=0)

        # Add tiles to the grid
        for row in range(CELL_COUNT):
            grid_row = []
            for col in range(CELL_COUNT):
                cell = Frame(
                    grid_frame, bg=EMPTY_COLOUR,
                    width=EDGE_LENGTH / CELL_COUNT,
                    height=EDGE_LENGTH / CELL_COUNT
                )
                cell.grid(row=row, column=col, padx=CELL_PAD, pady=CELL_PAD)
                tile = Label(
                    master=cell, text="", bg=EMPTY_COLOUR,
                    justify=CENTER, font=LABEL_FONT, width=5, height=2
                )
                tile.grid()
                grid_row.append(tile)
            self.grid_cells.append(grid_row)

    def init_matrix(self):
        """
        Initializes the game matrix with two starting tiles.
        """
        self.matrix = game_functions.initialize_game()

    def draw_grid_cells(self):
        """
        Updates the grid display based on the current game state.
        """
        for row in range(CELL_COUNT):
            for col in range(CELL_COUNT):
                tile_value = self.matrix[row][col]
                if not tile_value:
                    self.grid_cells[row][col].configure(text="", bg=EMPTY_COLOUR)
                else:
                    self.grid_cells[row][col].configure(
                        text=str(tile_value),
                        bg=TILE_COLOURS.get(tile_value, TILE_COLOURS[4096]),
                        fg=LABEL_COLOURS.get(tile_value, LABEL_COLOURS[4096])
                    )
        self.update_idletasks()

    def key_press(self, event):
        """
        Handles key press events for player moves and toggling AI play.
        """
        key = repr(event.char)
        if key == AI_PLAY_KEY:  # Toggle AI mode
            self.toggle_ai_play()
        elif key in self.commands:  # Execute player move
            self.commands[key]()

    def toggle_ai_play(self):
        """
        Toggles the AI's playing state and updates the button text.
        """
        if not self.ai_playing:
            self.ai_playing = True
            self.run_ai_play()
            self.ai_play_button.configure(text="Stop AI (p)")
        else:
            self.ai_playing = False
            self.ai_play_button.configure(text="AI Play (p)")

    def run_ai_play(self):
        """
        Runs the AI's moves continuously until no more moves can be made or AI mode is disabled.
        """
        if self.ai_playing:
            self.ai_move_single()
            self.master.after(100, self.run_ai_play)  # Schedule next AI move after 100ms

    def ai_move_single(self):
        """
        Performs a single AI move and updates the grid.
        """
        self.matrix, move_made, score_increment = game_ai.ai_move(self.matrix)
        if move_made:
            self.score += score_increment
            self.matrix = game_functions.add_new_tile(self.matrix)
            self.draw_grid_cells()
            self.update_score()

    # Move commands for the player
    def move_up_command(self):
        self.execute_move(game_functions.move_up)

    def move_down_command(self):
        self.execute_move(game_functions.move_down)

    def move_left_command(self):
        self.execute_move(game_functions.move_left)

    def move_right_command(self):
        self.execute_move(game_functions.move_right)

    def execute_move(self, move_func):
        """
        Executes a move using the given function, updates the grid, and adds a new tile if needed.
        """
        self.matrix, move_made, score_increment = move_func(self.matrix)
        if move_made:
            self.score += score_increment
            self.matrix = game_functions.add_new_tile(self.matrix)
            self.draw_grid_cells()
            self.update_score()

    def update_score(self):
        """
        Updates the displayed score and highest score.
        """
        self.highest_score = max(self.highest_score, self.score)
        self.score_label.configure(text=f"Score: {self.score}")
        self.highest_score_label.configure(text=f"Highest: {self.highest_score}")

    def reset_game(self):
        """
        Resets the game state and stops AI mode.
        """
        self.score = 0
        self.init_matrix()
        self.draw_grid_cells()
        self.update_score()
        self.ai_playing = False
        self.ai_play_button.configure(text="AI Play (p)")


gamegrid = Display()
