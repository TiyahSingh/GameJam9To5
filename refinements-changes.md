# Refinements & Changes Log — 9 to 5

> This document is a running log maintained throughout development. Each entry records scope shifts, design decisions, and refinements as they happen. Newest entries appear at the top.

---

## 2026-03-26 — HUD Button Images Replace Text Controls

**What changed:**
- Replaced all text-based control instructions in the right-side HUD panel with custom button images from the art assets:
  - **Reset Level** button (`New UI/Reset Level Button.png`) — replaces "R: reset (no penalty)" text
  - **Generate New Level** button (`New UI/Generate New Level Button.png`) — replaces "G: generate level" text
  - **Zoom In / Zoom Out** buttons (`New UI/Zoom In Button.png`, `New UI/Zoom Out Button.png`) — replace "+ / - : zoom in / out" text, placed side-by-side
  - **Exit (Close Game)** button (`UI and Buttons/Close Game Button.png`) — placed in the top-right corner of the HUD panel
- Removed all text lines from the "Controls" section: "WASD / Arrows: move", "Mouse click: move (from A)", "R: reset", "Progression: automatic", "G: generate level", "+ / - : zoom", "Esc: quit".
- Each button is clickable and triggers the same action as its keyboard equivalent (Reset → R, Generate → G, Zoom In → +, Zoom Out → −, Exit → Esc).
- All keyboard inputs remain fully functional and unchanged.

**Technical detail:**
- Added `_crop_and_scale()` static method to `GameApp`: uses `Surface.get_bounding_rect()` to crop transparent padding from the large canvas images (2000×1409 and 940×788), then `smoothscale`s to fit within the HUD width.
- Added `_load_hud_buttons()` method: loads 5 button PNGs, crops and scales them, stores surfaces as instance attributes. Called on init, level load, and zoom change.
- Button rects (`self.hud_btn_rects`) are computed each frame in `_draw_hud()` and checked for clicks in `_on_mouse_click()`.
- `_on_mouse_click()` now returns `False` to signal quit (for the exit button), `None` otherwise. The game loop checks this return value.
- Pill-shaped buttons (Reset, Generate) are scaled to `hud_w_px - 32` wide × 48px tall max; circular buttons (Zoom, Exit) to 44×44px max.

**Design decision:**
- Buttons are centered horizontally within the HUD panel for visual consistency.
- Zoom buttons placed side-by-side on one row to save vertical space.
- Exit button sits in the top-right corner of the screen, matching the menu's Close Game button placement.
- The title, level info, move count, par, stars, and best scores remain as text — only the control instructions were replaced with images.

---

## 2026-03-26 — Character Images on Non-Elevator Levels

**What changed:**
- Updated `assets.py` role detection to classify `Character 1.png` → `char_a` and `Character 2.png` → `char_b` from the `Usual Characters` folder.
- Updated `bucket_for_theme()` to inherit global character sprites into themed buckets that lack their own — all themes except Elevator now display the Usual Characters images instead of coloured rectangles with text labels.
- Elevator level retains its own themed character sprites (`Character 1 Elevator.png` / `Character 2 Elevator.jpg`).

**Impact:**
- Visual-only change. No movement or gameplay logic was modified.

---

## 2026-03-26 — AI Reflection, Ethics Declaration & References Added to README

**What changed:**
- Appended a comprehensive **AI Reflection** section to `README.md` addressing six key questions about the role of AI in this project:
  1. Where AI excelled and where it misled or limited the developer.
  2. How AI altered the creative and technical process.
  3. What would change about the AI collaboration next time.
  4. Ethical considerations around originality, transparency, and fair use.
  5. Whether AI-generated assets were credited appropriately.
  6. Whether reliance on AI ever felt ethically questionable.
- Added a formal **AI Attribution, Ethical & Fair Use Declaration** covering authorship, attribution, IP compliance, and human oversight — signed by the project author.
- Added a full **References** section (Harvard IIE Anglia Style) with 10 academic and industry citations supporting the reflections.

**Why:**
- Course requirements (GADS7331 Part 1 – Game Jam) mandate a reflective write-up on the ethical and practical use of AI tools during development.
- Transparency is a core project value — the declaration makes it unambiguous how AI contributed and that all work was critically reviewed.

**Impact:**
- Documentation-only change. No game code was modified.
- `README.md` grew from 134 lines to ~202 lines. The new sections sit after the existing "AI Tools Used" block, forming a natural continuation.

---

## 2026-03-26 — Repository Maintenance & Documentation Enrichment

**What changed:**
- Updated `refinements-changes.md` (this file) with expanded technical detail across all entries: exact module names, function signatures, data-structure choices, and algorithmic parameters are now documented.
- Updated `requirements.txt` with per-module import mapping, Python version compatibility notes, and platform-specific guidance.
- Added `.gitignore` to exclude `__pycache__/`, `.pyc` files, IDE folders, and OS junk files — keeping the repository clean for future commits.

**Why:**
- The documentation now serves as a standalone technical reference that a reviewer can read without needing to open the source code.
- A `.gitignore` prevents binary/cache artefacts from polluting the commit history.

**Impact:**
- No game code was modified. Repository hygiene and documentation quality improved.

---

## 2026-03-25 — Main Menu & Landing Page

**What changed:**
- Built a full-screen main menu system in `menu.py` (~161 lines) consisting of three classes:
  - `MainMenu` — top-level controller that manages state transitions (Start → Controls/Rules → Start) via a `_MenuState` enum.
  - `_Button` — lightweight wrapper around a `pygame.Surface` that handles hit-testing (`collidepoint`), hover detection, and a 1.08× scale-up animation on hover.
  - `MenuResult` — enum (`NONE`, `PLAY`, `QUIT`) returned to `GameApp` after each event.
- Menu loads six custom PNG assets from the art folders:
  - **Backgrounds:** `Start Screen.png`, `Controls Menu Background.png`, `Rules Menu Background.png` (from `GameArtImages/Backrounds & Menus/`).
  - **Buttons:** `Play Button.png`, `Controls Button.png`, `Rules Button.png`, `Back Button.png`, `Close Game Button.png` (from `GameArtImages/UI and Buttons/`).
- All backgrounds are `smoothscale`-d to a capped resolution (`min(940, display_w)` × `min(788, display_h)`) so the menu fits any screen.
- Button positions are computed relative to `menu_w` / `menu_h` using percentage offsets (e.g. Play at 82% height, Controls offset by −20% width) — this keeps the layout proportional on different displays.
- Keyboard shortcuts: `Enter` → Play, `Escape` → back or quit.
- The menu runs its own blocking event loop inside `GameApp._run_menu()` at 60 FPS; once the player clicks Play (or presses Enter), control transfers to the main game loop.

**Design decision:**
- Chose image-based buttons over text buttons to match the hand-drawn art style of the game.
- Menu is a blocking loop that runs before the game loop — keeps `GameApp.run()` clean and avoids mixing menu state with gameplay state.
- `_Button` applies a simple 1.08× scale on hover instead of sprite-swapping; this keeps the asset count low while still providing visual feedback.

---

## 2026-03-25 — Themed Art Pipeline & Asset Loader

**What changed:**
- Implemented `ArtLibrary` class in `assets.py` (~159 lines) — a recursive image loader that walks the entire `GameArtImages/` directory tree using `os.walk()`.
- **Theme detection** (`_theme_from_path`): folder path segments are normalised (lowercased, hyphens/spaces → underscores) and matched against keywords: `elevator`, `office`, `bathroom`/`restroom`, `break`, `parking`. Images outside themed folders go into a `global_bucket`.
- **Role detection** (`_role_from_name`): the full relative path + filename is scanned for keywords that map to 12 art roles:
  - `char_a`, `char_b` — player character sprites (also matches `Character_1_Elevator`, `Worker_A`, etc.)
  - `wall` / `blocker` — maze obstacles (also matches `Obstacle *`)
  - `goal_a`, `goal_b`, `goal` — goal tiles (matches `Goal_Location_Toilet_1`, `Desk_A`, etc.)
  - `hazard`, `interactive` — special tiles
  - `floor` — ground tiles
  - `hud` — UI elements (kept at original resolution)
  - `decor` — catch-all for any image that doesn't match another role
- All tile-like art is `smoothscale`-d to the current `tile_px` size on load. HUD art is kept at original resolution for overlay use.
- **`ArtBucket`** — a `@dataclass(slots=True)` with 12 lists (one per role). Each theme gets its own bucket; unthemed art goes into `global_bucket`.
- `bucket_for_theme()` falls back to `global_bucket` when no theme-specific art exists, and promotes `blocker` images to `wall` if no wall art is found — maximising visual coverage.
- **Deterministic tile-art selection**: tile coordinates are hashed (`(x * 7 + y * 13) % len(sprites)`) to pick a consistent image per position. This avoids per-frame randomness and keeps visuals stable.
- **Decor overlay system**: empty tiles have a 1-in-23 chance (deterministic via `(x * 97 + y * 193 + level_idx * 389) % 23`) of receiving a decor image overlay, ensuring every contributed image can appear in-game even if it doesn't match a specific tile role.
- Fallback rendering: if no art exists for a tile type, solid-colour rectangles (e.g. `(80, 84, 96)` for walls, `(68, 120, 210)` for Goal A) are drawn with `border_radius=6` for a polished look.
- Supported image formats: `.png`, `.jpg`, `.jpeg`, `.webp`, `.gif`. Unreadable files are silently skipped (`try/except` around `pygame.image.load`).

**Design decision:**
- Convention-over-configuration approach: artists drop images into themed folders and the engine picks them up automatically — no manifest file or config needed.
- The catch-all `decor` role ensures zero art goes unused; even misnamed files will appear as sparse environmental decoration.

---

## 2026-03-25 — Procedural Level Generator

**What changed:**
- Built `generator.py` (~110 lines) with two public functions:
  - `generate_level(rng, cfg)` — creates a random solvable puzzle matching a `GenConfig`.
  - `random_theme_config(rng)` — picks a random theme and returns a pre-tuned `GenConfig`.
- **`GenConfig`** dataclass encapsulates: grid width/height, theme name, wall density (float 0–1), blocker density, max generation attempts (default 250), and minimum required desync steps (default 2).
- **Five theme presets** in the `THEMES` list, each with tuned grid sizes and obstacle densities:
  - Elevator: 7×9, wall 10%, blocker 3% (small, sparse)
  - Office: 9×13, wall 16%, blocker 6%
  - Bathroom: 9×13, wall 18%, blocker 5%
  - Break Room: 10×14, wall 14%, blocker 6%
  - Parking Lot: 12×17, wall 12%, blocker 4% (large, open)
- **Generation algorithm** (per attempt):
  1. Create an empty grid of `Tile.EMPTY`.
  2. Place `a_start` randomly; temporarily mark it to avoid co-placement, then place `b_start`.
  3. Place `goal_a` and `goal_b` with a minimum Manhattan distance of `(w + h) // 4` from their respective starts — this forces non-trivial pathfinding.
  4. Scatter `Tile.WALL` and `Tile.BLOCKER` at configured densities, never overwriting starts or goals.
  5. Validate with `solve_level_bfs(max_expansions=120_000)`.
  6. Run `count_desync_steps()` on the solution — reject if fewer than 2 desync steps (moves where one character is blocked and the other isn't). This prevents trivially easy puzzles.
  7. Set `par_moves = len(solution) + 2`.
- If all 250 attempts fail, a `RuntimeError` is raised (never observed in practice with the current density ranges).
- Bound to the `G` key in `GameApp._on_keydown()` via `_generate_and_load()`, which appends the new level to the level list and immediately loads it.

**Design decision:**
- Generate-and-test approach rather than constructive generation. Simpler to implement, and the solver provides a hard correctness guarantee.
- The desync filter is the key quality gate — without it, many generated levels could be solved by moving in a single direction repeatedly.
- Theme configs define grid size and obstacle density independently, so each theme feels distinct even when procedurally generated.

---

## 2026-03-25 — BFS Solver & Level Validation

**What changed:**
- Implemented `solver.py` (~76 lines) with two functions:
  - `solve_level_bfs(level, max_expansions)` — BFS over the composite `(posA, posB)` state space. Returns a `SolveResult` containing `found` (bool), `moves` (list of direction strings), and `expanded` (number of states explored).
  - `count_desync_steps(level, moves)` — replays a move sequence and counts steps where one character moved and the other was blocked. Used as a quality metric for the procedural generator.
- **State representation**: `State(a: Vec2, b: Vec2)` — a frozen dataclass serving as the BFS node and dict key. The state space is `O(W² × H²)` in the worst case.
- **BFS implementation**: uses `collections.deque` for the frontier and a `dict[State, tuple | None]` for the visited/predecessor map. At each state, all four directions are tried; `move_characters()` is called to compute the transition. Fall-off transitions are skipped (dead-ends), matching the game rule that falling resets the level.
- **Path reconstruction**: on finding the goal state, the solver walks the predecessor chain backwards and reverses the result, producing the shortest move list.
- **Expansion limits**: 250,000 states for static level validation (called once at startup), 120,000 for procedural generation (called repeatedly, so a lower cap keeps generation fast).
- All 5 static levels are validated as solvable at load time in `static_levels()` — if a future edit breaks a level, the game raises a `ValueError` immediately rather than shipping an impossible puzzle.

**Design decision:**
- BFS chosen over A\* because the state space is small enough (typical levels expand fewer than 50,000 states) and BFS guarantees the shortest path — needed for accurate par targets.
- Fall-off transitions are dead-ends in the search (not explored further). This is correct because falling resets the level in-game and is never part of a valid solution.

---

## 2026-03-25 — 5 Handcrafted Static Levels

**What changed:**
- Designed 5 themed levels in `levels.py` (~112 lines) using ASCII-art notation, each constructed via `parse_ascii_level()` from `level.py`:
  1. **Bathroom** (7 rows × 9 cols, par 8) — introductory level with a small grid and simple wall layout. Starts in opposite corners, goals separated by a central wall corridor.
  2. **Office** (11 rows × 13 cols, par 12) — open floor plan with desk-like 2×2 wall clusters arranged in a grid pattern. More room to manoeuvre but more complex asymmetry.
  3. **Elevator** (13 rows × 13 cols, par 30) — dense maze with tight single-tile corridors and many turns. Longest optimal solve path of all static levels; demands careful planning.
  4. **Break Room** (13 rows × 13 cols, par 16) — medium-density layout with winding paths and dead-end traps. Tests the player's ability to avoid boundary falls.
  5. **Parking Lot** (16 rows × 17 cols, par 18) — largest grid with barrier-heavy columns. Wide open spaces between obstacle clusters make it deceptively tricky due to fall-off risk on the large perimeter.
- ASCII legend (parsed by `parse_ascii_level()` in `level.py`):
  - `.` → `Tile.EMPTY`, `#` → `Tile.WALL`, `X` → `Tile.BLOCKER`
  - `a` / `b` → start positions for Character A / B (stored as `Vec2`, tile becomes `EMPTY`)
  - `A` / `B` → `Tile.GOAL_A` / `Tile.GOAL_B`
  - `!` → `Tile.HAZARD`, `?` → `Tile.INTERACTIVE` (non-blocking decorative tiles)
- At load time, `static_levels()` validates every level with `solve_level_bfs(max_expansions=250_000)`. If any level is unsolvable, a `ValueError` is raised with the level number and theme, catching regressions immediately.

**Design decision:**
- Difficulty ramps through grid size and wall complexity, not through new mechanics — keeps the learning curve smooth and avoids tutorial friction.
- Level progression is locked: players must complete the current level to advance. The bracket-key (`[`/`]`) navigation handler exists in `_on_keydown()` but returns `True` immediately (no-op), enforcing linear progression.

---

## 2026-03-25 — Core Movement System & Game Loop

**What changed:**

*Movement system — `movement.py` (~78 lines):*
- `move_characters(level, a_pos, b_pos, direction)` → `StepResult` — the single function that implements all movement rules.
- `StepResult` dataclass carries: `moved`, `fell_off`, `overlapped_prevented`, `a_from`, `b_from`, `a_to`, `b_to`.
- Movement rules (applied in order):
  1. Compute `a_next = a_pos + DIRS[direction]`, same for B.
  2. **Boundary check**: if either next position is out of bounds → `fell_off = True`, both positions reset to their `_from` values. The caller (`GameApp._step`) resets the entire level.
  3. **Wall/blocker check** (independent): if `level.is_blocked(a_next)`, A stays at `a_from`; same for B. This is per-character — one can be blocked while the other moves.
  4. **Overlap prevention**: if `a_next == b_next` after wall checks, both revert to `_from`. A yellow flash signals this to the player.
- `goals_met()` helper checks win condition: `tile_at(a_pos) == GOAL_A and tile_at(b_pos) == GOAL_B`.

*Game loop — `app.py` (~463 lines):*
- `GameApp` class manages the full lifecycle: menu → game loop → quit.
- **60 FPS cap** via `pygame.time.Clock.tick(60)`.
- **Input handling**: keyboard (WASD / arrows for movement, R for reset, G for generate, +/− for zoom, Esc to quit) and mouse (click computes direction relative to Character A using `abs(dx) > abs(dy)` to determine axis priority).
- **HUD panel** (dark sidebar, right side): displays level number, theme, move count, par target, star rating, best scores, and a controls reference. Rendered with `pygame.font.SysFont("consolas", 18/26)`.
- **Star rating**: 3 stars if moves ≤ par, 2 stars if moves ≤ par + 3, 1 star otherwise.
- **Screen flash feedback**: red `(220, 70, 70)` for 220ms on fall, yellow `(230, 190, 70)` for 120ms on overlap, green `(70, 200, 120)` for 250ms on level complete. Implemented as a semi-transparent `SRCALPHA` overlay with `alpha=90`.
- **Auto-advance**: after level completion, `auto_advance_ms` is set to 700; once elapsed, `_load_level(idx + 1)` fires automatically.
- **Auto-fit layout** (`_fit_layout_to_screen`): queries `pygame.display.Info()` for screen resolution, computes the largest tile size (clamped 40–128 px) that fits both the grid and HUD within the display, and adjusts `tile_px` accordingly. User zoom offset (`+`/`−` keys, ±4 px per press, clamped −24 to +36) is applied on top.
- **Theme palette**: each theme maps to a unique floor colour (e.g. Bathroom → `(232, 236, 238)`) with a white background.
- `LevelStats` dataclass tracks per-level best moves and best stars, persisted in `self.stats` (dict keyed by level index) for the duration of the session.

*Data model — `level.py` (~119 lines):*
- `Character` dataclass: `id` (str), `start` (Vec2), `pos` (Vec2), with a `reset()` method.
- `Level` dataclass: `theme`, `grid` (2D list of `Tile`), `a_start`, `b_start`, `par_moves`. Properties `w` and `h` derived from the grid. Methods: `in_bounds()`, `tile_at()`, `is_blocked()`, `find_goal_a()`, `find_goal_b()`.

*Shared types — `types.py` (~43 lines):*
- `Vec2(x, y)` — frozen dataclass with `__add__` for vector arithmetic.
- `Tile` enum: `EMPTY`, `WALL`, `BLOCKER`, `GOAL_A`, `GOAL_B`, `HAZARD`, `INTERACTIVE`.
- `DIRS` — direction name → `Vec2` mapping (`up → (0,−1)`, etc.).
- `manhattan(a, b)` — Manhattan distance utility used by the generator.
- `iter_neighbors(p)` — yields `(name, p + d)` for all four cardinal directions.

**Design decision:**
- Step-based (not real-time) movement chosen because puzzle games benefit from deliberate, unpressured input.
- Off-grid fall killing both characters (not just the one who fell) creates meaningful boundary awareness — the grid edge is the primary hazard, not walls.
- Overlap prevention uses "both stay" rather than pushing or swapping — simpler mental model for the player.
- The `StepResult` dataclass decouples movement logic from rendering/state management, making the movement system independently testable.

---

## 2026-03-24 — Project Documentation Added

**What changed:**
- Created `plan.md` with milestones, AI tools disclosure, and a full task list covering all development phases.
- Wrote detailed `README.md` covering: game concept, feature list, installation steps (clone, pip install, run), controls table, game rules, full project structure tree, dependency table, credits, and AI tools disclosure.
- Created this `refinements-changes.md` running log to document every scope shift and design decision chronologically.
- Updated `requirements.txt` with descriptive header comments, per-library documentation (homepage, licence, purpose), and a list of all standard-library modules used by the project for completeness.

**Why:**
- Course requirements (GADS7331 Part 1 – Game Jam) mandate maintained documentation files throughout the project. These files also serve as evidence of iterative development and reflective practice.

**Impact:**
- No code changes. Documentation-only addition. Four files created/updated: `plan.md`, `README.md`, `refinements-changes.md`, `requirements.txt`.

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
| `@dataclass(slots=True)` throughout | Reduces memory footprint and attribute access time for frequently-created objects like `Vec2`, `State`, `StepResult`. |
| Frozen `Vec2` and `State` | Immutability allows safe use as dictionary keys (BFS visited set) and prevents accidental mutation of position data. |
| Tile enum (not raw ints) | Type safety and readable comparisons (`Tile.WALL` vs magic number `1`). |
| `smoothscale` over `scale` | Better visual quality at the cost of marginally slower asset loading (one-time cost at startup). |
| 60 FPS cap with step-based input | Provides smooth flash/hover animations while keeping input discrete — no accidental double-moves. |
| Session-only stats (no save file) | Keeps the scope appropriate for a game jam; avoids file I/O complexity and save-corruption edge cases. |

---

## Module Summary

| File | Lines | Purpose | Key exports |
|------|-------|---------|-------------|
| `main.py` | 20 | Entry point; initialises Pygame, runs `GameApp`, ensures `pygame.quit()` via `finally` | `main()` |
| `game/types.py` | 43 | Shared value types and constants | `Vec2`, `Tile`, `DIRS`, `manhattan()`, `iter_neighbors()` |
| `game/level.py` | 119 | Level and Character data models; ASCII level parser | `Level`, `Character`, `parse_ascii_level()` |
| `game/levels.py` | 112 | 5 handcrafted static levels; BFS validation at load time | `static_levels()` |
| `game/movement.py` | 78 | Dual-character movement logic with boundary, wall, and overlap rules | `move_characters()`, `StepResult`, `goals_met()` |
| `game/solver.py` | 76 | BFS solver over (posA, posB) state space; desync quality metric | `solve_level_bfs()`, `count_desync_steps()`, `SolveResult` |
| `game/generator.py` | 110 | Procedural level generator with solver validation and desync filtering | `generate_level()`, `random_theme_config()`, `GenConfig` |
| `game/assets.py` | 159 | Recursive art loader; theme/role classification by folder/filename keywords | `ArtLibrary`, `ArtBucket` |
| `game/menu.py` | 161 | Full-screen main menu with Play, Controls, Rules, Close buttons and overlays | `MainMenu`, `MenuResult` |
| `game/app.py` | 463 | Game loop, rendering, HUD, input handling, auto-fit display, zoom | `GameApp`, `LevelStats` |
