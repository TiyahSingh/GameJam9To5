from __future__ import annotations

from game.level import Level, parse_ascii_level


def static_levels() -> list[Level]:
    # Handcrafted intro-to-advanced set. Goals are 'A' and 'B', starts are 'a' and 'b'.
    levels = [
        parse_ascii_level(
            theme="Bathroom",
            par_moves=8,
            rows=[
                "#########",
                "#..A....#",
                "#.###.#.#",
                "#a..#.#b#",
                "#.###.#.#",
                "#....B..#",
                "#########",
            ],
        ),
        parse_ascii_level(
            theme="Office",
            par_moves=12,
            rows=[
                "#############",
                "#a..........#",
                "#..##..##..A#",
                "#...........#",
                "#..##..##...#",
                "#...........#",
                "#..##..##..B#",
                "#...........#",
                "#b..........#",
                "#...........#",
                "#############",
            ],
        ),
        parse_ascii_level(
            theme="Elevator",
            par_moves=30,
            rows=[
                "#############",
                "#a..#...#...#",
                "#.#.#.#.#.#.#",
                "#.#...#...#A#",
                "#.###.###...#",
                "#...#.....#.#",
                "#.#.###.#.#.#",
                "#.#.....#.#.#",
                "#.###...#.#.#",
                "#...#...#..b#",
                "#.#...#.....#",
                "#B..........#",
                "#############",
            ],
        ),
        parse_ascii_level(
            theme="Break Room",
            par_moves=16,
            rows=[
                "#############",
                "#a....#.....#",
                "#.###.#.###.#",
                "#...#...#A#.#",
                "###.#####.#.#",
                "#...#...#.#.#",
                "#.###.#.#.#.#",
                "#.....#...#.#",
                "#.#####.###.#",
                "#.#B..#.....#",
                "#.#.###.###.#",
                "#.....#....b#",
                "#############",
            ],
        ),
        parse_ascii_level(
            theme="Parking Lot",
            par_moves=18,
            rows=[
                "#################",
                "#a......#.......#",
                "#.#####.#.#####.#",
                "#.....#.#.#.....#",
                "#####.#.#.#.#####",
                "#...#.#.#.#.#...#",
                "#.#.#.#.#.#.#.#.#",
                "#.#...#...#...#.#",
                "#.#####.###.#####",
                "#.....#..A#.....#",
                "#.###.#####.###.#",
                "#...#.....#...#.#",
                "#.#####.#.#####.#",
                "#.......#......b#",
                "#.....B.........#",
                "#################",
            ],
        ),
    ]

    # Guarantee: every handcrafted level is solvable.
    # (Procedural levels are also validated, but this protects against future edits.)
    from game.solver import solve_level_bfs

    for i, lvl in enumerate(levels, start=1):
        res = solve_level_bfs(lvl, max_expansions=250_000)
        if not res.found:
            raise ValueError(f"Static level {i} ({lvl.theme}) is unsolvable; adjust layout.")

    return levels

