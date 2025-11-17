import unittest
from unittest.mock import patch # Import patch
from tetris_game import GameEngine, UserInterface, LEFT, RIGHT, DOWN, SHAPES, Tetromino, TETROMINO_COLORS
import curses

# Mock curses.color_pair globally for all tests
# This mock will simply return the pair_id it receives,
# as we don't need actual curses color functionality in tests.
def mock_curses_color_pair(pair_id):
    return pair_id

# Patch curses.color_pair before any tests run
curses.color_pair = mock_curses_color_pair

class TestGameEngine(unittest.TestCase):
    def setUp(self):
        self.engine = GameEngine()
        
    def test_new_tetromino_generation(self):
        tetromino = self.engine._get_next_tetromino()
        self.assertIsNotNone(tetromino)
        self.assertIn(tetromino.shape, SHAPES.keys())
        self.assertEqual(tetromino.rotation, 0) # Should start with 0 rotation
        # Assert color_id is set
        self.assertIn(tetromino.color_id, TETROMINO_COLORS.values())
        
    def test_place_tetromino(self):
        # Manually set a simple tetromino to place
        shape_name = 'O'
        self.engine.current_tetromino = Tetromino(shape=shape_name, position=(0, 0), rotation=0, color_id=TETROMINO_COLORS[shape_name])
        self.engine.place_tetromino()
        
        # Check if the blocks are placed on the board with correct color_id
        # 'O' shape is 2x2
        expected_color = TETROMINO_COLORS[shape_name]
        self.assertEqual(self.engine.board[0][0], expected_color)
        self.assertEqual(self.engine.board[0][1], expected_color)
        self.assertEqual(self.engine.board[1][0], expected_color)
        self.assertEqual(self.engine.board[1][1], expected_color)
        
        # Ensure a new tetromino is generated after placing
        self.assertIsNotNone(self.engine.current_tetromino)
        self.assertIsNotNone(self.engine.next_tetrominoes[0])
        
    def test_clear_lines(self):
        # Fill a line to be cleared with a specific color
        test_color = TETROMINO_COLORS['I']
        for x in range(self.engine.width):
            self.engine.board[self.engine.height - 1][x] = test_color
        
        initial_score = self.engine.score
        self.engine.clear_lines()
        
        # Check if the line is cleared (top row should be empty, i.e., 0)
        self.assertTrue(all(cell == 0 for cell in self.engine.board[self.engine.height - 1])) # Check the cleared line
        
        # Check if score is updated (1 line cleared = 100 points)
        self.assertEqual(self.engine.score, initial_score + 100)
        
        # Test multiple line clear
        self.setUp() # Reset the engine state for the second scenario
        test_color = TETROMINO_COLORS['I'] # Re-define test_color after setUp
        for y in range(self.engine.height - 3, self.engine.height):
            for x in range(self.engine.width):
                self.engine.board[y][x] = test_color
        
        initial_score = self.engine.score
        self.engine.clear_lines()
        # 3 lines cleared = 500 points
        self.assertEqual(self.engine.score, initial_score + 500)

    def test_check_collision_boundaries(self):
        # Test collision with left boundary
        tetromino_i = Tetromino(shape='I', position=(-1, 0), rotation=0, color_id=TETROMINO_COLORS['I']) # Outside left
        self.assertTrue(self.engine.check_collision(tetromino_i))
        
        # Test collision with right boundary
        tetromino_i = Tetromino(shape='I', position=(self.engine.width - 3, 0), rotation=0, color_id=TETROMINO_COLORS['I']) # 'I' is 4 wide, so width-4 is max valid x
        self.assertTrue(self.engine.check_collision(tetromino_i))
        
        # Test collision with bottom boundary
        tetromino_i = Tetromino(shape='I', position=(0, self.engine.height), rotation=0, color_id=TETROMINO_COLORS['I']) # Outside bottom
        self.assertTrue(self.engine.check_collision(tetromino_i))
        
        # Test no collision
        tetromino_i = Tetromino(shape='I', position=(0, 0), rotation=0, color_id=TETROMINO_COLORS['I'])
        self.assertFalse(self.engine.check_collision(tetromino_i))

    def test_check_collision_with_blocks(self):
        # Place a block on the board with a color
        self.engine.board[0][0] = TETROMINO_COLORS['O']
        
        # Test collision with existing block
        tetromino_o = Tetromino(shape='O', position=(0, 0), rotation=0, color_id=TETROMINO_COLORS['O'])
        self.assertTrue(self.engine.check_collision(tetromino_o))
        
        # Test no collision
        tetromino_o = Tetromino(shape='O', position=(2, 2), rotation=0, color_id=TETROMINO_COLORS['O'])
        self.assertFalse(self.engine.check_collision(tetromino_o))

    def test_rotate_tetromino(self):
        # Test 'O' tetromino (should not rotate)
        shape_name_o = 'O'
        self.engine.current_tetromino = Tetromino(shape=shape_name_o, position=(0, 0), rotation=0, color_id=TETROMINO_COLORS[shape_name_o])
        initial_rotation = self.engine.current_tetromino.rotation
        self.engine.rotate_tetromino()
        self.assertEqual(self.engine.current_tetromino.rotation, initial_rotation)
        
        # Test 'I' tetromino rotation
        shape_name_i = 'I'
        self.engine.current_tetromino = Tetromino(shape=shape_name_i, position=(5, 5), rotation=0, color_id=TETROMINO_COLORS[shape_name_i])
        self.engine.rotate_tetromino()
        self.assertEqual(self.engine.current_tetromino.rotation, 1) # Should rotate to 90 degrees
        self.engine.rotate_tetromino()
        self.assertEqual(self.engine.current_tetromino.rotation, 0) # Should rotate back to 0 degrees

    def test_rotate_tetromino_collision(self):
        # Place blocks to block rotation, forcing a wall kick
        self.engine.board[6][5] = TETROMINO_COLORS['S'] # Obstacle at row 6, column 5
        self.engine.board[7][5] = TETROMINO_COLORS['S'] # Another obstacle to ensure no wall kick can easily resolve
        
        # 'I' tetromino at (5,5) rotation 0
        shape_name_i = 'I'
        self.engine.current_tetromino = Tetromino(shape=shape_name_i, position=(5, 5), rotation=0, color_id=TETROMINO_COLORS[shape_name_i])
        initial_position = self.engine.current_tetromino.position
        initial_rotation = self.engine.current_tetromino.rotation

        self.engine.rotate_tetromino()
        
        # Assert that rotation occurred and position shifted due to wall kick
        self.assertEqual(self.engine.current_tetromino.rotation, (initial_rotation + 1) % len(SHAPES['I'])) # Should rotate
        self.assertEqual(self.engine.current_tetromino.position[0], initial_position[0] - 1) # Should shift left by 1 (due to dx=-1 wall kick)
        self.assertEqual(self.engine.current_tetromino.position[1], initial_position[1]) # Y position should remain same
        
    def test_move_tetromino(self):
        shape_name_i = 'I'
        self.engine.current_tetromino = Tetromino(shape=shape_name_i, position=(5, 5), rotation=0, color_id=TETROMINO_COLORS[shape_name_i])
        
        # Move left
        self.engine.move_tetromino(LEFT)
        self.assertEqual(self.engine.current_tetromino.position, (4, 5))
        
        # Move right
        self.engine.move_tetromino(RIGHT)
        self.assertEqual(self.engine.current_tetromino.position, (5, 5)) # Moved from 4 to 5
        
        # Move down
        self.engine.move_tetromino(DOWN)
        self.assertEqual(self.engine.current_tetromino.position, (5, 6))

    def test_move_tetromino_collision(self):
        # Place a block to block movement
        self.engine.board[5][4] = TETROMINO_COLORS['J']
        
        shape_name_i = 'I'
        self.engine.current_tetromino = Tetromino(shape=shape_name_i, position=(5, 5), rotation=0, color_id=TETROMINO_COLORS[shape_name_i])
        initial_position = self.engine.current_tetromino.position
        
        # Try to move left into the block
        self.engine.move_tetromino(LEFT)
        self.assertEqual(self.engine.current_tetromino.position, initial_position) # Should not move

    def test_hard_drop(self):
        # Set a specific tetromino for predictable testing
        shape_name_i = 'I'
        initial_tetromino = Tetromino(shape=shape_name_i, position=(5, 0), rotation=0, color_id=TETROMINO_COLORS[shape_name_i])
        self.engine.current_tetromino = initial_tetromino
        
        self.engine.hard_drop()
        
        # Assert that the previous tetromino is now part of the board with its color
        # 'I' tetromino (horizontal) at (5,0) will drop to (5, height-1)
        # Blocks will be at (5, height-1), (6, height-1), (7, height-1), (8, height-1)
        for x_offset in range(4):
            self.assertEqual(self.engine.board[self.engine.height - 1][5 + x_offset], TETROMINO_COLORS[shape_name_i])
            
        # Assert that a new tetromino has been generated (unless game over)
        if not self.engine.game_over:
            self.assertIsNotNone(self.engine.current_tetromino)
            self.assertIsNot(self.engine.current_tetromino, initial_tetromino) # Assert it's a new object

    def test_soft_drop(self):
        # Set a specific tetromino for predictable testing
        shape_name_i = 'I'
        initial_tetromino = Tetromino(shape=shape_name_i, position=(5, self.engine.height - 1), rotation=0, color_id=TETROMINO_COLORS[shape_name_i])
        self.engine.current_tetromino = initial_tetromino
        
        self.engine.soft_drop() # This should cause placement
        
        # Assert that the previous tetromino is now part of the board with its color
        # 'I' tetromino (horizontal) at (5, height-1)
        # Blocks will be at (5, height-1), (6, height-1), (7, height-1), (8, height-1)
        for x_offset in range(4):
            self.assertEqual(self.engine.board[self.engine.height - 1][5 + x_offset], TETROMINO_COLORS[shape_name_i])
            
        # Assert that a new tetromino has been generated (unless game over)
        if not self.engine.game_over:
            self.assertIsNotNone(self.engine.current_tetromino)
            self.assertIsNot(self.engine.current_tetromino, initial_tetromino) # Assert it's a new object

    def test_game_over_on_new_tetromino(self):
        # Fill the top center of the board to ensure a new tetromino immediately collides
        test_color = TETROMINO_COLORS['T']
        # Fill the area where a new tetromino would spawn (top 4 rows, center columns)
        for y in range(4): # Max height of a tetromino is 4
            for x_offset in range(4): # Max width of a tetromino is 4
                board_x = self.engine.width // 2 - 2 + x_offset # Center 4 columns
                if 0 <= board_x < self.engine.width:
                    self.engine.board[y][board_x] = test_color
        
        # Place a piece that lands without clearing lines, to trigger new tetromino generation
        self.engine.current_tetromino = Tetromino(shape='O', position=(0, self.engine.height - 1), rotation=0, color_id=TETROMINO_COLORS['O'])
        self.engine.place_tetromino()
        
        self.assertTrue(self.engine.game_over)

    def test_game_over_on_new_tetromino_full_board(self):
        # Fill the top center of the board to ensure a new tetromino immediately collides
        test_color = TETROMINO_COLORS['L']
        # Fill the area where a new tetromino would spawn (top 4 rows, center columns)
        for y in range(4): # Max height of a tetromino is 4
            for x_offset in range(4): # Max width of a tetromino is 4
                board_x = self.engine.width // 2 - 2 + x_offset # Center 4 columns
                if 0 <= board_x < self.engine.width:
                    self.engine.board[y][board_x] = test_color
        
        # Place a piece that lands without clearing lines, to trigger new tetromino generation
        self.engine.current_tetromino = Tetromino(shape='O', position=(0, self.engine.height - 1), rotation=0, color_id=TETROMINO_COLORS['O'])
        self.engine.place_tetromino()
        
        self.assertTrue(self.engine.game_over)

    def test_level_increment(self):
        initial_level = self.engine.level
        test_color = TETROMINO_COLORS['S']
        
        # Simulate clearing 10 lines to increment level by 1
        for _ in range(10):
            for x in range(self.engine.width):
                self.engine.board[self.engine.height - 1][x] = test_color
            self.engine.clear_lines()
            
        self.assertEqual(self.engine.level, initial_level + 1)
        
        # Simulate clearing another 10 lines
        for _ in range(10):
            for x in range(self.engine.width):
                self.engine.board[self.engine.height - 1][x] = test_color
            self.engine.clear_lines()
            
        self.assertEqual(self.engine.level, initial_level + 2)

    def test_rotate_tetromino_wall_kick(self):
        # Set up a 'T' tetromino near the right wall
        initial_x = self.engine.width - 3
        shape_name_t = 'T'
        self.engine.current_tetromino = Tetromino(shape=shape_name_t, position=(initial_x, 0), rotation=0, color_id=TETROMINO_COLORS[shape_name_t])
        
        # Place an obstacle to block direct rotation
        # The rotated 'T' at (initial_x, 0) would have a block at (initial_x + 1, 1)
        # which is (self.engine.width - 3 + 1, 1) = (self.engine.width - 2, 1)
        # So, place obstacle at board[1][self.engine.width - 2]
        self.engine.board[1][self.engine.width - 2] = TETROMINO_COLORS['J']
        
        # Perform rotation
        self.engine.rotate_tetromino()
        
        # Assert that rotation occurred and position shifted due to wall kick
        self.assertEqual(self.engine.current_tetromino.rotation, 1) # Should rotate to 90 degrees
        self.assertEqual(self.engine.current_tetromino.position[0], initial_x - 1) # Should shift left by 1
        self.assertEqual(self.engine.current_tetromino.position[1], 0) # Y position should remain same


# --- Phase 1: Essential UX & Visual Clarity Tests ---
# Test cases for FFR-2: Improved Block Appearance (curses Colors)
# Test cases for FFR-5: Ghost Piece
# Test cases for FFR-6: Hold Piece
# Test cases for FFR-20: In-Game Help/Controls Screen

# --- Phase 2: Core Gameplay Polish & Feedback Tests ---
# Test cases for FFR-1: Line Clear Animation
# Test cases for FFR-11: Level Up Visual Feedback
# Test cases for FFR-13: Tetromino Bag System
# Test cases for FFR-18: Lock Delay
# Test cases for FFR-19: Entry Delay

# --- Phase 3: Progression & Replayability Tests ---
# Test cases for FFR-4: High Score System (Local Persistent)
# Test cases for FFR-9: Dynamic Fall Speed
# Test cases for FFR-7/FFR-15: Adjustable Starting Difficulty
# Test cases for FFR-16: Enhanced Next Piece Preview (Multiple Pieces)

# --- Phase 4: Advanced Gameplay & Polish Tests ---
# Test cases for FFR-8: Advanced Scoring (T-Spins, Combos)
# Test cases for FFR-10: Level Progression Triggers (Multiple)
# Test cases for FFR-14: Next Level Progress Indicator
# Test cases for FFR-30: Main Menu
# Test cases for FFR-31: Pause Functionality


class MockStdscr:
    def __init__(self):
        self._screen = []
        self.height = 30
        self.width = 80
        self.attrs = [] # To capture attributes
        
    def getmaxyx(self):
        return self.height, self.width

    def clear(self):
        self._screen = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        self.attrs = []

    def addstr(self, y, x, text, attr=0): # Add attr parameter
        if 0 <= y < self.height and 0 <= x < self.width:
            for i, char in enumerate(text):
                if x + i < self.width:
                    self._screen[y][x + i] = char
                    self.attrs.append((y, x + i, attr)) # Capture attribute

    def refresh(self):
        pass # No actual refresh in mock

    def nodelay(self, arg):
        pass

    def timeout(self, arg):
        pass

    def getch(self):
        return -1 # No input by default

    def attron(self, attr):
        # In a real curses app, this would set the current drawing attribute.
        # For mock, we can just store it or ignore it if not testing attribute state.
        # For now, we'll just pass.
        self.current_attr = attr # Store the current attribute

    def attroff(self, attr):
        # Same as attron
        self.current_attr = 0 # Reset attribute

class TestUserInterface(unittest.TestCase):
    def setUp(self):
        self.engine = GameEngine()
        self.mock_stdscr = MockStdscr()
        self.ui = UserInterface(self.engine, self.mock_stdscr, is_test_mode=True)
        
    def test_draw_board_empty(self):
        self.ui.draw_board()
        # Check if the board is drawn with empty cells
        # Each cell is " ." so 10 columns * 2 chars = 20 chars per row
        # 20 rows * 20 chars = 400 chars for the board part
        # Plus score and next tetromino lines
        
        # A simple check: ensure the top-left is an empty cell representation
        self.assertEqual(self.mock_stdscr._screen[0][0], ' ')
        self.assertEqual(self.mock_stdscr._screen[0][1], '.')

    def test_draw_board_with_tetromino(self):
        shape_name = 'O'
        self.engine.current_tetromino = Tetromino(shape=shape_name, position=(0, 0), rotation=0, color_id=TETROMINO_COLORS[shape_name])
        self.ui.draw_board()
        
        # Check if the tetromino is drawn
        self.assertEqual(self.mock_stdscr._screen[0][0], '[')
        self.assertEqual(self.mock_stdscr._screen[0][1], ']')
        self.assertEqual(self.mock_stdscr._screen[0][2], '[')
        self.assertEqual(self.mock_stdscr._screen[0][3], ']')
        
        self.assertEqual(self.mock_stdscr._screen[1][0], '[')
        self.assertEqual(self.mock_stdscr._screen[1][1], ']')
        self.assertEqual(self.mock_stdscr._screen[1][2], '[')
        self.assertEqual(self.mock_stdscr._screen[1][3], ']')

    def test_draw_game_over(self):
        self.engine.game_over = True
        self.ui.draw_board()
        
        # Check for "GAME OVER!" message
        game_over_message = "GAME OVER!"
        message_y = self.engine.height // 2
        message_x = self.engine.width - 5 # This positioning might need adjustment based on actual UI
        
        # Find the start of the message in the mock screen
        found = False
        for y in range(self.mock_stdscr.height):
            screen_row_str = "".join(self.mock_stdscr._screen[y])
            if game_over_message in screen_row_str:
                found = True
                break
        self.assertTrue(found, f"'{game_over_message}' not found on screen.")

    def test_draw_level_and_time(self):
        self.engine.level = 5
        self.engine.time_elapsed = 123
        self.ui.draw_board()
        
        level_message = f"Level: {self.engine.level}"
        time_message = f"Time: {self.engine.time_elapsed}s"
        
        # Check for Level message
        found_level = False
        for y in range(self.mock_stdscr.height):
            screen_row_str = "".join(self.mock_stdscr._screen[y])
            if level_message in screen_row_str:
                found_level = True
                break
        self.assertTrue(found_level, f"'{level_message}' not found on screen.")

        # Check for Time message
        found_time = False
        for y in range(self.mock_stdscr.height):
            screen_row_str = "".join(self.mock_stdscr._screen[y])
            if time_message in screen_row_str:
                found_time = True
                break
        self.assertTrue(found_time, f"'{time_message}' not found on screen.")

if __name__ == '__main__':
    unittest.main()