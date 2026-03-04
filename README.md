# ⚡ Energy Quest – Intelligent Agent Competition

Energy Quest is an interactive grid-based AI game where a **human player competes against an AI agent** to reach a goal while managing energy and navigating obstacles.

The project demonstrates key **Artificial Intelligence search algorithms** and allows players to compete against them in real time.

Developed as part of the **Artificial Intelligence course (EECE453)** at the **American University in Dubai**.

---

# 🎮 Game Overview

In Energy Quest, both the **human player** and an **AI agent** attempt to reach the goal tile on a grid map.

Along the way, they must:

- Navigate around **walls**
- Avoid **traps**
- Collect **energy gems**
- Manage their **energy consumption**

The winner is determined by **who reaches the goal with the most remaining energy**.

---

# 🧠 AI Algorithms Implemented

The game includes multiple AI opponents with different difficulty levels:

| Algorithm | Difficulty | Description |
|-----------|------------|-------------|
| **Breadth‑First Search (BFS)** | Easy | Explores the grid level by level. Guarantees shortest path but ignores energy cost. |
| **A\*** | Hard | Uses heuristics to efficiently find the optimal path to the goal. |
| **Genetic Algorithm (GA)** | Very Hard | Evolves candidate solutions over generations to find high‑quality paths. |

Each algorithm demonstrates a different approach to solving search problems in AI.

---

# 🕹️ Gameplay Features

- Human vs AI competition
- Multiple AI difficulty levels
- Energy‑based gameplay
- Traps and obstacles
- Energy gem collection
- Countdown start system
- Dynamic winner detection
- Professional UI panel
- Smooth animations
- Interactive game controls
- New map generation
- Credits screen

---

# 🧩 Game Elements

| Element | Description |
|--------|-------------|
| 🔵 Human Agent | Controlled using arrow keys |
| 🟣 AI Agent | Controlled by the selected algorithm |
| 🟡 Energy Gems | Increase player energy |
| 🟥 Traps | Reduce energy |
| ⬛ Walls | Block movement |
| 🟩 Goal Tile | Destination players must reach |

Each player has **their own energy gems**, ensuring fair competition.

---

# 🎮 Controls

| Key | Action |
|----|--------|
| **Arrow Keys** | Move player |
| **Mouse Click** | Interact with UI buttons |
| **ESC** | Exit Credits screen |
| **F11** | Toggle Fullscreen |

---

# 🧠 Game Mechanics

- Each movement **consumes energy**
- Gems **restore energy**
- Traps **reduce energy**
- Players cannot move if:
  - Energy reaches **0**
  - The **goal has been reached**
- The game ends when:
  - Both players finish
  - One player reaches the goal and the other cannot continue

Winner is determined by the **highest remaining energy**.

---

# 🖥️ User Interface

The game interface includes:

### Game Grid
Displays:

- Obstacles
- Gems
- Traps
- Agents
- Goal

### Control Panel
Displays:

- AI opponent selection
- Energy bars
- Game metrics
- Control buttons

Buttons include:

- BFS
- A*
- Genetic AI
- Start Game
- Reset
- New Map
- Credits

---

# 📊 Metrics Displayed

The HUD shows:

- Human energy
- AI energy
- Nodes expanded by AI
- Current game status

These metrics help visualize the **performance of AI algorithms**.

---

# 🏗️ Project Structure

```
EnergyQuest/
│
├── main.py
│
├── core/
│   ├── game.py
│   ├── grid.py
│   └── agent.py
│
├── ai/
│   ├── search.py
│   └── genetic.py
│
├── ui/
│   ├── renderer.py
│   ├── hud.py
│   └── buttons.py
│
├── config/
│   └── settings.py
│
└── README.md
```

---

# ⚙️ Installation

### 1. Clone the repository

```
git clone https://github.com/yourusername/energy-quest-ai.git
```

### 2. Navigate to project

```
cd energy-quest-ai
```

### 3. Install dependencies

```
pip install pygame
```

### 4. Run the game

```
python main.py
```

---

# 🛠️ Technologies Used

- **Python 3**
- **Pygame**
- Artificial Intelligence algorithms
- Object‑oriented programming
- Grid‑based pathfinding

---

# 🎓 Educational Objectives

This project demonstrates key AI concepts including:

- State space search
- Pathfinding algorithms
- Heuristic optimization
- Evolutionary algorithms
- Agent‑based systems
- Game simulation

It also provides a **visual environment to compare algorithm performance**.

---

# 👨‍🏫 Instructor

**Dr. Nejib Ben Hadj‑Alouane**  
Artificial Intelligence – EECE453  
American University in Dubai

---

# 👨‍💻 Developed By

- **Abaan Ahmed**
- Mohammed Almheiri
- Younis Almarzooqi
- Sultan Alsalman

American University in Dubai  
Spring 2026

---

# 🚀 Future Improvements

Potential enhancements:

- More AI algorithms
- Dynamic map generation
- Multiplayer mode
- Better animations
- Sound effects
- Leaderboard system
- Reinforcement Learning agent

---

# 📜 License

This project is developed for **educational purposes**.

---

# ⭐ Acknowledgements

Special thanks to:

- **American University in Dubai**
- **Dr. Nejib Ben Hadj‑Alouane**
- The **EECE453 Artificial Intelligence course**

for providing the opportunity to develop this project.

