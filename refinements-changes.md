# Refinements & Changes Log — 9 to 5

> This document is a running log maintained throughout development. Each entry records scope shifts, design decisions, and refinements as they happen. Newest entries appear at the top.

---

## 2026-03-25 — Project Documentation Added

**What changed:**
- Created `plan.md` with milestones, AI tools disclosure, and a full task list.
- Wrote detailed `README.md` covering installation, controls, rules, project structure, and credits.
- Created this `refinements-changes.md` running log.
- Updated `requirements.txt` with descriptive comments.

**Why:**
- Course requirements mandate maintained documentation files throughout the project.

**Impact:**
- No code changes. Documentation-only addition.

---

## 2026-03-25 — Main Menu & Landing Page

**What changed:**
- Built a full-screen main menu system (`menu.py`) with custom background art from `GameArtImages/Backrounds & Menus/`.
- Added Play, Controls, Rules, and Close Game buttons with hover-scale effects.
- Implemented Controls overlay and Rules overlay sub-screens, each with a Back button to return to the start screen.
- Menu adapts to display resolution and supports keyboard shortcuts (Enter to play, Escape to quit/go back).

**Design decision:**
- Chose image-based buttons over text buttons to match the hand-drawn art style of the game.
- Menu is a blocking loop that runs before the game loop — keeps `GameApp.run()` clean.

---

## 2026-03-25 — Themed Art Pipeline & Asset Loader

**What changed:**
- Implemented `ArtLibrary` in `assets.py` — a recursive image loader that walks `GameArtImages/` and auto-classifies every image by theme and role.
- Theme detection inferred from folder names (e.g. `Bathroom Levels/` → Bathroom theme).
- Role detection inferred from filename keywords: `Obstacle *` → wall, `Goal Location *` → goal, `Character 1` → char_a, etc.
- All tile-like art auto-scaled to the current `tile_px` size. HUD art kept at original resolution.
- Fallback: if no art exists for a tile type, solid-colour rectangles are drawn instead.
- Added deterministic tile-art selection using position-based hashing — visuals are stable across frames without per-frame randomness.
- Decor images placed sparsely on empty tiles as overlays so all contributed art gets used.

**Design decision:**
- Convention-over-configuration approach: artists drop images into themed folders and the engine picks them up automatically, no manifest file needed.

---

## 2026-03-25 — Procedural Level Generator

**What changed:**
- Built `generator.py` with a `generate_level()` function that creates random solvable puzzles on demand.
- Generator places start positions, goals (with minimum Manhattan distance), and random wall/blocker obstacles at configurable densities per theme.
- Every generated level is validated by the BFS solver before being accepted.
- Added a desync-step quality filter: generated levels must require at least 2 moves where the characters diverge (one blocked, the other free). This prevents trivially easy puzzles.
- Par moves auto-calculated as optimal solution length + 2.
- Bound to the `G` key in-game for on-demand generation.

**Design decision:**
- Generate-and-test approach (up to 250 attempts) rather than constructive generation. Simpler to implement and the solver guarantees quality.
- Theme configs define grid size and obstacle density — Elevator levels are small and sparse, Parking Lot levels are large and open.

---

## 2026-03-25 — BFS Solver & Level Validation

**What changed:**
- Implemented `solve_level_bfs()` in `solver.py` — a breadth-first search over the (posA, posB) state space.
- Solver explores up to 250k states for static levels and 120k for generated levels.
- Added `count_desync_steps()` to measure puzzle quality (how many moves require asymmetric character behaviour).
- All 5 static levels are validated as solvable at load time — if a future edit breaks a level, the game raises an error immediately rather than shipping an impossible puzzle.

**Design decision:**
- BFS chosen over A* because the state space is small enough and BFS guarantees shortest path (needed for accurate par targets).
- Fall-off transitions are dead-ends in the search (not explored further), matching the game rule that falling resets the level.

---

## 2026-03-25 — 5 Handcrafted Static Levels

**What changed:**
- Designed 5 themed levels in `levels.py` using ASCII-art notation:
  1. **Bathroom** (7×9, par 8) — introductory level, small grid, simple wall layout.
  2. **Office** (11×13, par 12) — open floor with desk-like wall clusters.
  3. **Elevator** (13×13, par 30) — tight maze corridors, longest solve path.
  4. **Break Room** (13×13, par 16) — medium density, winding paths.
  5. **Parking Lot** (15×17, par 18) — largest grid, barrier-heavy layout.
- Each level uses the `parse_ascii_level()` parser in `level.py` with legend: `.` empty, `#` wall, `X` blocker, `a`/`b` starts, `A`/`B` goals, `!` hazard, `?` interactive.

**Design decision:**
- Difficulty ramps through grid size and wall complexity, not through new mechanics — keeps the learning curve smooth.
- Level progression is locked: players must complete the current level to advance. Bracket-key navigation was disabled to enforce this.

---

## 2026-03-25 — Core Movement System & Game Loop

**What changed:**
- Implemented dual-character synchronised movement in `movement.py` — both characters receive the same directional input each step.
- Movement rules:
  - If a character's next tile is a wall/blocker, that character stays; the other still moves.
  - If either character would leave the grid, both "fall" and the level resets.
  - If both characters would land on the same tile, neither moves (overlap prevention).
- Built the main game loop in `app.py` with 60 FPS cap, keyboard and mouse input handling, and the full rendering pipeline.
- HUD panel displays level info, move count, par, star rating (3 stars at/under par, 2 within +3, 1 otherwise), and best scores.
- Screen flash feedback: red on fall, yellow on overlap, green on level complete.
- Auto-advance to next level after 700ms on completion.
- Auto-fit layout scales the grid to fit the player's display resolution.
- Zoom in/out with `+`/`-` keys.

**Design decision:**
- Step-based (not real-time) movement chosen because puzzle games benefit from deliberate, unpressured input.
- Off-grid fall killing both characters (not just the one who fell) creates meaningful boundary awareness — the grid edge is the primary hazard, not walls.
- Overlap prevention uses "both stay" rather than pushing or swapping — simpler mental model for the player.

---

## Design Decisions Summary

| Decision | Rationale |
|----------|-----------|
| Step-based (not real-time) movement | Puzzle games benefit from deliberate input; avoids timing pressure. |
| Off-grid fall kills both characters | Creates meaningful boundary awareness — the grid edge is the primary hazard. |
| Overlap prevention (both stay) | Simpler than pushing or swapping; keeps mental model predictable. |
| BFS solver validates all levels | Guarantees no impossible puzzles ship; also provides par targets. |
| Procedural generator requires desync | Ensures generated puzzles are interesting (not trivially solvable by moving in one direction). |
| Art loaded by folder/filename convention | Artists can drop images into themed folders without touching code. |
| Level progression is linear (locked) | Players must beat the current level to advance; bracket-key navigation disabled. |
| Image-based menu buttons | Matches the hand-drawn art style; more polished than text UI. |
| Generate-and-test level creation | Simpler than constructive generation; solver guarantees quality. |
