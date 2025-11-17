# Text-based Tetris Game

## 1. Introduction
A classic Tetris game implemented as a text-based console application using Python and the `curses` library. The objective is to manipulate falling tetrominoes to create horizontal lines of blocks without gaps. Clearing lines awards points, and the game ends when the stack of blocks reaches the top of the playing field.

## 2. Features
-   **Core Tetris Mechanics:** Smooth movement (left, right, soft drop, hard drop), rotation, and line clearing.
-   **Collision Detection:** Robust collision detection with board boundaries, existing blocks, and wall kick logic for rotations.
-   **Score Tracking:** Points awarded for clearing lines.
-   **Level Progression:** Game level increases for every 10 lines cleared.
-   **Game Over:** Detects when new tetrominoes cannot enter the board, displays a "Game Over!" message, and offers a restart option.
-   **Next Tetromino Preview:** Displays the next falling tetromino.
-   **Automatic Fall Speed Adjustment:** The block falling speed automatically adjusts with the game level.
-   **Hold Piece:** Allows players to store and swap a tetromino.
-   **Improved Block Appearance with Colors:** Tetrominoes and settled blocks are displayed with distinct colors.
-   **In-Game Help/Controls Screen:** Provides an accessible screen detailing controls and basic game rules.
-   **Game Timer:** Tracks and displays the elapsed game time.

## 3. How to Play

### Prerequisites
-   Python 3.x
-   `windows-curses` package (for Windows users): `pip install windows-curses`

### Running the Game
1.  Open a terminal or command prompt.
2.  Navigate to the project directory.
3.  Execute the game:
    ```bash
    python tetris_game.py
    ```

### Controls
-   **Left Arrow / 'a'**: Move tetromino left
-   **Right Arrow / 'd'**: Move tetromino right
-   **'Z'**: Rotate tetromino clockwise
-   **Down Arrow / 's'**: Soft drop (move faster)
-   **Spacebar**: Hard drop (instantly drop to bottom)
-   **'C'**: Hold piece
-   **'H'**: Toggle Help Screen
-   **'r'**: Restart game (when game over)
-   **'q'**: Quit game

## 4. How to Run Tests

### Running Unit Tests
1.  Open a terminal or command prompt.
2.  Navigate to the project directory.
3.  Execute the test suite:
    ```bash
    python -m unittest test_tetris_game.py
    ```
    All tests should pass, indicating the core game logic and UI rendering are functioning as expected.

## 5. Development Status
The project is in a stable and functional state, with all core mechanics implemented and thoroughly tested.

**Completed Milestones:**
-   **Comprehensive Test Suite:** Expanded unit tests covering all tetromino rotations, edge cases, multiple line clears, and game over conditions. All tests are passing.
-   **Refined Collision Detection:** Implemented robust collision detection logic, including wall kicks for rotations, ensuring accurate and fair gameplay.
-   **Enhanced Game Over Handling:** A clear "Game Over!" message is displayed, and players can easily restart the game.
-   **Improved User Interface:** The UI now displays the current score, game level, and elapsed time, alongside the next tetromino preview.
-   **Automatic Fall Speed Adjustment:** The block falling speed automatically adjusts with the game level.
-   **Hold Piece:** Allows players to store and swap a tetromino.
-   **Improved Block Appearance with Colors:** Tetrominoes and settled blocks are displayed with distinct colors.
-   **In-Game Help/Controls Screen:** Provides an accessible screen detailing controls and basic game rules.
-   **Code Readability & Maintainability:** The codebase has been thoroughly commented to improve understanding and facilitate future development.

## 6. Future Enhancements

These enhancements are planned to be implemented in phases, ensuring a runnable and testable design at each stage.

#### Phase 1: Essential UX & Visual Clarity
-   **Improved Block Appearance (Implemented):** Enhance visual distinction of tetrominoes and settled blocks (e.g., `curses` colors, varied ASCII characters).
-   **Ghost Piece:** Display a translucent outline showing where the current tetromino will land.
-   **Hold Piece Feature (Implemented):** Allow players to store one tetromino for later use.
-   **In-Game Help/Controls Screen (Implemented):** Provide an accessible screen detailing controls and basic game rules.

#### Phase 2: Core Gameplay Polish & Feedback
-   **Line Clear Animation:** Implement more visual effects for line clears.
-   **Level Up Visual Feedback:** Provide distinct visual (e.g., screen flash, "LEVEL UP!" message) upon level advancement.
-   **Tetromino Bag System:** Introduce a "7-bag" system for tetromino generation to ensure a fair and predictable distribution of pieces.
-   **Lock Delay:** Introduce a short delay after a tetromino lands before it locks into place, allowing for final adjustments.
-   **Entry Delay:** Implement a short pause when a new piece spawns, giving players time to assess.

#### Phase 3: Progression & Replayability
-   **High Score Tracking:** Implement a system to save and display high scores.
-   **Dynamic Fall Speed (Implemented):** Implement progressive increase in tetromino fall speed with each level.
-   **Adjustable Starting Difficulty:** Allow players to choose a lower starting level or speed, influencing initial game parameters.
-   **Enhanced Next Piece Preview:** Display multiple upcoming tetrominoes.

#### Phase 4: Advanced Gameplay & Polish
-   **Sophisticated Scoring System:** Develop a more complex scoring system that rewards combos, T-spins, and higher-level play.
-   **Level Progression Triggers:** Explore multiple level progression triggers (e.g., score milestones, time elapsed).
-   **Next Level Progress Indicator:** Display a visual indicator (e.g., progress bar) showing the player's progress towards the next level.
-   **Main Menu:** Implement a comprehensive main menu with options for starting the game, viewing high scores, accessing help, configuring settings, and quitting.
-   **Pause Functionality:** Allow players to pause and resume the game at any time.

## 7. Development Roadmap: Iterative & Runnable Design for Validation

The development will proceed in distinct phases, with each phase culminating in a runnable, testable version of the game. This ensures continuous validation and allows for early feedback.

**Phase 0: Current Baseline (Already Achieved)**
*   **Features:** Core Tetris mechanics (movement, rotation, line clear, score, level, timer, next piece, game over, restart). Robust collision detection with basic wall kick. Comprehensive unit tests.
*   **Deliverable:** Current `tetris_game.py` (runnable).
*   **Validation:** All existing unit tests pass. Manual playtesting confirms core functionality.

**Phase 1: Essential UX & Visual Clarity**
*   **Target Features:**
    *   Improved Block Appearance (`curses` Colors) - Implemented
    *   Ghost Piece
    *   Hold Piece Feature - Implemented
    *   In-Game Help/Controls Screen - Implemented
*   **Deliverable:** A runnable `tetris_game.py` with enhanced visuals, ghost piece, hold piece, and an in-game help screen.
*   **Validation Method:**
    *   **Unit Tests:** New tests for ghost piece calculation, hold piece logic (swapping, restrictions), and help screen display.
    *   **Manual Playtesting:** Verify visual clarity of colors, correct ghost piece behavior, functional hold piece, and accessible/readable help screen.
    *   **Code Review:** Ensure color implementation is consistent and maintainable.

**Phase 2: Core Gameplay Polish & Feedback**
*   **Target Features:**
    *   Line Clear Animation
    *   Level Up Visual Feedback
    *   Tetromino Bag System
    *   Lock Delay
    *   Entry Delay
*   **Deliverable:** A runnable `tetris_game.py` with improved visual feedback for line clears and level ups, fairer piece generation, and more forgiving piece placement mechanics.
*   **Validation Method:**
    *   **Unit Tests:** New tests for bag system (ensuring all 7 pieces appear in a cycle), lock delay timing, and entry delay timing.
    *   **Manual Playtesting:** Observe line clear animations, level up visuals, verify bag system behavior, and confirm lock/entry delays feel natural and responsive.
    *   **Code Review:** Ensure timing mechanisms are robust and animations are non-blocking.

**Phase 3: Progression & Replayability**
*   **Target Features:**
    *   High Score Tracking
    *   Dynamic Fall Speed - Implemented
    *   Adjustable Starting Difficulty
    *   Enhanced Next Piece Preview (Multiple Pieces)
*   **Deliverable:** A runnable `tetris_game.py` with a functional local high score system, dynamic difficulty scaling, adjustable starting difficulty, and an enhanced next piece preview.
*   **Validation Method:**
    *   **Unit Tests:** New tests for high score saving/loading, dynamic fall speed calculation, and next piece queue management.
    *   **Manual Playtesting:** Verify high scores are saved and displayed correctly. Test different starting difficulties. Observe fall speed changes and multiple next pieces.
    *   **Code Review:** Ensure data persistence is secure and robust.

**Phase 4: Advanced Gameplay & Polish**
*   **Target Features:**
    *   Sophisticated Scoring System
    *   Level Progression Triggers
    *   Next Level Progress Indicator
    *   Main Menu
    *   Pause Functionality
*   **Deliverable:** A runnable `tetris_game.py` with advanced scoring, flexible level progression, a progress indicator, pause functionality, and a main menu.
*   **Validation Method:**
    *   **Unit Tests:** New tests for advanced scoring logic, multiple level triggers, and pause/resume states.
    *   **Manual Playtesting:** Verify advanced scoring, test different level progression paths, observe progress indicator, and confirm pause/resume functionality. Navigate the main menu.
    *   **Code Review:** Ensure scoring logic is accurate and complex state transitions are handled correctly.

## 8. Technologies Used
-   **Python:** Primary programming language.
-   **`curses` library:** For creating the text-based console user interface.
-   **`unittest` module:** For unit testing the game logic.
-   **`color_utils.py`:** A utility for applying ANSI color codes to terminal text output.

## 8. Project Structure
-   `tetris_game.py`: Contains the `GameEngine` (core game logic) and `UserInterface` (console rendering and input) classes, along with the main game loop.
-   `test_tetris_game.py`: Comprehensive unit tests for the `GameEngine` and `UserInterface` components.
-   `requirements_specification.md`: Detailed functional and non-functional requirements for the game.
-   `system_design.md`: Provides an overview of the system architecture and component design.
-   `review_feedback.md`: Contains feedback and assessments from previous development iterations.
-   `20251116-015828_complete_state.json`: A snapshot of the project's state at a specific iteration.
-   `README.md`: This document, providing an overview and instructions for the project.
-   `color_utils.py`: Provides a `Color` class for generating colored terminal output using ANSI escape codes.
