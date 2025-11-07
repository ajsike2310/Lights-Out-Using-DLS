import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import random
import copy
import time
import threading

GRID_SIZE = 3
AI = -1

class LightsOutAIOnly:
    def __init__(self, root):
        self.root = root
        self.root.title("💡 Lights Out")
        self.root.geometry("1600x900")
        self.root.configure(bg="#0d0d0d")
        self.root.resizable(False, False)

        # Game Variables (rows/cols adjustable)
        self.rows = GRID_SIZE
        self.cols = GRID_SIZE
        self.state = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.buttons = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        self.lock = threading.Lock()
        self._minimax_cache = {}
        self.ai_move_delay_ms = 1000
        self.ai_blink_colors = ["#00E5FF", "#111", "#00E5FF", "#111"]
        self.game_start_time = time.time()
        self.ai_move_log = []

        # --- Professional Header ---
        self.title_label = tk.Label(self.root, text="💡 Lights Out AI Demo",
                                    font=("Segoe UI Semibold", 28), fg="#00FFC6", bg="#0d0d0d")
        self.title_label.pack(pady=25)

        self.status_label = tk.Label(self.root, text="Press G to Generate or S to Solve",
                                     font=("Segoe UI", 16), fg="#FFD700", bg="#0d0d0d")
        self.status_label.pack(pady=10)
        # --- Main content: left=board, right=log ---
        main_frame = tk.Frame(self.root, bg="#0d0d0d")
        main_frame.pack(fill="both", expand=True, padx=15, pady=10)

        # Left panel: controls + board
        left_panel = tk.Frame(main_frame, bg="#0d0d0d")
        left_panel.pack(side="left", anchor="n")

        # grid size controls (rows x cols)
        ctrl = tk.Frame(left_panel, bg="#0d0d0d")
        ctrl.pack(pady=(0, 6))
        tk.Label(ctrl, text="Rows:", fg="#AAAAAA", bg="#0d0d0d").grid(row=0, column=0, padx=(0,4))
        self.rows_spin = tk.Spinbox(ctrl, from_=1, to=12, width=4)
        self.rows_spin.delete(0, 'end')
        self.rows_spin.insert(0, str(self.rows))
        self.rows_spin.grid(row=0, column=1)
        tk.Label(ctrl, text="Cols:", fg="#AAAAAA", bg="#0d0d0d").grid(row=0, column=2, padx=(8,4))
        self.cols_spin = tk.Spinbox(ctrl, from_=1, to=12, width=4)
        self.cols_spin.delete(0, 'end')
        self.cols_spin.insert(0, str(self.cols))
        self.cols_spin.grid(row=0, column=3)
        set_btn = tk.Button(ctrl, text="Set Grid", command=self.set_grid, bg="#222", fg="#00FFC6")
        set_btn.grid(row=0, column=4, padx=(8,0))

        # board sits under the controls in the left panel
        self.board_frame = tk.Frame(left_panel, bg="#0d0d0d")
        self.board_frame.pack()
        self.create_grid()

        # --- Instructions ---
        instr = tk.Label(self.root, text="Controls: G = Generate | S = AI Solve | R = Reset | Q = Quit | L = Clear Log",
                         font=("Segoe UI", 10), fg="#AAAAAA", bg="#0d0d0d")
        instr.pack(pady=8)

        # Right panel: log and controls
        right_panel = tk.Frame(main_frame, bg="#0d0d0d", width=420)
        right_panel.pack(side="left", fill="y")
        right_panel.pack_propagate(False)

        # --- AI Log Panel (with scrollbar) ---
        log_frame = tk.Frame(right_panel, bg="#0d0d0d")
        log_frame.pack(fill="both", expand=True, padx=(8,0), pady=4)
        self.log_text = tk.Text(log_frame, height=20, bg="#111", fg="#00FFC6",
                                insertbackground="#00FFC6", font=("Consolas", 10), relief="flat", padx=10, pady=6)
        self.log_text.pack(side="left", fill="both", expand=True)
        self.log_text.insert("end", "💡 AI log initialized.\n")
        self.log_text.config(state="disabled")

        # vertical scrollbar for the log
        log_scroll = tk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        log_scroll.pack(side="right", fill="y")
        self.log_text.configure(yscrollcommand=log_scroll.set)

        # Clear Log button
        try:
            clear_btn = tk.Button(right_panel, text="Clear Log", command=self.clear_move_log,
                                  bg="#222", fg="#00FFC6", relief="groove")
            clear_btn.pack(anchor="ne", pady=(4, 0), padx=(0,8))
        except Exception:
            pass

        # --- Bindings ---
        self.root.bind('<g>', lambda e: self.generate_puzzle_random())
        self.root.bind('<G>', lambda e: self.generate_puzzle_random())
        self.root.bind('<s>', lambda e: self.start_solver_thread())
        self.root.bind('<S>', lambda e: self.start_solver_thread())
        self.root.bind('<r>', lambda e: self.reset_game())
        self.root.bind('<R>', lambda e: self.reset_game())
        self.root.bind('<q>', lambda e: self.root.destroy())
        self.root.bind('<Q>', lambda e: self.root.destroy())
        self.root.bind('<l>', lambda e: self.clear_move_log())
        self.root.bind('<L>', lambda e: self.clear_move_log())

        # Start with a puzzle
        self.generate_puzzle_random()

    # --- UI Setup ---
    def create_grid(self):
        # clear any existing widgets in the board_frame
        for w in self.board_frame.winfo_children():
            w.destroy()
        # recreate buttons grid based on current rows/cols
        self.buttons = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        for r in range(self.rows):
            for c in range(self.cols):
                btn = tk.Label(self.board_frame, width=10, height=5, bg="#111",
                               relief="flat", bd=0, cursor="arrow")
                btn.grid(row=r, column=c, padx=12, pady=12)
                self.buttons[r][c] = btn

    # --- Puzzle generation ---
    def generate_puzzle_random(self, moves=None):
        if moves is None:
            max_cells = max(1, self.rows * self.cols)
            # prefer at least 3 moves when the board is large enough
            if max_cells >= 3:
                moves = random.randint(3, max_cells)
            else:
                moves = random.randint(1, max_cells)

        with self.lock:
            self.state = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
            for _ in range(moves):
                r, c = random.randrange(self.rows), random.randrange(self.cols)
                self.toggle(r, c)
            self.ai_move_log = []
            self._minimax_cache = {}
            self.game_start_time = time.time()

        # keep the existing log (do not auto-clear); inform the user how to clear
        self.update_buttons()
        self.status_label.config(text="Puzzle Generated — Press 'S' to Solve",
                                 fg="#00FFAA")
    # --- AI Solver Thread ---
    def start_solver_thread(self):
        threading.Thread(target=self._run_solver, daemon=True).start()

    def _run_solver(self):
        # Schedule status update on main thread
        self.root.after(0, lambda: self.status_label.config(text="AI Solving...", fg="#00B0FF"))
        max_depth = self.rows * self.cols
        with self.lock:
            start = copy.deepcopy(self.state)

        for depth in range(0, max_depth + 1):
            path = []
            visited = {self._state_key(start)}
            found = self._dfs_solve(start, depth, path, visited)
            if found is not None:
                msg = f"AI found solution ({len(found)} moves)"
                self._log(msg)
                self.root.after(0, lambda msg=msg: self.status_label.config(text=msg, fg="#00B0FF"))
                delay = self.ai_move_delay_ms
                for i, (rr, cc) in enumerate(found):
                    self.root.after(i * delay, lambda r=rr, c=cc: self.animate_ai_move(r, c))
                    self.root.after(i * delay + max(50, delay - 50),
                                    lambda r=rr, c=cc: self._finalize_ai_move(r, c))
                return
        self._log("No solution found within depth limit.")
        # show info on main thread
        self.root.after(0, lambda: messagebox.showinfo("No solution", "No solution found within depth limit."))

    # --- DFS Solver ---
    def _dfs_solve(self, state, depth_left, path, visited):
        if self.is_game_over_state(state):
            return list(path)
        if depth_left == 0:
            return None
        for r in range(self.rows):
            for c in range(self.cols):
                temp = copy.deepcopy(state)
                self.toggle_cell(temp, r, c)
                key = self._state_key(temp)
                if key in visited:
                    continue
                visited.add(key)
                path.append((r, c))
                res = self._dfs_solve(temp, depth_left - 1, path, visited)
                if res is not None:
                    return res
                path.pop()
                visited.remove(key)
        return None

    # --- Core Functions ---
    def toggle(self, r, c):
        for i, j in [(r, c), (r-1, c), (r+1, c), (r, c-1), (r, c+1)]:
            if 0 <= i < self.rows and 0 <= j < self.cols:
                self.state[i][j] = 1 - self.state[i][j]

    def toggle_cell(self, grid, r, c):
        for i, j in [(r, c), (r-1, c), (r+1, c), (r, c-1), (r, c+1)]:
            if 0 <= i < self.rows and 0 <= j < self.cols:
                grid[i][j] = 1 - grid[i][j]

    def update_buttons(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.state[r][c] == 1:
                    self.buttons[r][c].config(bg="#FFD700", highlightthickness=2, highlightbackground="#FF0")
                else:
                    self.buttons[r][c].config(bg="#111", highlightthickness=0)

    def set_grid(self):
        # Read user-specified rows/cols and rebuild the board
        try:
            r = int(self.rows_spin.get())
            c = int(self.cols_spin.get())
        except Exception:
            return
        r = max(1, min(12, r))
        c = max(1, min(12, c))
        self.rows = r
        self.cols = c
        # reinitialize state and UI
        self.state = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.create_grid()
        self.generate_puzzle_random()

    def _state_key(self, state):
        return tuple(tuple(row) for row in state)

    def animate_ai_move(self, r, c):
        btn = self.buttons[r][c]
        colors = self.ai_blink_colors
        total_ms = max(200, self.ai_move_delay_ms)
        step = max(50, total_ms // (len(colors) + 1))
        delay = 0
        for col in colors:
            self.root.after(delay, lambda b=btn, col=col: b.config(bg=col))
            delay += step

    def _finalize_ai_move(self, r, c):
        with self.lock:
            self.toggle(r, c)
        self.update_buttons()

        lights = sum(sum(row) for row in self.state)
        ts = time.time() - self.game_start_time
        self._log(f"Move ({r},{c}) | t={ts:.2f}s | lights={lights}")

        if self.is_game_over():
            self._log("AI turned off all lights!")
            # do NOT auto-clear the log; let the user clear it manually
            messagebox.showinfo("Completed", "🎉 AI turned off all lights!")
            self.reset_game()

    def reset_game(self):
        self.generate_puzzle_random()
        self._log("New puzzle generated.")
        self.status_label.config(text="Game Reset — Press 'S' to Solve", fg="#FFD700")

    # --- Utils ---
    def is_game_over(self):
        return all(cell == 0 for row in self.state for cell in row)

    def is_game_over_state(self, grid):
        return all(cell == 0 for row in grid for cell in row)

    def _log(self, msg):
        self.log_text.config(state="normal")
        self.log_text.insert("end", f"{msg}\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def clear_move_log(self):
        with self.lock:
            try:
                self.ai_move_log = []
            except Exception:
                self.ai_move_log = []
            try:
                self.game_start_time = time.time()
            except Exception:
                pass
        # clear UI
        try:
            self.log_text.config(state="normal")
            self.log_text.delete('1.0', 'end')
            self.log_text.insert('end', '💡 AI log initialized.\n')
            self.log_text.config(state="disabled")
        except Exception:
            pass

# ---------- RUN ----------
if __name__ == "__main__":
    root = tk.Tk()
    app = LightsOutAIOnly(root)
    root.mainloop()
