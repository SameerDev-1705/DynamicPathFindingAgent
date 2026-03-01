import tkinter as tk
from tkinter import ttk, messagebox
import math
from queue import PriorityQueue
import random
import time
# Colors
WHITE = "#FFFFFF"
BLACK = "#2C3E50"      # Wall
RED = "#E74C3C"        # Visited
GREEN = "#2ECC71"      # Path
BLUE = "#3498DB"       # Start
YELLOW = "#F1C40F"     # Frontier
PURPLE = "#9B59B6"     # Goal
GREY = "#BDC3C7"       # Grid lines
ORANGE = "#E67E22"     # Agent moving
class Node:
    def __init__(self, row, col, width, height, canvas):
        self.row = row
        self.col = col
        self.x = col * width
        self.y = row * height
        self.width = width
        self.height = height
        self.color = WHITE
        self.neighbors = []
        self.g = float('inf')
        self.h = float('inf')
        self.f = float('inf')
        self.parent = None
        self.canvas = canvas
        self.rect_id = self.canvas.create_rectangle(
            self.x, self.y, self.x + self.width, self.y + self.height, 
            fill=self.color, outline=GREY
        )
    def get_pos(self):
        return self.row, self.col
    def is_wall(self): return self.color == BLACK
    def reset(self):
        self.color = WHITE
        self.canvas.itemconfig(self.rect_id, fill=self.color)
    def reset_search_data(self):
        self.g = float('inf')
        self.h = float('inf')
        self.f = float('inf')
        self.parent = None
    def make_start(self):
        self.color = BLUE
        self.canvas.itemconfig(self.rect_id, fill=self.color)
    def make_wall(self):
        self.color = BLACK
        self.canvas.itemconfig(self.rect_id, fill=self.color)
    def make_goal(self):
        self.color = PURPLE
        self.canvas.itemconfig(self.rect_id, fill=self.color)
    def make_visited(self):
        self.color = RED
        self.canvas.itemconfig(self.rect_id, fill=self.color)
    def make_frontier(self):
        self.color = YELLOW
        self.canvas.itemconfig(self.rect_id, fill=self.color)
    def make_path(self):
        self.color = GREEN
        self.canvas.itemconfig(self.rect_id, fill=self.color)
    def make_agent(self):
        self.color = ORANGE
        self.canvas.itemconfig(self.rect_id, fill=self.color)
    def update_neighbors(self, grid, rows, cols):
        self.neighbors = []
        if self.row < rows - 1 and not grid[self.row + 1][self.col].is_wall(): # Down
            self.neighbors.append(grid[self.row + 1][self.col])
        if self.row > 0 and not grid[self.row - 1][self.col].is_wall(): # Up
            self.neighbors.append(grid[self.row - 1][self.col])
        if self.col < cols - 1 and not grid[self.row][self.col + 1].is_wall(): # Right
            self.neighbors.append(grid[self.row][self.col + 1])
        if self.col > 0 and not grid[self.row][self.col - 1].is_wall(): # Left
            self.neighbors.append(grid[self.row][self.col - 1])
class PathfindingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dynamic Pathfinding Agent")
        self.rows = 20
        self.cols = 20
        self.canvas_width = 700
        self.canvas_height = 700
        self.grid = []
        self.start_node = None
        self.goal_node = None
        self.dynamic_mode = tk.BooleanVar(value=False)
        self.path = []
        self.agent_idx = 0
        self.animation_job = None
        self.path_parents = {}
        self.dragging_start = False
        self.dragging_goal = False
        self.metrics = {
            "nodes_visited": tk.IntVar(value=0),
            "path_cost": tk.IntVar(value=0),
            "exec_time": tk.StringVar(value="0.00 ms")
        }
        self.setup_ui()
        self.create_grid()
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        # Left Panel (Controls)
        control_frame = ttk.Frame(main_frame, width=280)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        # Grid Size Box
        grid_lf = ttk.LabelFrame(control_frame, text="Grid Size", padding=5)
        grid_lf.pack(fill=tk.X, pady=5)
        ttk.Label(grid_lf, text="Rows:").grid(row=0, column=0, padx=2, pady=2, sticky=tk.W)
        self.rows_var = tk.StringVar(value=str(self.rows))
        ttk.Spinbox(grid_lf, from_=5, to=100, textvariable=self.rows_var, width=5).grid(row=0, column=1, padx=2, pady=2)

        ttk.Label(grid_lf, text="Cols:").grid(row=1, column=0, padx=2, pady=2, sticky=tk.W)
        self.cols_var = tk.StringVar(value=str(self.cols))
        ttk.Spinbox(grid_lf, from_=5, to=100, textvariable=self.cols_var, width=5).grid(row=1, column=1, padx=2, pady=2)

        ttk.Button(grid_lf, text="Apply Size", command=self.apply_grid_size).grid(row=2, column=0, columnspan=2, pady=5, sticky=tk.EW)

        # Map Generation Box
        map_lf = ttk.LabelFrame(control_frame, text="Map Generation", padding=5)
        map_lf.pack(fill=tk.X, pady=5)
        
        ttk.Label(map_lf, text="Density %:").grid(row=0, column=0, padx=2, pady=2, sticky=tk.W)
        self.density_var = tk.StringVar(value="30")
        ttk.Spinbox(map_lf, from_=0, to=100, textvariable=self.density_var, width=5).grid(row=0, column=1, padx=2, pady=2)
        
        ttk.Button(map_lf, text="Generate Maze", command=self.generate_maze).grid(row=1, column=0, columnspan=2, pady=5, sticky=tk.EW)
        
        # Search Settings Box
        search_lf = ttk.LabelFrame(control_frame, text="Search Settings", padding=5)
        search_lf.pack(fill=tk.X, pady=5)
        
        ttk.Label(search_lf, text="Algorithm:").pack(anchor=tk.W, pady=2)
        self.algorithm_var = tk.StringVar(value="A* Search")
        algos = ["A* Search", "Greedy Best-First Search"]
        ttk.Combobox(search_lf, textvariable=self.algorithm_var, values=algos, state="readonly").pack(fill=tk.X, pady=2)
        
        ttk.Label(search_lf, text="Heuristic:").pack(anchor=tk.W, pady=2)
        self.heuristic_var = tk.StringVar(value="Manhattan")
        heurs = ["Manhattan", "Euclidean"]
        ttk.Combobox(search_lf, textvariable=self.heuristic_var, values=heurs, state="readonly").pack(fill=tk.X, pady=2)
        
        # Dynamic Mode
        ttk.Checkbutton(search_lf, text="Dynamic Mode (Spawning)", variable=self.dynamic_mode).pack(anchor=tk.W, pady=10)
        
        # Actions Box
        action_lf = ttk.LabelFrame(control_frame, text="Actions", padding=5)
        action_lf.pack(fill=tk.X, pady=5)
        
        ttk.Button(action_lf, text="Start Search", command=self.start_search).pack(fill=tk.X, pady=2)
        ttk.Button(action_lf, text="Clear Path", command=self.clear_path).pack(fill=tk.X, pady=2)
        ttk.Button(action_lf, text="Reset Grid", command=self.create_grid).pack(fill=tk.X, pady=2)
        
        # Metrics Box
        metrics_lf = ttk.LabelFrame(control_frame, text="Real-Time Metrics", padding=5)
        metrics_lf.pack(fill=tk.X, pady=5)
        
        ttk.Label(metrics_lf, text="Nodes Visited:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Label(metrics_lf, textvariable=self.metrics["nodes_visited"]).grid(row=0, column=1, sticky=tk.E, pady=2)
        
        ttk.Label(metrics_lf, text="Path Cost:").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Label(metrics_lf, textvariable=self.metrics["path_cost"]).grid(row=1, column=1, sticky=tk.E, pady=2)
        
        ttk.Label(metrics_lf, text="Execution Time:").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Label(metrics_lf, textvariable=self.metrics["exec_time"]).grid(row=2, column=1, sticky=tk.E, pady=2)
        
        # Legend Box
        legend_lf = ttk.LabelFrame(control_frame, text="Legend", padding=5)
        legend_lf.pack(fill=tk.X, pady=5)
        
        self.add_legend_item(legend_lf, BLUE, "Start Node")
        self.add_legend_item(legend_lf, PURPLE, "Goal Node")
        self.add_legend_item(legend_lf, BLACK, "Wall / Obstacle")
        self.add_legend_item(legend_lf, YELLOW, "Frontier (Queue)")
        self.add_legend_item(legend_lf, RED, "Visited / Expanded")
        self.add_legend_item(legend_lf, GREEN, "Final Path")
        self.add_legend_item(legend_lf, ORANGE, "Agent (Dynamic)")
        
        ttk.Label(control_frame, text="Controls: Left Click to Draw Walls/Drag Start/Goal\nRight Click to Erase Walls", foreground="gray", justify=tk.LEFT, wraplength=250).pack(fill=tk.X, pady=10)

        # Right Panel (Canvas)
        self.canvas = tk.Canvas(main_frame, width=self.canvas_width, height=self.canvas_height, bg=WHITE)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.canvas.bind("<Button-1>", self.on_left_click)
        self.canvas.bind("<B1-Motion>", self.on_left_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_left_release)
        self.canvas.bind("<Button-3>", self.on_right_click)
        self.canvas.bind("<B3-Motion>", self.on_right_drag)

    def add_legend_item(self, parent, color, text):
        f = ttk.Frame(parent)
        f.pack(fill=tk.X, pady=1)
        tk.Label(f, bg=color, width=2, height=1).pack(side=tk.LEFT, padx=(0,5))
        ttk.Label(f, text=text).pack(side=tk.LEFT)

    def cancel_animation(self):
        if self.animation_job:
            self.root.after_cancel(self.animation_job)
            self.animation_job = None

    def apply_grid_size(self):
        try:
            r = int(self.rows_var.get())
            c = int(self.cols_var.get())
            if 5 <= r <= 100 and 5 <= c <= 100:
                self.rows = r
                self.cols = c
                self.create_grid()
            else:
                messagebox.showerror("Error", "Rows and Cols must be between 5 and 100.")
        except ValueError:
             messagebox.showerror("Error", "Invalid dimensions.")

    def generate_maze(self):
        self.cancel_animation()
        self.create_grid()
        try:
            density_float = float(self.density_var.get()) / 100.0
        except:
            density_float = 0.3
            
        for row in self.grid:
            for node in row:
                if node != self.start_node and node != self.goal_node:
                    if random.random() < density_float:
                        node.make_wall()

    def clear_path(self):
        self.cancel_animation()
        for row in self.grid:
            for node in row:
                if node.color in (RED, YELLOW, GREEN, ORANGE):
                    node.reset()
        self.metrics["nodes_visited"].set(0)
        self.metrics["path_cost"].set(0)
        self.metrics["exec_time"].set("0.00 ms")
        self.start_node.make_start()
        self.goal_node.make_goal()

    def create_grid(self):
        self.cancel_animation()
        self.canvas.delete("all")
        self.grid = []
        node_w = self.canvas_width / self.cols
        node_h = self.canvas_height / self.rows
        
        for r in range(self.rows):
            row_list = []
            for c in range(self.cols):
                node = Node(r, c, node_w, node_h, self.canvas)
                row_list.append(node)
            self.grid.append(row_list)
            
        self.start_node = self.grid[1][1] if self.rows > 2 else self.grid[0][0]
        self.start_node.make_start()
        
        gr, gc = self.rows - 2, self.cols - 2
        if gr < 0: gr = 0
        if gc < 0: gc = 0
        self.goal_node = self.grid[gr][gc]
        self.goal_node.make_goal()

    def get_clicked_node(self, event):
        col, row = int(event.x // (self.canvas_width / self.cols)), int(event.y // (self.canvas_height / self.rows))
        if row < 0 or row >= self.rows or col < 0 or col >= self.cols: 
            return None
        return self.grid[row][col]

    def on_left_click(self, event):
        node = self.get_clicked_node(event)
        if not node: return
        
        if node == self.start_node:
            self.dragging_start = True
        elif node == self.goal_node:
            self.dragging_goal = True
        elif node != self.start_node and node != self.goal_node:
            node.make_wall()

    def on_left_drag(self, event):
        node = self.get_clicked_node(event)
        if not node: return
        
        if self.dragging_start:
            if node != self.goal_node and not node.is_wall():
                self.start_node.reset()
                node.make_start()
                self.start_node = node
        elif self.dragging_goal:
            if node != self.start_node and not node.is_wall():
                self.goal_node.reset()
                node.make_goal()
                self.goal_node = node
        else:
            if node != self.start_node and node != self.goal_node:
                node.make_wall()

    def on_left_release(self, event):
        self.dragging_start = False
        self.dragging_goal = False

    def on_right_click(self, event):
        node = self.get_clicked_node(event)
        if not node: return
        if node != self.start_node and node != self.goal_node:
            node.reset()

    def on_right_drag(self, event):
        node = self.get_clicked_node(event)
        if not node: return
        if node != self.start_node and node != self.goal_node:
            node.reset()

    def heuristic(self, p1, p2):
        algo = self.heuristic_var.get()
        x1, y1 = p1
        x2, y2 = p2
        if algo == "Manhattan":
            return abs(x1 - x2) + abs(y1 - y2)
        else:
            return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

    def reconstruct_path(self, current, instant=False):
        path = []
        while current in self.path_parents:
            path.append(current)
            current = self.path_parents[current]
            if not instant: current.make_path()
        path.reverse()
        return path

    def search(self, start, goal, instant=False):
        for row in self.grid:
            for node in row:
                node.reset_search_data()
                
        algo = self.algorithm_var.get()
        count = 0
        open_set = PriorityQueue()
        open_set.put((0, count, start))
        self.path_parents = {}
        
        start.g = 0
        start.h = self.heuristic(start.get_pos(), goal.get_pos())
        start.f = start.h if algo == "Greedy Best-First Search" else start.g + start.h
        
        open_set_hash = {start}
        start_time = time.time()
        nodes_expanded = 0
        
        while not open_set.empty():
            if not instant and nodes_expanded % 10 == 0:
                self.root.update_idletasks()
                
            current = open_set.get()[2]
            open_set_hash.remove(current)
            
            if current == goal:
                exec_time = (time.time() - start_time) * 1000
                self.metrics["exec_time"].set(f"{exec_time:.2f} ms")
                self.metrics["nodes_visited"].set(nodes_expanded)
                
                path = self.reconstruct_path(goal, instant)
                self.metrics["path_cost"].set(len(path))
                
                goal.make_goal()
                start.make_start()
                return path
                
            nodes_expanded += 1
            
            for neighbor in current.neighbors:
                temp_g = current.g + 1
                
                if temp_g < neighbor.g:
                    self.path_parents[neighbor] = current
                    neighbor.g = temp_g
                    neighbor.h = self.heuristic(neighbor.get_pos(), goal.get_pos())
                    neighbor.f = neighbor.h if algo == "Greedy Best-First Search" else neighbor.g + neighbor.h
                    
                    if neighbor not in open_set_hash:
                        count += 1
                        open_set.put((neighbor.f, count, neighbor))
                        open_set_hash.add(neighbor)
                        if neighbor != goal and not instant:
                            neighbor.make_frontier()
                            
            if current != start and not instant:
                current.make_visited()
                
        # Path not found
        exec_time = (time.time() - start_time) * 1000
        self.metrics["exec_time"].set(f"{exec_time:.2f} ms")
        self.metrics["nodes_visited"].set(nodes_expanded)
        self.metrics["path_cost"].set(0)
        return []

    def start_search(self):
        self.clear_path()
        for row in self.grid:
            for node in row:
                node.update_neighbors(self.grid, self.rows, self.cols)
                
        if self.dynamic_mode.get():
            self.start_dynamic_agent()
        else:
            path = self.search(self.start_node, self.goal_node, instant=False)
            if not path:
                messagebox.showinfo("Result", "No path found.")

    def start_dynamic_agent(self):
        self.path = self.search(self.start_node, self.goal_node, instant=True)
        if not self.path:
            messagebox.showinfo("Result", "No path found to begin with!")
            return
            
        # Draw initial path ahead visually
        for node in self.path:
            if node != self.goal_node:
                node.make_path()
        self.start_node.make_start()
            
        self.agent_idx = -1
        self.agent_node = self.start_node
        self.animate_agent()
        
    def animate_agent(self):
        if self.agent_node == self.goal_node:
            messagebox.showinfo("Success", "Agent reached the goal!")
            return
            
        # Spawn dynamic obstacle
        if random.random() < 0.1: # 10% chance
            empty_nodes = [n for row in self.grid for n in row if n.color == WHITE and n != self.start_node and n != self.goal_node and n != self.agent_node]
            if empty_nodes:
                new_wall = random.choice(empty_nodes)
                new_wall.make_wall()
                
                # Replan if blocked
                remaining_path = self.path[self.agent_idx+1:] if self.agent_idx >= 0 else self.path
                if new_wall in remaining_path:
                    # Clear out the remainder of old visual green path
                    for n in remaining_path:
                        if n.color == GREEN: n.reset()

                    for row in self.grid:
                        for node in row:
                            node.update_neighbors(self.grid, self.rows, self.cols)
                    new_path = self.search(self.agent_node, self.goal_node, instant=True)
                    if not new_path:
                        self.agent_node.make_agent() # redraw agent color
                        messagebox.showinfo("Blocked", "Agent was trapped by dynamic obstacles!")
                        return
                    self.path = new_path
                    self.agent_idx = -1
                    # Draw new green path ahead
                    for n in self.path:
                        if n.color == WHITE: n.make_path()
        # Move agent
        self.agent_idx += 1
        if self.agent_idx < len(self.path):
            if self.agent_node != self.start_node and self.agent_node != self.goal_node:
                self.agent_node.make_path() # leave green trail behind
            self.agent_node = self.path[self.agent_idx]
            if self.agent_node != self.goal_node:
                self.agent_node.make_agent()      
        self.animation_job = self.root.after(200, self.animate_agent)
if __name__ == "__main__":
    root = tk.Tk()
    app = PathfindingApp(root)
    root.mainloop()