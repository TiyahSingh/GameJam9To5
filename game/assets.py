from __future__ import annotations

import os
from dataclasses import dataclass

import pygame


def _norm(s: str) -> str:
    return s.lower().replace("-", "_").replace(" ", "_")


def _theme_from_path(rel_parts: list[str]) -> str | None:
    joined = "_".join(_norm(p) for p in rel_parts)
    # Supports folder names like "Bathroom Levels".
    if "elevator" in joined:
        return "Elevator"
    if "office" in joined:
        return "Office"
    if "bathroom" in joined or "restroom" in joined:
        return "Bathroom"
    if "break" in joined:
        return "Break Room"
    if "parking" in joined:
        return "Parking Lot"
    return None


def _role_from_name(rel_parts: list[str], filename: str) -> str:
    joined = "_".join(_norm(p) for p in rel_parts + [filename])

    # Characters — order matters: more specific patterns first
    if "character_1" in joined or "char_a" in joined or "worker_a" in joined or "player_a" in joined or "a_sprite" in joined:
        return "char_a"
    if "character_2" in joined or "char_b" in joined or "worker_b" in joined or "player_b" in joined or "b_sprite" in joined:
        return "char_b"

    # Tiles — "Obstacle *" images from each theme folder render as maze walls
    if "obstacle" in joined:
        return "wall"
    if "wall" in joined:
        return "wall"
    if "block" in joined or "blocker" in joined:
        return "blocker"
    if "goal_location_toilet_1" in joined or "toilet_1" in joined or "toilet1" in joined:
        return "goal_a"
    if "goal_location_toilet_2" in joined or "toilet_2" in joined or "toilet2" in joined:
        return "goal_b"
    if "goal_a" in joined or "desk_a" in joined or "toilet_a" in joined or "sink_a" in joined:
        return "goal_a"
    if "goal_b" in joined or "desk_b" in joined or "toilet_b" in joined or "sink_b" in joined:
        return "goal_b"
    if "goal" in joined:
        return "goal"
    if "hazard" in joined:
        return "hazard"
    if "interactive" in joined or "button" in joined or "switch" in joined:
        return "interactive"
    if "floor" in joined or "ground" in joined or "tile" in joined:
        return "floor"
    if "hud" in joined or "panel" in joined or "ui" in joined:
        return "hud"

    return "decor"


@dataclass(slots=True)
class ArtBucket:
    floor: list[pygame.Surface]
    wall: list[pygame.Surface]
    blocker: list[pygame.Surface]
    goal_a: list[pygame.Surface]
    goal_b: list[pygame.Surface]
    goal: list[pygame.Surface]
    hazard: list[pygame.Surface]
    interactive: list[pygame.Surface]
    decor: list[pygame.Surface]
    char_a: list[pygame.Surface]
    char_b: list[pygame.Surface]
    hud: list[pygame.Surface]

    @staticmethod
    def empty() -> "ArtBucket":
        return ArtBucket(
            floor=[],
            wall=[],
            blocker=[],
            goal_a=[],
            goal_b=[],
            goal=[],
            hazard=[],
            interactive=[],
            decor=[],
            char_a=[],
            char_b=[],
            hud=[],
        )


class ArtLibrary:
    """
    Loads *all* images under GameArtImages/ (recursive).
    They are grouped by (optional) theme inferred from folder names + a role inferred from path/name keywords.

    If you just drop a bunch of images without naming conventions, they still get used via the 'decor' bucket.
    """

    def __init__(self, root_dir: str, tile_px: int) -> None:
        self.root_dir = root_dir
        self.tile_px = tile_px
        self.by_theme: dict[str, ArtBucket] = {}
        self.global_bucket: ArtBucket = ArtBucket.empty()
        self.loaded_count = 0

        if not os.path.isdir(root_dir):
            return

        exts = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
        for dirpath, _dirnames, filenames in os.walk(root_dir):
            for fn in filenames:
                ext = os.path.splitext(fn)[1].lower()
                if ext not in exts:
                    continue

                full = os.path.join(dirpath, fn)
                rel = os.path.relpath(full, root_dir)
                rel_parts = rel.split(os.sep)[:-1]

                try:
                    surf = pygame.image.load(full).convert_alpha()
                except Exception:
                    # Skip unreadable files rather than breaking the game.
                    continue

                self.loaded_count += 1

                theme = _theme_from_path(rel_parts)
                role = _role_from_name(rel_parts, fn)

                # Scale tile-like art to tile size. For HUD art we keep original.
                if role not in ("hud",):
                    surf = pygame.transform.smoothscale(surf, (tile_px, tile_px))

                bucket = self.global_bucket if theme is None else self.by_theme.setdefault(theme, ArtBucket.empty())
                getattr(bucket, role if hasattr(bucket, role) else "decor").append(surf)

    def bucket_for_theme(self, theme: str) -> ArtBucket:
        tb = self.by_theme.get(theme)
        if tb is None:
            return self.global_bucket
        if not tb.wall and tb.blocker:
            tb.wall = list(tb.blocker)
        if not tb.char_a and self.global_bucket.char_a:
            tb.char_a = list(self.global_bucket.char_a)
        if not tb.char_b and self.global_bucket.char_b:
            tb.char_b = list(self.global_bucket.char_b)
        return tb

