from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable


@dataclass(frozen=True, slots=True)
class Vec2:
    x: int
    y: int

    def __add__(self, other: "Vec2") -> "Vec2":
        return Vec2(self.x + other.x, self.y + other.y)


class Tile(Enum):
    EMPTY = 0
    WALL = 1
    BLOCKER = 2
    GOAL_A = 3
    GOAL_B = 4
    HAZARD = 5
    INTERACTIVE = 6


DIRS: dict[str, Vec2] = {
    "up": Vec2(0, -1),
    "down": Vec2(0, 1),
    "left": Vec2(-1, 0),
    "right": Vec2(1, 0),
}


def manhattan(a: Vec2, b: Vec2) -> int:
    return abs(a.x - b.x) + abs(a.y - b.y)


def iter_neighbors(p: Vec2) -> Iterable[tuple[str, Vec2]]:
    for name, d in DIRS.items():
        yield name, p + d

