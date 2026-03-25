from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from game.level import Level
from game.movement import StepResult, move_characters
from game.types import Vec2


@dataclass(frozen=True, slots=True)
class State:
    a: Vec2
    b: Vec2


@dataclass(slots=True)
class SolveResult:
    found: bool
    moves: list[str]
    expanded: int


def solve_level_bfs(level: Level, *, max_expansions: int = 200_000) -> SolveResult:
    start = State(level.a_start, level.b_start)

    q: deque[State] = deque([start])
    prev: dict[State, tuple[State, str, StepResult] | None] = {start: None}
    expanded = 0

    while q:
        s = q.popleft()
        expanded += 1
        if expanded > max_expansions:
            break

        if level.tile_at(s.a).name == "GOAL_A" and level.tile_at(s.b).name == "GOAL_B":
            # reconstruct
            path: list[str] = []
            cur = s
            while prev[cur] is not None:
                cur_prev, move, _step = prev[cur]
                path.append(move)
                cur = cur_prev
            path.reverse()
            return SolveResult(found=True, moves=path, expanded=expanded)

        for direction in ("up", "down", "left", "right"):
            step = move_characters(level, s.a, s.b, direction)
            if step.fell_off:
                continue  # falling off is a dead transition
            ns = State(step.a_to, step.b_to)
            if ns in prev:
                continue
            prev[ns] = (s, direction, step)
            q.append(ns)

    return SolveResult(found=False, moves=[], expanded=expanded)


def count_desync_steps(level: Level, moves: list[str]) -> int:
    a = level.a_start
    b = level.b_start
    desync = 0
    for m in moves:
        step = move_characters(level, a, b, m)
        if step.fell_off:
            return -1
        a_moved = step.a_to != a
        b_moved = step.b_to != b
        if a_moved != b_moved:
            desync += 1
        a, b = step.a_to, step.b_to
    return desync

