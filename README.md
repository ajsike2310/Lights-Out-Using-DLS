# Lights Out — AI 

A small Tkinter-based Lights Out demo with an AI solver (depth-limited DFS). This repository contains a single script, `LightsOut.py`, which launches a GUI where the program can generate puzzles and have the built-in AI attempt to solve them while animating moves and logging progress.

## Key features

- Clean, dark-themed Tkinter GUI
- Adjustable grid size (rows & cols)
- Puzzle generator
- AI solver with animated moves and logging
- Keyboard shortcuts for quick control

## Requirements

- Python 3.8+ (3.10/3.11 recommended)
- Pillow (for image support if needed by the UI)

You can install the dependency with pip:

```powershell
pip install Pillow
```

No additional packages are required to run the GUI beyond the Python standard library and Pillow.

## Files

- `LightsOut.py` — main script. Launches the GUI and contains the AI solver and UI logic.

## Running

From the project folder (where `LightsOut.py` is located), run:

```powershell
python LightsOut.py
```

On Windows you can double-click `LightsOut.py` if Python files are associated with your interpreter, but running from a terminal will show any error messages.

## Controls and UI

- Buttons: the board is displayed as a grid of tiles (labels acting as cells).
- Grid control: use the `Rows` and `Cols` spinboxes and press `Set Grid` to change the size (1–12 allowed).
- Generate a random puzzle: press the `G` key or click the UI generate button (if present).
- Start the AI solver: press the `S` key (the AI will animate each move and write entries to the log panel).
- Reset puzzle (generate a new one): press the `R` key.
- Clear AI log: press `L` (there's also a Clear Log button in the UI).
- Quit: press `Q` or close the window.

The status label at the top shows short messages (e.g. `Puzzle Generated`, `AI Solving...`, etc.). The right panel holds an AI log with details about moves, elapsed time and lights remaining.

## How the AI works (brief)

- The AI uses a depth-limited depth-first search (DFS) over possible move sequences.
- It tests depths from `0` up to `rows * cols` until it finds a solution, then animates the found sequence.
- This brute-force approach is simple and works for small boards (e.g., 3×3), but it does not scale well for larger boards because the search space grows exponentially.

## Configuration options (in `LightsOut.py`)

- `GRID_SIZE` — default grid size used at startup (top of `LightsOut.py`).
- `ai_move_delay_ms` — delay (ms) between AI moves/animations.
- `ai_blink_colors` — colors used to animate the chosen tile before finalizing the move.

Adjust these variables in `LightsOut.py` if you want different defaults or faster/slower animations.

## Limitations and notes

- The DFS solver is not optimized; it can be slow or fail to find a solution within reasonable time for larger grids. For larger boards, consider implementing a linear algebra approach over GF(2) (the common Lights Out solver) or a more advanced search with heuristics and pruning.
- The GUI uses `tkinter.Label` widgets as cells for a stylized look — if you want clickable cells for manual play, you'll need to change them to `tk.Button` and add click handlers.

