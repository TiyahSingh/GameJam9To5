from __future__ import annotations

import random
from dataclasses import dataclass

from game.level import Level
from game.solver import count_desync_steps, solve_level_bfs
from game.types import Tile, Vec2, manhattan


@dataclass(slots=True)
class GenConfig:
    w: int
    h: int
    theme: str
    wall_density: float = 0.16
    blocker_density: float = 0.06
    max_tries: int = 250
    require_desync_steps: int = 2


THEMES: list[tuple[str, tuple[int, int], tuple[float, float]]] = [
    ("Elevator", (7, 9), (0.10, 0.03)),
    ("Office", (9, 13), (0.16, 0.06)),
    ("Bathroom", (9, 13), (0.18, 0.05)),
    ("Break Room", (10, 14), (0.14, 0.06)),
    ("Parking Lot", (12, 17), (0.12, 0.04)),
]


def _empty_grid(w: int, h: int) -> list[list[Tile]]:
    return [[Tile.EMPTY for _ in range(w)] for _ in range(h)]


def _random_empty_cell(rng: random.Random, grid: list[list[Tile]]) -> Vec2:
    h = len(grid)
    w = len(grid[0])
    while True:
        p = Vec2(rng.randrange(w), rng.randrange(h))
        if grid[p.y][p.x] == Tile.EMPTY:
            return p


def generate_level(rng: random.Random, cfg: GenConfig) -> Level:
    """
    Generate a level by sampling obstacles, then validating with a BFS solver.
    Hard constraints:
      - Always solvable (validated)
      - Requires at least N desync steps in the solved path
      - No reliance on off-grid deaths (solver rejects fall-off transitions)
    """
    for _ in range(cfg.max_tries):
        grid = _empty_grid(cfg.w, cfg.h)

        a_start = _random_empty_cell(rng, grid)
        grid[a_start.y][a_start.x] = Tile.INTERACTIVE  # temp mark to avoid re-pick
        b_start = _random_empty_cell(rng, grid)
        grid[a_start.y][a_start.x] = Tile.EMPTY

        # Place goals far-ish to encourage planning.
        goal_a = _random_empty_cell(rng, grid)
        while manhattan(goal_a, a_start) < (cfg.w + cfg.h) // 4:
            goal_a = _random_empty_cell(rng, grid)
        grid[goal_a.y][goal_a.x] = Tile.GOAL_A

        goal_b = _random_empty_cell(rng, grid)
        while manhattan(goal_b, b_start) < (cfg.w + cfg.h) // 4 or goal_b == goal_a:
            goal_b = _random_empty_cell(rng, grid)
        grid[goal_b.y][goal_b.x] = Tile.GOAL_B

        # Obstacles (never overwrite starts/goals)
        for y in range(cfg.h):
            for x in range(cfg.w):
                p = Vec2(x, y)
                if p in (a_start, b_start, goal_a, goal_b):
                    continue
                roll = rng.random()
                if roll < cfg.wall_density:
                    grid[y][x] = Tile.WALL
                elif roll < cfg.wall_density + cfg.blocker_density:
                    grid[y][x] = Tile.BLOCKER

        lvl = Level(theme=cfg.theme, grid=grid, a_start=a_start, b_start=b_start, par_moves=None)
        try:
            # Ensure goals exist; level object already has them in grid.
            _ = lvl.find_goal_a()
            _ = lvl.find_goal_b()
        except Exception:
            continue

        res = solve_level_bfs(lvl, max_expansions=120_000)
        if not res.found:
            continue

        desync = count_desync_steps(lvl, res.moves)
        if desync < cfg.require_desync_steps:
            continue

        # Par target: solved length + small buffer (encourages efficiency but is fair).
        lvl.par_moves = max(1, len(res.moves) + 2)
        return lvl

    raise RuntimeError("Failed to generate a solvable level (try lowering densities or increasing max_tries)")


def random_theme_config(rng: random.Random) -> GenConfig:
    theme, (h, w), (wall_d, block_d) = rng.choice(THEMES)
    return GenConfig(w=w, h=h, theme=theme, wall_density=wall_d, blocker_density=block_d)

