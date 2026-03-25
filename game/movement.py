from __future__ import annotations

from dataclasses import dataclass

from game.level import Level
from game.types import DIRS, Vec2


@dataclass(slots=True)
class StepResult:
    moved: bool
    fell_off: bool
    overlapped_prevented: bool
    a_from: Vec2
    b_from: Vec2
    a_to: Vec2
    b_to: Vec2


def move_characters(
    level: Level,
    a_pos: Vec2,
    b_pos: Vec2,
    direction: str,
) -> StepResult:
    """
    Implements the exact rules from the prompt:
    - Compute next positions for both from the same direction.
    - If either goes off-grid => both "die" (caller must reset level); no other resets.
    - If next is blocked for a character, that character stays (independent).
    - If next positions are equal => both stay (overlap prevention).
    """
    if direction not in DIRS:
        raise ValueError(f"Unknown direction: {direction}")
    d = DIRS[direction]

    a_from = a_pos
    b_from = b_pos
    a_next = a_pos + d
    b_next = b_pos + d

    if (not level.in_bounds(a_next)) or (not level.in_bounds(b_next)):
        return StepResult(
            moved=False,
            fell_off=True,
            overlapped_prevented=False,
            a_from=a_from,
            b_from=b_from,
            a_to=a_from,
            b_to=b_from,
        )

    if level.is_blocked(a_next):
        a_next = a_from
    if level.is_blocked(b_next):
        b_next = b_from

    overlapped = a_next == b_next
    if overlapped:
        a_next = a_from
        b_next = b_from

    moved = (a_next != a_from) or (b_next != b_from)
    return StepResult(
        moved=moved,
        fell_off=False,
        overlapped_prevented=overlapped,
        a_from=a_from,
        b_from=b_from,
        a_to=a_next,
        b_to=b_next,
    )


def goals_met(level: Level, a_pos: Vec2, b_pos: Vec2) -> bool:
    return level.tile_at(a_pos).name == "GOAL_A" and level.tile_at(b_pos).name == "GOAL_B"

