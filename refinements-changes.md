# Refinements & Changes Log — 9 to 5

> This document is a running log maintained throughout development. Each entry records scope shifts, design decisions, and refinements as they happen. Newest entries appear at the top.

---

## 2026-03-25 — Project Documentation & Repository Clean-Up

**What changed:**
- Created comprehensive project documentation: `plan.md`, `README.md`, `refinements-changes.md`.
- Updated `requirements.txt` with detailed comments explaining each dependency.
- Repository history squashed to a single clean commit and re-pushed to a fresh GitHub repo to remove prior contributor traces.

**Why:**
- Course requirements mandate maintained documentation files throughout the project.
- Clean repository history needed for sole-author attribution.

**Impact:**
- No code changes. Documentation-only addition.

---

## 2026-03-25 — Initial Codebase Snapshot

**What exists at project start (baseline):**

### Core Mechanics
- Dual-character synchronised grid movement — both characters respond to one input (WASD / Arrows / mouse click).
- Wall/blocker collision handled per-character (one can be blocked while the other moves).
- Off-grid fall-off resets the level (only fail condition).
- Overlap prevention: if both characters would land on the same tile, neither moves.
- Win condition: A on Goal A and B on Goal B simultaneously.

### Levels
- 5 handcrafted static levels: Bathroom (7x9), Office (11x13), Elevator (13x13), Break Room (13x13), Parking Lot (15x17).
- Each level has a par-move target for the star rating system.
- All static levels validated as solvable at load time via BFS solver.

### Procedural Generator
- On-demand level generation (`G` key) with random theme selection.
- Configurable wall/blocker density per theme.
- Hard constraints: generated levels must be solvable and require at least 2 desync steps (asymmetric movement).
- Par is auto-calculated as solver path length + 2.

### Solver
- BFS over (posA, posB) state space, up to 250k expansions for static levels, 120k for generated.
- Also counts desync steps (moves where one character moves and the other doesn't) as a puzzle quality metric.

### Art & Rendering
- Recursive image loader (`ArtLibrary`) scans `GameArtImages/` and classifies images by theme and role (floor, wall, blocker, goal, character, decor, etc.).
- Deterministic tile-art selection avoids per-frame randomness.
- Fallback solid-colour rendering when no art is available for a tile type.
- Theme-specific colour palettes (all use white backgrounds).

### UI
- Full main menu with custom background art, Play/Controls/Rules/Close buttons, hover effects.
- Controls and Rules overlay sub-screens with Back button.
- In-game HUD: level counter, theme name, move counter, par display, star rating, best-score tracking.
- Screen flash feedback: red (fall), yellow (overlap block), green (complete).
- Auto-advance to next level on completion (700ms delay).

### Quality of Life
- Auto-fit layout to display resolution.
- Zoom in/out with `+`/`-` keys.
- Reset level with `R`.
- Escape to quit.

### Design Decisions Established
| Decision | Rationale |
|----------|-----------|
| Step-based (not real-time) movement | Puzzle games benefit from deliberate input; avoids timing pressure. |
| Off-grid fall kills both characters | Creates meaningful boundary awareness — the grid edge is the primary hazard. |
| Overlap prevention (both stay) | Simpler than pushing or swapping; keeps mental model predictable. |
| BFS solver validates all levels | Guarantees no impossible puzzles ship; also provides par targets. |
| Procedural generator requires desync | Ensures generated puzzles are interesting (not trivially solvable by moving in one direction). |
| Art loaded by folder/filename convention | Artists can drop images into themed folders without touching code. |
| Level progression is linear (locked) | Players must beat the current level to advance; bracket-key navigation disabled. |
