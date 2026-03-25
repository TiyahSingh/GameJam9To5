# 9 to 5 (Python)

2D top-down, grid-based puzzle game where you control **two office workers simultaneously** with a single input.

## Run

```powershell
py -m pip install -r requirements.txt
py main.py
```

## Controls

- **Move**: `WASD` or Arrow Keys (one tile per input)
- **Mouse**: click a tile to convert the click into a movement direction (relative to Character A)
- **Reset level**: `R`
- **Prev/Next level**: `[` and `]`
- **Generate a new procedural level**: `G`

## Rules (implemented)

- Both characters respond to one input (synchronous, step-based).
- If a character attempts to move into a wall/blocked tile, that character stays; the other may still move.
- If **either** character would move off-grid, **both** fall and the level resets (this is the only fail/reset condition).
- Characters cannot occupy the same tile; if a move would overlap, both stay for that step.
- Win when A is on Goal A and B is on Goal B.

