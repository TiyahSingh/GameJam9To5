# 9 to 5

A 2D top-down, grid-based puzzle game where you control **two office workers simultaneously** with a single input. Navigate through themed office environments — bathrooms, elevators, offices, break rooms, and parking lots — to guide both characters to their goal tiles.

The twist: both characters move in the same direction at the same time. Walls block individually, but if either character steps off the grid, both fall and the level resets. Think ahead, plan asymmetric paths, and reach both goals to advance.

---

## Features

- **Dual-character synchronised movement** — one input controls both workers
- **5 handcrafted puzzle levels** across themed environments (Bathroom, Office, Elevator, Break Room, Parking Lot)
- **Procedural level generator** — press `G` for an infinite supply of new puzzles, each validated as solvable by a BFS solver
- **Star rating system** — complete levels at or under par for 3 stars
- **Themed pixel art** — custom backgrounds, obstacles, goals, and character sprites per environment
- **Main menu** with Start Screen, Controls overlay, and Rules overlay
- **Auto-fit display** — adapts to your screen resolution
- **Zoom controls** — scale the grid up or down to your preference

---

## Installation

### Prerequisites

- **Python 3.10+** (tested on Python 3.13)
- **pip** (comes with Python)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/TiyahSingh/GameJam9To5.git
   cd GameJam9To5
   ```

2. Install dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```

3. Run the game:
   ```bash
   python main.py
   ```

> **Windows note:** If `python` is not recognised, try `py main.py` instead.

---

## Controls

| Input | Action |
|-------|--------|
| `WASD` / Arrow Keys | Move both characters one tile |
| Mouse Click | Move relative to Character A (click direction) |
| `R` | Reset current level (no penalty) |
| `G` | Generate a new procedural level |
| `+` / `-` | Zoom in / out |
| `Esc` | Quit game |

---

## Game Rules

1. **Both characters respond to every input** — movement is synchronous and step-based.
2. **Wall/blocker collision** is per-character: if one is blocked, only that one stays; the other still moves.
3. **Off-grid fall** — if **either** character would move outside the grid boundary, **both** fall and the level resets. This is the only fail condition.
4. **No overlap** — characters cannot occupy the same tile. If a move would place both on the same square, neither moves for that step.
5. **Win condition** — Character A stands on Goal A **and** Character B stands on Goal B simultaneously.

---

## Project Structure

```
main.py                 Entry point
requirements.txt        Python dependencies
plan.md                 Development plan and milestones
refinements-changes.md  Running changelog of design decisions

game/                   Core game package
  app.py                Game loop, rendering, HUD, input
  level.py              Level & Character data models
  levels.py             5 handcrafted static levels
  movement.py           Dual-character movement logic
  solver.py             BFS solver for validation & par
  generator.py          Procedural level generator
  assets.py             Recursive art loader
  menu.py               Main menu system
  types.py              Shared types (Vec2, Tile, directions)

GameArtImages/          Art assets organised by theme
  Backrounds & Menus/   Menu screen backgrounds
  Bathroom Levels/      Bathroom theme tiles
  Breakroom Levels/     Break room theme tiles
  Elevator Level Characters/  Elevator theme + characters
  Office Levels/        Office theme tiles
  Parking Lot Levels/   Parking lot theme tiles
  UI and Buttons/       Button sprites (Play, Rules, etc.)
  UI Mockup Template/   UI design reference mockups
  Usual Characters/     Default character sprites
```

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `pygame-ce` / `pygame` | >= 2.5.2 | 2D game framework — windowing, rendering, input, image loading |

See `requirements.txt` for the full dependency specification.

---

## Credits

- **Tiyah Singh** — Game design, programming, level design, project lead
- Art assets created for the Game Jam 9-to-5 project

---

## AI Tools Used

This project was developed with assistance from **Cursor (Claude AI)**. The AI agent was used for:

- Code exploration and refactoring
- Documentation generation and maintenance
- Git operations and repository management
- Iterative bug fixing and feature development

All game design decisions, level design, art direction, and creative vision are original human work. AI was used as a development accelerator, not a replacement for design thinking.
