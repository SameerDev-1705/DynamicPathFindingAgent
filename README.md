# Dynamic Pathfinding Agent

## Overview

This project implements a **Dynamic Pathfinding Agent** using **A\*** and **Greedy Best-First Search (GBFS)** in a customizable grid environment.

The system allows users to:

- Define grid size (Rows × Columns)
- Generate random mazes with adjustable obstacle density
- Manually draw and erase walls
- Select search algorithms and heuristics
- Enable dynamic obstacle spawning with real-time re-planning
- View full visual search animation
- Monitor real-time performance metrics

The project is built using Python and Tkinter.

---

## Implemented Algorithms

### A* Search
Uses the evaluation function:

f(n) = g(n) + h(n)

Where:
- g(n) = cost from start node to current node
- h(n) = heuristic estimate to goal

### Greedy Best-First Search
Uses the evaluation function:

f(n) = h(n)

---

## Heuristics

- Manhattan Distance
- Euclidean Distance

Users can select both algorithm and heuristic from the GUI before starting the search.

---

## Dynamic Mode

When Dynamic Mode is enabled:

- Obstacles spawn randomly while the agent is moving.
- If a spawned obstacle blocks the current path, the agent automatically re-plans from its current position.
- Re-computation is optimized to avoid unnecessary full resets.

---

## Visualization

The GUI highlights:

- Frontier nodes (Yellow)
- Visited nodes (Red)
- Final path (Green)
- Start node (Blue)
- Goal node (Purple)
- Walls (Black)
- Moving agent (Orange)

A real-time metrics panel displays:

- Nodes Visited
- Path Cost
- Execution Time (milliseconds)

---

## Requirements

- Python 3.8 or higher
- Tkinter

Tkinter is included with standard Python installations.

If missing:

Linux:
sudo apt-get install python3-tk

macOS:
brew install python-tk

---

## How to Run

1. Clone or download the repository.
2. Open a terminal inside the project folder.
3. Run:

python filename.py

Replace `filename.py` with the actual script name.

---

## Controls

Left Click: Draw walls  
Right Click: Erase walls  
Drag Start/Goal: Move start or goal node  
Enable Dynamic Mode: Activate obstacle spawning  

---

## Purpose

This project demonstrates informed search strategies, heuristic comparison, and real-time path re-planning in dynamic grid environments. It is suitable for academic and educational use.
