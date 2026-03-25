from __future__ import annotations

from dataclasses import dataclass

from game.types import Tile, Vec2


@dataclass(slots=True)
class Character:
    id: str  # "A" or "B"
    start: Vec2
    pos: Vec2

    def reset(self) -> None:
        self.pos = self.start


@dataclass(slots=True)
class Level:
    theme: str
    grid: list[list[Tile]]
    a_start: Vec2
    b_start: Vec2
    par_moves: int | None = None

    @property
    def h(self) -> int:
        return len(self.grid)

    @property
    def w(self) -> int:
        return len(self.grid[0]) if self.grid else 0

    def in_bounds(self, p: Vec2) -> bool:
        return 0 <= p.x < self.w and 0 <= p.y < self.h

    def tile_at(self, p: Vec2) -> Tile:
        return self.grid[p.y][p.x]

    def is_blocked(self, p: Vec2) -> bool:
        t = self.tile_at(p)
        return t in (Tile.WALL, Tile.BLOCKER)

    def find_goal_a(self) -> Vec2:
        for y in range(self.h):
            for x in range(self.w):
                if self.grid[y][x] == Tile.GOAL_A:
                    return Vec2(x, y)
        raise ValueError("Level has no GOAL_A")

    def find_goal_b(self) -> Vec2:
        for y in range(self.h):
            for x in range(self.w):
                if self.grid[y][x] == Tile.GOAL_B:
                    return Vec2(x, y)
        raise ValueError("Level has no GOAL_B")


def parse_ascii_level(
    *,
    theme: str,
    rows: list[str],
    par_moves: int | None = None,
) -> Level:
    """
    Legend:
      . empty
      # wall
      X blocker
      a start A
      b start B
      A goal A
      B goal B
      ! hazard (non-fatal; rendered only)
      ? interactive (non-blocking; rendered only)
    """
    if not rows:
        raise ValueError("rows is empty")
    w = len(rows[0])
    if any(len(r) != w for r in rows):
        raise ValueError("rows must be same width")

    grid: list[list[Tile]] = []
    a_start: Vec2 | None = None
    b_start: Vec2 | None = None

    for y, r in enumerate(rows):
        out_row: list[Tile] = []
        for x, ch in enumerate(r):
            if ch == ".":
                out_row.append(Tile.EMPTY)
            elif ch == "#":
                out_row.append(Tile.WALL)
            elif ch == "X":
                out_row.append(Tile.BLOCKER)
            elif ch == "A":
                out_row.append(Tile.GOAL_A)
            elif ch == "B":
                out_row.append(Tile.GOAL_B)
            elif ch == "a":
                a_start = Vec2(x, y)
                out_row.append(Tile.EMPTY)
            elif ch == "b":
                b_start = Vec2(x, y)
                out_row.append(Tile.EMPTY)
            elif ch == "!":
                out_row.append(Tile.HAZARD)
            elif ch == "?":
                out_row.append(Tile.INTERACTIVE)
            else:
                raise ValueError(f"Unknown tile char {ch!r}")
        grid.append(out_row)

    if a_start is None or b_start is None:
        raise ValueError("Level must include both 'a' and 'b' start positions")

    return Level(theme=theme, grid=grid, a_start=a_start, b_start=b_start, par_moves=par_moves)

