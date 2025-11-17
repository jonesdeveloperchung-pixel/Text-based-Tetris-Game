import curses
from collections import namedtuple
import random
import time

# Named tuples for better readability and structure
GameBoard = namedtuple('GameBoard', ['width', 'height', 'blocks'])
Tetromino = namedtuple('Tetromino', ['shape', 'position', 'rotation', 'color_id'])

# Tetromino shapes and their rotations. Each shape is a list of 2D arrays,
# where each 2D array represents a rotation state. '1' indicates a block, '0' is empty.
SHAPES = {
    'I': [
        [[1, 1, 1, 1]], # 0 degrees (horizontal)
        [[1], [1], [1], [1]] # 90 degrees (vertical)
    ],
    'O': [
        [[1, 1], [1, 1]] # 0 degrees (square, no rotation effect)
    ],
    'T': [
        [[0, 1, 0], [1, 1, 1]], # 0 degrees
        [[1, 0], [1, 1], [1, 0]], # 90 degrees
        [[1, 1, 1], [0, 1, 0]], # 180 degrees
        [[0, 1], [1, 1], [0, 1]] # 270 degrees
    ],
    'S': [
        [[0, 1, 1], [1, 1, 0]], # 0 degrees
        [[1, 0], [1, 1], [0, 1]] # 90 degrees
    ],
    'Z': [
        [[1, 1, 0], [0, 1, 1]], # 0 degrees
        [[0, 1], [1, 1], [1, 0]] # 90 degrees
    ],
    'J': [
        [[1, 0, 0], [1, 1, 1]], # 0 degrees
        [[1, 1], [1, 0], [1, 0]], # 90 degrees
        [[1, 1, 1], [0, 0, 1]], # 180 degrees
        [[0, 1], [0, 1], [1, 1]] # 270 degrees
    ],
    'L': [
        [[0, 0, 1], [1, 1, 1]], # 0 degrees
        [[1, 0], [1, 0], [1, 1]], # 90 degrees
        [[1, 1, 1], [1, 0, 0]], # 180 degrees
        [[1, 1], [0, 1], [0, 1]] # 270 degrees
    ]
}

# Map tetromino shapes to curses color constants
# These are default curses colors. Actual pair IDs will be defined later.
TETROMINO_COLORS = {
    'I': curses.COLOR_CYAN,
    'O': curses.COLOR_YELLOW,
    'T': curses.COLOR_MAGENTA,
    'S': curses.COLOR_GREEN,
    'Z': curses.COLOR_RED,
    'J': curses.COLOR_BLUE,
    'L': curses.COLOR_WHITE # Using white as a placeholder for orange
}

# Direction vectors for movement (dx, dy)
LEFT = (-1, 0)
RIGHT = (1, 0)
DOWN = (0, 1)

class GameEngine:
    """
    Manages the core logic of the Tetris game, including the game board,
    tetromino generation, movement, rotation, collision detection,
    line clearing, scoring, and game state (level, time, game over).
    """
    def __init__(self, width=10, height=20, start_level=1):
        """
        Initializes the GameEngine with a specified board size and sets up
        the initial game state.

        Args:
            width (int): The width of the game board.
            height (int): The height of the game board.
            start_level (int): The initial level of the game.
        """
        self.width = width
        self.height = height
        # The game board, represented as a 2D list. 0 for empty, 1 for filled block.
        self.board = [[0] * width for _ in range(height)]
        
        # Current falling tetromino and the next one in queue
        self.current_tetromino = None # Will be set by _get_next_tetromino
        self.next_tetrominoes = [] # List of upcoming tetrominoes
        self.held_tetromino = None # Initialize held tetromino
        
        # Game statistics
        self.score = 0
        self.level = start_level
        self.lines_cleared_total = (start_level - 1) * 10 # Adjust total lines cleared for starting level
        self.time_elapsed = 0
        
        # Game state flags
        self.game_over = False
        self.tetromino_bag = []
        self.level_up = False
        self.lock_delay = 0.5
        self.landing_time = None
        self.entry_delay = 0.1
        self.combo_count = 0
        self.last_clear_was_tetris = False
        self.fall_delay = max(0.1, 0.5 - (self.level - 1) * 0.05) # Initial fall delay based on start_level
        self.high_score = self._load_high_score()
        
        # Initialize first tetrominoes
        for _ in range(3): # Populate with 3 next tetrominoes
            self.next_tetrominoes.append(self._generate_random_tetromino())
        self.current_tetromino = self._get_next_tetromino()
        self.calculate_ghost_piece_position()

    def _load_high_score(self):
        """
        Loads the high score from a file.
        """
        try:
            with open("highscore.txt", "r") as f:
                return int(f.read())
        except FileNotFoundError:
            return 0

    def _save_high_score(self):
        """
        Saves the high score to a file.
        """
        with open("highscore.txt", "w") as f:
            f.write(str(self.high_score))

    def hold_tetromino(self):
        """
        Holds the current tetromino.
        """
        if not self.can_hold:
            return

        if self.held_tetromino is None:
            self.held_tetromino = self.current_tetromino
            self.current_tetromino = self._get_next_tetromino()
        else:
            self.held_tetromino, self.current_tetromino = self.current_tetromino, self.held_tetromino
            self.current_tetromino = self.current_tetromino._replace(position=(self.width // 2 - len(SHAPES[self.current_tetromino.shape][0][0]) // 2, 0))

        self.can_hold = False
        self.calculate_ghost_piece_position()

    def calculate_ghost_piece_position(self):
        """
        Calculates the final landing position of the current tetromino.
        """
        if self.current_tetromino is None:
            self.ghost_piece_position = None
            return

        ghost_tetromino = self.current_tetromino
        while not self.check_collision(ghost_tetromino):
            ghost_tetromino = Tetromino(
                shape=ghost_tetromino.shape,
                position=(ghost_tetromino.position[0], ghost_tetromino.position[1] + 1),
                rotation=ghost_tetromino.rotation,
                color_id=ghost_tetromino.color_id
            )
        self.ghost_piece_position = (ghost_tetromino.position[0], ghost_tetromino.position[1] - 1)

    def _generate_random_tetromino(self):
        """
        Generates a new random tetromino.
        """
        if not self.tetromino_bag:
            self.tetromino_bag = list(SHAPES.keys())
            random.shuffle(self.tetromino_bag)

        shape_name = self.tetromino_bag.pop()
        shape_data = SHAPES[shape_name][0] 
        position = (self.width // 2 - len(shape_data[0]) // 2, 0) 
        rotation = 0
        color_id = TETROMINO_COLORS[shape_name]
        
        return Tetromino(shape=shape_name, position=position, rotation=rotation, color_id=color_id)

    def _get_next_tetromino(self):
        """
        Gets the next tetromino from the queue and adds a new one.
        """
        tetromino = self.next_tetrominoes.pop(0)
        self.next_tetrominoes.append(self._generate_random_tetromino())
        return tetromino

    def place_tetromino(self):
        """
        Places the current falling tetromino onto the game board permanently.
        Then clears any completed lines, updates the score and level,
        and generates the next tetromino.
        """
        current_shape_data = SHAPES[self.current_tetromino.shape][self.current_tetromino.rotation]
        for y_offset, row in enumerate(current_shape_data):
            for x_offset, cell in enumerate(row):
                if cell: # If it's a block in the tetromino shape
                    board_x = self.current_tetromino.position[0] + x_offset
                    board_y = self.current_tetromino.position[1] + y_offset
                    # Ensure coordinates are within board boundaries before placing
                    if 0 <= board_y < self.height and 0 <= board_x < self.width:
                        self.board[board_y][board_x] = self.current_tetromino.color_id
        
        lines_cleared = self.clear_lines()

        # Move the next tetromino to become the current one
        self.current_tetromino = self._get_next_tetromino()
        self.can_hold = True
        self.combo_count = 0 # Reset combo
        
        if self.check_collision(self.current_tetromino):
            self.game_over = True
            if self.score > self.high_score:
                self.high_score = self.score
                self._save_high_score()
        
        self.calculate_ghost_piece_position()
        return lines_cleared

    def clear_lines(self):
        """
        Checks for and clears any completed horizontal lines on the board.
        Updates the score and level based on the number of lines cleared.
        """
        cleared_lines_indices = []
        for y in range(self.height):
            if all(self.board[y]):
                cleared_lines_indices.append(y)

        if not cleared_lines_indices:
            self.last_clear_was_tetris = False
            return False

        for y in cleared_lines_indices:
            self.board.pop(y)
            self.board.insert(0, [0] * self.width)

        lines_cleared = len(cleared_lines_indices)
        
        # Scoring
        score_map = {1: 100, 2: 300, 3: 500, 4: 800}
        base_score = score_map.get(lines_cleared, 0)
        
        # Combo bonus
        combo_bonus = 50 * self.combo_count
        self.score += base_score + combo_bonus
        self.combo_count += 1

        # Back-to-back Tetris bonus
        if lines_cleared == 4:
            if self.last_clear_was_tetris:
                self.score += 400 # 50% bonus for back-to-back Tetris
            self.last_clear_was_tetris = True
        else:
            self.last_clear_was_tetris = False

        if lines_cleared > 0:
            self.lines_cleared_total += lines_cleared
            new_level = 1 + (self.lines_cleared_total // 10)
            if new_level > self.level:
                self.level_up = True
            self.level = new_level
            self.fall_delay = max(0.1, 0.5 - (self.level - 1) * 0.05)
        
        self.cleared_lines = cleared_lines_indices
        return True

    def check_collision(self, tetromino):
        """
        Checks if a given tetromino's current position and rotation
        would result in a collision with the board boundaries or
        existing blocks on the board.

        Args:
            tetromino (Tetromino): The tetromino to check for collision.

        Returns:
            bool: True if a collision is detected, False otherwise.
        """
        shape_data = SHAPES[tetromino.shape][tetromino.rotation]
        for y_offset, row in enumerate(shape_data):
            for x_offset, cell in enumerate(row):
                if cell: # Only check for blocks that are part of the tetromino
                    board_x = tetromino.position[0] + x_offset
                    board_y = tetromino.position[1] + y_offset
                    
                    # Check collision with board boundaries
                    if not (0 <= board_x < self.width and 0 <= board_y < self.height):
                        return True
                    
                    # Check collision with existing blocks on the board
                    # Ensure board_y is valid before accessing self.board[board_y]
                    if board_y >= 0 and self.board[board_y][board_x] != 0:
                        return True
        return False

    def rotate_tetromino(self):
        """
        Attempts to rotate the current tetromino clockwise.
        If the rotation causes a collision, it attempts to perform
        a 'wall kick' (shifting horizontally) to resolve the collision.
        """
        if self.current_tetromino is None:
            return

        current_shape_name = self.current_tetromino.shape
        current_rotation_index = self.current_tetromino.rotation
        
        # Calculate the next rotation index
        next_rotation_index = (current_rotation_index + 1) % len(SHAPES[current_shape_name])
        new_tetromino = Tetromino(shape=current_shape_name, position=self.current_tetromino.position, rotation=next_rotation_index, color_id=self.current_tetromino.color_id)
        
        # If no collision after rotation, apply the rotation
        if not self.check_collision(new_tetromino):
            self.current_tetromino = new_tetromino
            self.landing_time = None
        else:
            # Wall kick logic: try to move left/right if rotation causes collision
            # This is a simplified wall kick, more complex rules exist in official Tetris
            for dx in [-1, 1, -2, 2]: # Try small horizontal offsets
                test_position = (self.current_tetromino.position[0] + dx, self.current_tetromino.position[1])
                test_tetromino = Tetromino(shape=current_shape_name, position=test_position, rotation=next_rotation_index, color_id=self.current_tetromino.color_id)
                if not self.check_collision(test_tetromino):
                    self.current_tetromino = test_tetromino # Apply rotation and shift
                    self.landing_time = None
                    break
        self.calculate_ghost_piece_position()

    def move_tetromino(self, direction):
        """
        Attempts to move the current tetromino in the specified direction.

        Args:
            direction (tuple): A tuple (dx, dy) representing the change in
                               x and y coordinates (e.g., LEFT, RIGHT, DOWN).

        Returns:
            bool: True if the move was successful (no collision), False otherwise.
        """
        if self.current_tetromino is None:
            return False

        new_position = (self.current_tetromino.position[0] + direction[0], self.current_tetromino.position[1] + direction[1])
        new_tetromino = Tetromino(shape=self.current_tetromino.shape, position=new_position, rotation=self.current_tetromino.rotation, color_id=self.current_tetromino.color_id)
        
        # If no collision after moving, apply the move
        if not self.check_collision(new_tetromino):
            self.current_tetromino = new_tetromino
            self.landing_time = None
            self.calculate_ghost_piece_position()
            return True
        return False

    def soft_drop(self):
        """
        Attempts to move the current tetromino down one step.
        If it cannot move down (collides), it is placed on the board.
        """
        if self.current_tetromino is None:
            return False
        # If move_tetromino (DOWN) returns False, it means collision, so place it
        if not self.move_tetromino(DOWN):
            if self.place_tetromino():
                return True
        return False

    def hard_drop(self):
        """
        Instantly drops the current tetromino to the lowest possible position
        on the board and then places it.
        """
        if self.current_tetromino is None:
            return
        # Keep moving down until a collision is detected
        while self.move_tetromino(DOWN):
            pass
        if self.place_tetromino():
            return True
        return False

class UserInterface:
    """
    Handles the display of the game board and other UI elements in the console
    using the curses library, and captures user input.
    """
    def __init__(self, game_engine, stdscr, is_test_mode=False):
        """
        Initializes the UserInterface.

        Args:
            game_engine (GameEngine): The game engine instance to interact with.
            stdscr (curses.window): The curses window object for screen manipulation.
            is_test_mode (bool): If True, curses-specific settings are skipped for testing.
        """
        self.game_engine = game_engine
        self.stdscr = stdscr
        
        # Initialize color attributes for both test and non-test modes
        self.color_pair_map = {}
        self.default_pair_id = 0 # Default to 0 (no color) if curses not initialized or in test mode
        self.settled_block_pair_id = 0 # Default to 0
        self.ghost_piece_pair_id = 0 # Default to 0

        # Apply curses settings only if not in test mode
        if not is_test_mode:
            curses.curs_set(0) # Hide cursor to prevent flickering
            self.stdscr.nodelay(1) # Make getch() non-blocking
            # Set a timeout for getch() based on game_engine's fall_delay (converted to milliseconds)
            self.stdscr.timeout(int(self.game_engine.fall_delay * 1000))

            # Initialize colors
            if curses.has_colors():
                curses.start_color()
                self.color_pair_map = {}
                pair_id_counter = 1
                for shape_name, color_const in TETROMINO_COLORS.items():
                    curses.init_pair(pair_id_counter, color_const, curses.COLOR_BLACK)
                    self.color_pair_map[color_const] = pair_id_counter
                    pair_id_counter += 1
                # Define a default color for empty spaces or other UI elements
                curses.init_pair(pair_id_counter, curses.COLOR_WHITE, curses.COLOR_BLACK)
                self.default_pair_id = pair_id_counter
                pair_id_counter += 1
                # Define a color for settled blocks
                curses.init_pair(pair_id_counter, curses.COLOR_WHITE, curses.COLOR_BLACK)
                self.settled_block_pair_id = pair_id_counter
                pair_id_counter += 1
                # Define a color for the ghost piece
                curses.init_pair(pair_id_counter, curses.COLOR_WHITE, curses.COLOR_BLACK)
                self.ghost_piece_pair_id = pair_id_counter

    def draw_board(self):
        """
        Clears the screen and draws the current state of the game board,
        the falling tetromino, score, level, time, next tetromino preview,
        and game over message if applicable, using curses colors.
        """
        max_y, max_x = self.stdscr.getmaxyx()
        
        # Calculate required dimensions
        # Board takes game_engine.height rows and game_engine.width * 2 columns
        # Stats and previews take additional rows below the board
        required_height = self.game_engine.height + 10 # Board height + 1 (spacing) + 4 (stats) + 1 (Next/Hold labels) + 4 (max tetromino height)
        required_width = max(self.game_engine.width * 2, 20) # Board width or max length of info lines

        if max_y < required_height or max_x < required_width:
            self.stdscr.clear()
            self.stdscr.addstr(0, 0, f"Terminal too small! Please resize to at least {required_height}x{required_width}.")
            self.stdscr.addstr(1, 0, f"Current size: {max_y}x{max_x}")
            self.stdscr.refresh()
            return # Skip drawing the board to prevent errors
        
        self.stdscr.clear() # Clear the entire screen
        
        # Draw game board (settled blocks)
        for y in range(self.game_engine.height):
            for x in range(self.game_engine.width):
                block_color_id = self.game_engine.board[y][x]
                if block_color_id != 0:
                    # Get the curses color pair ID from our map
                    pair_id = self.color_pair_map.get(block_color_id, self.default_pair_id)
                    self.stdscr.attron(curses.color_pair(pair_id) | curses.A_DIM)
                    self.stdscr.addstr(y, x * 2, "[]") 
                    self.stdscr.attroff(curses.color_pair(pair_id) | curses.A_DIM)
                else:
                    # Use default color for empty spaces
                    self.stdscr.attron(curses.color_pair(self.default_pair_id))
                    self.stdscr.addstr(y, x * 2, " .") 
                    self.stdscr.attroff(curses.color_pair(self.default_pair_id))
        
        # Draw ghost piece
        if self.game_engine.ghost_piece_position and self.game_engine.current_tetromino:
            shape_data = SHAPES[self.game_engine.current_tetromino.shape][self.game_engine.current_tetromino.rotation]
            self.stdscr.attron(curses.color_pair(self.ghost_piece_pair_id) | curses.A_DIM)
            for y_offset, row in enumerate(shape_data):
                for x_offset, cell in enumerate(row):
                    if cell:
                        board_x = self.game_engine.ghost_piece_position[0] + x_offset
                        board_y = self.game_engine.ghost_piece_position[1] + y_offset
                        if 0 <= board_x < self.game_engine.width and 0 <= board_y < self.game_engine.height:
                            self.stdscr.addstr(board_y, board_x * 2, "::")
            self.stdscr.attroff(curses.color_pair(self.ghost_piece_pair_id) | curses.A_DIM)

        # Draw current falling tetromino
        if self.game_engine.current_tetromino:
            shape_data = SHAPES[self.game_engine.current_tetromino.shape][self.game_engine.current_tetromino.rotation]
            tetromino_color_id = self.game_engine.current_tetromino.color_id
            pair_id = self.color_pair_map.get(tetromino_color_id, self.default_pair_id)
            self.stdscr.attron(curses.color_pair(pair_id))
            for y_offset, row in enumerate(shape_data):
                for x_offset, cell in enumerate(row):
                    if cell: # If it's a block in the tetromino shape
                        board_x = self.game_engine.current_tetromino.position[0] + x_offset
                        board_y = self.game_engine.current_tetromino.position[1] + y_offset
                        # Only draw if within visible board boundaries
                        if 0 <= board_x < self.game_engine.width and 0 <= board_y < self.game_engine.height:
                            self.stdscr.addstr(board_y, board_x * 2, "[]")
            self.stdscr.attroff(curses.color_pair(pair_id))
                            
        # Display game information: score, level, time, next tetromino
        # Use default color for text
        self.stdscr.attron(curses.color_pair(self.default_pair_id))
        self.stdscr.addstr(self.game_engine.height + 1, 0, f"Score: {self.game_engine.score}")
        self.stdscr.addstr(self.game_engine.height + 2, 0, f"Level: {self.game_engine.level}")
        self.stdscr.addstr(self.game_engine.height + 3, 0, f"Time: {self.game_engine.time_elapsed}s")
        self.stdscr.addstr(self.game_engine.height + 4, 0, f"High Score: {self.game_engine.high_score}")
        self.stdscr.addstr(self.game_engine.height + 5, 0, "Next:")
        self.stdscr.addstr(self.game_engine.height + 5, 10, "Hold:")
        self.stdscr.attroff(curses.color_pair(self.default_pair_id))
        
        # Draw next tetromino preview
        if self.game_engine.next_tetrominoes:
            next_shape_data = SHAPES[self.game_engine.next_tetrominoes[0].shape][self.game_engine.next_tetrominoes[0].rotation]
            next_tetromino_color_id = self.game_engine.next_tetrominoes[0].color_id
            pair_id = self.color_pair_map.get(next_tetromino_color_id, self.default_pair_id)
            self.stdscr.attron(curses.color_pair(pair_id))
            for y_offset, row in enumerate(next_shape_data):
                for x_offset, cell in enumerate(row):
                    if cell:
                        # Position the next tetromino preview below the "Next:" label
                        self.stdscr.addstr(self.game_engine.height + 6 + y_offset, x_offset * 2, "[]")
            self.stdscr.attroff(curses.color_pair(pair_id))

        # Draw held tetromino preview
        if self.game_engine.held_tetromino:
            held_shape_data = SHAPES[self.game_engine.held_tetromino.shape][self.game_engine.held_tetromino.rotation]
            held_tetromino_color_id = self.game_engine.held_tetromino.color_id
            pair_id = self.color_pair_map.get(held_tetromino_color_id, self.default_pair_id)
            self.stdscr.attron(curses.color_pair(pair_id))
            for y_offset, row in enumerate(held_shape_data):
                for x_offset, cell in enumerate(row):
                    if cell:
                        # Position the held tetromino preview below the "Hold:" label
                        self.stdscr.addstr(self.game_engine.height + 6 + y_offset, 10 + x_offset * 2, "[]")
            self.stdscr.attroff(curses.color_pair(pair_id))
                        
        # Display "GAME OVER!" message if the game has ended
        if self.game_engine.game_over:
            self.stdscr.attron(curses.color_pair(self.default_pair_id) | curses.A_BOLD) # Bold for game over
            self.stdscr.addstr(self.game_engine.height // 2, self.game_engine.width - 5, "GAME OVER!")
            self.stdscr.addstr(self.game_engine.height // 2 + 1, self.game_engine.width - 8, "Press 'r' to restart")
            self.stdscr.attroff(curses.color_pair(self.default_pair_id) | curses.A_BOLD)

        self.stdscr.refresh() # Update the physical screen

    def draw_help_screen(self):
        """
        Draws the help screen with controls and instructions.
        """
        max_y, max_x = self.stdscr.getmaxyx()
        
        controls = [
            "Left Arrow: Move Left",
            "Right Arrow: Move Right",
            "Z: Rotate", # Updated control
            "Down Arrow: Soft Drop",
            "Spacebar: Hard Drop",
            "C: Hold Piece",
            "H: Toggle Help Screen",
            "Q: Quit Game",
            "R (Game Over): Restart Game"
        ]
        
        required_height = len(controls) + 5 # Title + spacing + controls + spacing + instruction
        required_width = max(len(c) for c in controls) + 5 # Longest control + some padding
        required_width = max(required_width, len("Press 'H' to return to game, or 'Q' to quit.") + 5)

        if max_y < required_height or max_x < required_width:
            self.stdscr.clear()
            self.stdscr.addstr(0, 0, f"Terminal too small for help screen! Please resize to at least {required_height}x{required_width}.")
            self.stdscr.addstr(1, 0, f"Current size: {max_y}x{max_x}")
            self.stdscr.refresh()
            return # Skip drawing the help screen to prevent errors

        self.stdscr.clear()
        self.stdscr.attron(curses.color_pair(self.default_pair_id) | curses.A_BOLD)
        self.stdscr.addstr(0, 0, "Tetris Controls:")
        self.stdscr.attroff(curses.color_pair(self.default_pair_id) | curses.A_BOLD)

        controls = [
            "Left Arrow: Move Left",
            "Right Arrow: Move Right",
            "Z: Rotate", # Updated control
            "Down Arrow: Soft Drop",
            "Spacebar: Hard Drop",
            "C: Hold Piece",
            "H: Toggle Help Screen",
            "Q: Quit Game",
            "R (Game Over): Restart Game"
        ]

        for i, control in enumerate(controls):
            self.stdscr.addstr(2 + i, 0, control)
        
        self.stdscr.addstr(len(controls) + 4, 0, "Press 'H' to return to game, or 'Q' to quit.")
        self.stdscr.refresh()

    def draw_line_clear_animation(self):
        """
        Draws the line clear animation.
        """
        for y in self.game_engine.cleared_lines:
            for x in range(self.game_engine.width):
                self.stdscr.addstr(y, x * 2, "##")
        self.stdscr.refresh()
        time.sleep(0.1)

        # The lines are already cleared in the game engine,
        # so we just need to reset the cleared_lines list here.
        self.game_engine.cleared_lines = []

    def draw_level_up_animation(self):
        """
        Draws the level up animation.
        """
        self.stdscr.attron(curses.color_pair(self.default_pair_id) | curses.A_BOLD)
        self.stdscr.addstr(self.game_engine.height // 2, self.game_engine.width - 5, "LEVEL UP!")
        self.stdscr.refresh()
        time.sleep(1)
        self.game_engine.level_up = False

    def get_input(self):
        """
        Captures a single character input from the user.
        Returns -1 if no input is available (due to nodelay setting).

        Returns:
            int: The ASCII value of the key pressed, or -1 if no key was pressed.
        """
        try:
            key = self.stdscr.getch()
            return key
        except:
            return -1 # No input available

def main(stdscr):
    # Prompt for starting level
    start_level_input = ""
    while not start_level_input.isdigit() or not (1 <= int(start_level_input) <= 10):
        stdscr.clear()
        stdscr.addstr(0, 0, "Enter starting level (1-10): ")
        stdscr.refresh()
        curses.echo() # Enable echoing of characters
        start_level_input = stdscr.getstr(0, 29, 2).decode('utf-8') # Read up to 2 characters
        curses.noecho() # Disable echoing
    
    start_level = int(start_level_input)

    game_engine = GameEngine(start_level=start_level)
    ui = UserInterface(game_engine, stdscr)
    start_time = time.time()

    # Define game states
    PLAYING = 0
    GAME_OVER = 1
    HELP_SCREEN = 2
    LINE_CLEAR_ANIMATION = 3
    current_game_state = PLAYING # Initial state

    while True:
        if current_game_state == PLAYING:
            if game_engine.game_over:
                current_game_state = GAME_OVER
                continue

            current_time = time.time()
            game_engine.time_elapsed = int(current_time - start_time)

            if game_engine.landing_time and time.time() - game_engine.landing_time > game_engine.lock_delay:
                if game_engine.place_tetromino():
                    current_game_state = LINE_CLEAR_ANIMATION
                game_engine.landing_time = None

            key = ui.get_input()

            if key == curses.KEY_LEFT:
                game_engine.move_tetromino(LEFT)
            elif key == curses.KEY_RIGHT:
                game_engine.move_tetromino(RIGHT)
            elif key == ord('z'): # Rotate with 'Z' key
                game_engine.rotate_tetromino()
            elif key == curses.KEY_DOWN: # Soft drop
                if game_engine.soft_drop():
                    current_game_state = LINE_CLEAR_ANIMATION
            elif key == ord(' '): # Hard drop
                if game_engine.hard_drop():
                    current_game_state = LINE_CLEAR_ANIMATION
            elif key == ord('c'): # Hold piece
                game_engine.hold_tetromino()
            elif key == ord('q'): # Quit
                break
            elif key == ord('h'): # Toggle help screen
                current_game_state = HELP_SCREEN
                
            game_engine.soft_drop() # Tetromino falls automatically

            ui.draw_board()

        elif current_game_state == GAME_OVER:
            key = ui.get_input()
            if key == ord('r'):
                game_engine = GameEngine() # Reset game
                ui.game_engine = game_engine # Update UI's reference to new engine
                start_time = time.time() # Reset timer
                current_game_state = PLAYING # Go back to playing
            elif key == ord('q'): # Quit
                break
            elif key == ord('h'): # Toggle help screen
                current_game_state = HELP_SCREEN
            ui.draw_board() # Still draw board to show game over message

        elif current_game_state == HELP_SCREEN:
            key = ui.get_input()
            if key == ord('h') or key == ord('q'): # Exit help screen or quit
                current_game_state = PLAYING # Go back to playing
            ui.draw_help_screen() # Draw the help screen

        elif current_game_state == LINE_CLEAR_ANIMATION:
            ui.draw_line_clear_animation()
            if game_engine.level_up:
                ui.draw_level_up_animation()
                # Update the curses timeout when level changes
                stdscr.timeout(int(game_engine.fall_delay * 1000))
            current_game_state = PLAYING


if __name__ == '__main__':
    curses.wrapper(main)
