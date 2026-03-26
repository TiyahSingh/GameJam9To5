# Development Plan — 9 to 5

## Project Summary

**9 to 5** is a 2D top-down, grid-based puzzle game built with Python and Pygame. The player controls two office workers simultaneously with a single input, navigating themed environments (Bathroom, Office, Elevator, Break Room, Parking Lot) to reach designated goal tiles. The game features handcrafted levels, a procedural level generator backed by a BFS solver, themed pixel-art assets, and a polished main menu.

---

## Milestones

### Milestone 1 — Core Prototype (Completed)
- [x] Grid-based movement system with synchronised dual-character control
- [x] Tile types: Empty, Wall, Blocker, Goal A, Goal B, Hazard, Interactive
- [x] Movement rules: wall blocking, off-grid fall-off reset, overlap prevention
- [x] Win condition: Character A on Goal A **and** Character B on Goal B
- [x] Keyboard input (WASD / Arrow keys) and mouse-click direction inference
- [x] Level data model with ASCII-art parsing (`parse_ascii_level`)

### Milestone 2 — Levels, Solver & Generator (Completed)
- [x] 5 handcrafted static levels across all themes with par-move targets
- [x] BFS solver (`solve_level_bfs`) to validate solvability up to 250k state expansions
- [x] Desync-step counter to ensure generated puzzles require asymmetric thinking
- [x] Procedural level generator with configurable wall/blocker density per theme
- [x] Runtime solvability guarantee on all static and generated levels

### Milestone 3 — Art Pipeline & Themed Rendering (Completed)
- [x] Recursive image loader (`ArtLibrary`) scanning `GameArtImages/`
- [x] Automatic theme detection from folder names and role detection from filenames
- [x] Art buckets per theme: floor, wall, blocker, goal_a, goal_b, hazard, interactive, decor, characters
- [x] Deterministic tile-art selection (no randomness per frame, stable visuals)
- [x] Fallback colour rendering when art assets are unavailable

### Milestone 4 — UI, Menu & HUD (Completed)
- [x] Full-screen main menu with Start Screen background art
- [x] Play, Controls, Rules, and Close Game buttons with hover effects
- [x] Controls overlay and Rules overlay sub-screens with Back navigation
- [x] In-game HUD panel: level number, theme, move counter, par display, star rating
- [x] Best-score tracking per level (moves and stars)
- [x] Auto-advance to next level on completion (700ms delay)

### Milestone 5 — Polish & Quality of Life (Completed)
- [x] Screen flash feedback: red (fall-off), yellow (overlap prevented), green (level complete)
- [x] Auto-fit layout to current display resolution
- [x] Zoom in/out with `+` / `-` keys
- [x] Level reset with `R` (no penalty)
- [x] On-demand procedural level generation with `G`

### Milestone 6 — UI Enhancements & Interactivity (Completed)
- [x] Custom UI button images replacing text labels (Reset, Generate, Zoom, Exit, Pause, Clue)
- [x] Clipboard-themed right-side HUD panel with desk surface background
- [x] Character sprite images for Player A and Player B (all non-Elevator levels)
- [x] Colour-coded goal tile glow highlights and player tile identity overlays
- [x] Pause menu system with aspect-ratio-preserving background and close button
- [x] Pause menu buttons (Home, Sound toggle, Back) vertically laid out on clipboard paper
- [x] Clue system: BFS-based optimal path arrows, 3 uses, +1 reward for 3-star completion
- [x] Procedural 5-pointed star rating (gold/grey, 1–3 stars based on par moves)

### Milestone 7 — Audio & Volume Control (Completed)
- [x] Procedural audio manager (`game/audio.py`) — no external audio files required
- [x] Theme-based background music: Office (Cmaj7), Elevator (Am9), default (Bm) ambient pads
- [x] Detuned oscillator pairs, sub-octave warmth, octave shimmer, stereo panning LFO
- [x] 7 sound effects: click, move, clue, complete, fail, pause open/close
- [x] Music toggle via pause menu Sound button (visual strikethrough when off)
- [x] Volume slider in pause menu — blue cartoonish style, real-time drag control
- [x] Master volume system controlling all SFX + music simultaneously


---

## AI Tools Used

| Tool | Purpose |
|------|---------|
| **Cursor (Claude)** | AI-assisted coding agent used for codebase exploration, refactoring, documentation generation, Git operations, and iterative development throughout the project. |

> All AI-assisted work is clearly documented. Cursor was used as a development accelerator — all game design, level design, and art direction are original human decisions.

---

## Task List

| # | Task | Status | Notes |
|---|------|--------|-------|
| 1 | Core grid movement + dual-character sync | Done | `movement.py`, `types.py` |
| 2 | Level data model + ASCII parser | Done | `level.py` |
| 3 | 5 static themed levels | Done | `levels.py` |
| 4 | BFS solver + solvability validation | Done | `solver.py` |
| 5 | Procedural level generator | Done | `generator.py` |
| 6 | Art asset loader with theme/role detection | Done | `assets.py` |
| 7 | Main menu with background art + buttons | Done | `menu.py` |
| 8 | Game loop, HUD, flash feedback, zoom | Done | `app.py` |
| 9 | Auto-fit to screen resolution | Done | `app.py` |
| 10 | Documentation (plan, readme, changelog) | Done | Project root |
| 11 | Custom UI button images (Reset, Generate, Zoom, Exit, Pause, Clue) | Done | `app.py` |
| 12 | Pause menu with clipboard background + close button | Done | `app.py` |
| 13 | Clue system (BFS path hints, 3 uses, 3-star reward) | Done | `app.py`, `solver.py` |
| 14 | Procedural star rating (gold/grey, 1–3 stars) | Done | `app.py` |
| 15 | Character sprites + player/goal tile colour highlights | Done | `app.py`, `assets.py` |
| 16 | Procedural audio manager (SFX + music) | Done | `audio.py` |
| 17 | Volume slider in pause menu | Done | `app.py`, `audio.py` |
| 18 | Pause menu layout polish (close button, button spacing) | Done | `app.py` |
| 19 | Level-select screen | Planned | — |
| 20 | Undo/redo system | Planned | — |
| 21 | Character movement animation | Planned | — |
| 22 | Standalone executable packaging | Planned | — |

---

## Architecture Overview

```
main.py              Entry point — initialises Pygame, runs GameApp
game/
  app.py             Main game loop, rendering, HUD, pause menu, input handling
  audio.py           Procedural audio manager — SFX, music, volume control
  level.py           Level & Character data models, ASCII level parser
  levels.py          5 handcrafted static levels with solvability checks
  movement.py        Dual-character movement rules and step resolution
  solver.py          BFS solver for level validation, par & clue path calculation
  generator.py       Procedural level generator with quality constraints
  assets.py          Recursive art loader with theme/role classification
  menu.py            Main menu system with overlays and button widgets
  types.py           Shared types: Vec2, Tile enum, direction constants
GameArtImages/       Themed art assets (backgrounds, obstacles, goals, characters, UI)
  New UI/            Button images (Reset, Generate, Zoom, Pause, Clue, Star)
  Pause Menu Buttons/ Home, Sound, Back, Replay button sprites
```
