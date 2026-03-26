from __future__ import annotations

import os
import random
from dataclasses import dataclass

import pygame

from game.assets import ArtLibrary
from game.generator import generate_level, random_theme_config
from game.level import Character, Level
from game.levels import static_levels
from game.menu import MainMenu, MenuResult
from game.movement import move_characters
from game.types import Tile, Vec2


@dataclass(slots=True)
class LevelStats:
    completed: bool = False
    best_moves: int | None = None
    best_stars: int | None = None


class GameApp:
    def __init__(self) -> None:
        self.rng = random.Random()

        self.levels: list[Level] = static_levels()
        self.level_idx = 0
        self.level: Level = self.levels[self.level_idx]

        self.a = Character("A", start=self.level.a_start, pos=self.level.a_start)
        self.b = Character("B", start=self.level.b_start, pos=self.level.b_start)

        self.move_count = 0
        self.completed = False
        self.auto_advance_ms: int | None = None

        self.stats: dict[int, LevelStats] = {}

        self.tile_px = 96
        self.pad_px = 12
        self.hud_w_px = 280
        self.user_zoom_offset = 0

        self._fit_layout_to_screen(self.level)

        self.screen = pygame.display.set_mode(self._window_size())
        pygame.display.set_caption("9 to 5")
        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont("consolas", 18)
        self.font_big = pygame.font.SysFont("consolas", 26, bold=True)

        self.art_root = os.path.join(os.path.dirname(os.path.dirname(__file__)), "GameArtImages")
        self.art = ArtLibrary(self.art_root, tile_px=self.tile_px)

        self._load_hud_buttons()

        self.flash_ms = 0
        self.flash_color: tuple[int, int, int] | None = None

    def _window_size(self) -> tuple[int, int]:
        w = self.level.w * self.tile_px + self.pad_px * 2 + self.hud_w_px
        h = self.level.h * self.tile_px + self.pad_px * 2
        return w, h

    def _fit_layout_to_screen(self, level: Level) -> None:
        """
        Auto-fit game canvas to current display so levels stay fully visible.
        Keeps gameplay unchanged; only visual scale/layout is adjusted.
        """
        info = pygame.display.Info()
        display_w = max(800, info.current_w)
        display_h = max(600, info.current_h)

        self.pad_px = 8
        self.hud_w_px = max(180, min(280, display_w // 5))

        # Keep small margins so the game is not undersized.
        max_window_w = display_w - 30
        max_window_h = display_h - 70

        avail_w_for_grid = max(200, max_window_w - self.hud_w_px - self.pad_px * 2)
        avail_h_for_grid = max(200, max_window_h - self.pad_px * 2)

        max_tile = 128
        min_tile = 40
        by_w = avail_w_for_grid // max(1, level.w)
        by_h = avail_h_for_grid // max(1, level.h)
        base_tile = max(min_tile, min(max_tile, by_w, by_h))
        self.tile_px = max(min_tile, min(max_tile, base_tile + self.user_zoom_offset))

    @staticmethod
    def _crop_and_scale(surf: pygame.Surface, max_w: int, max_h: int) -> pygame.Surface:
        """Crop a surface to its opaque bounding box, then scale to fit within max_w x max_h."""
        bbox = surf.get_bounding_rect()
        cropped = surf.subsurface(bbox).copy()
        cw, ch = cropped.get_size()
        scale = min(max_w / max(1, cw), max_h / max(1, ch))
        new_w = max(1, int(cw * scale))
        new_h = max(1, int(ch * scale))
        return pygame.transform.smoothscale(cropped, (new_w, new_h))

    def _load_hud_buttons(self) -> None:
        new_ui = os.path.join(self.art_root, "New UI")
        ui_btn = os.path.join(self.art_root, "UI and Buttons")

        def load(folder: str, name: str) -> pygame.Surface:
            return pygame.image.load(os.path.join(folder, name)).convert_alpha()

        btn_w = self.hud_w_px - 32
        pill_h = 48
        circle_size = 44

        self.img_btn_reset = self._crop_and_scale(load(new_ui, "Reset Level Button.png"), btn_w, pill_h)
        self.img_btn_generate = self._crop_and_scale(load(new_ui, "Generate New Level Button.png"), btn_w, pill_h)
        self.img_btn_zoom_in = self._crop_and_scale(load(new_ui, "Zoom In Button.png"), circle_size, circle_size)
        self.img_btn_zoom_out = self._crop_and_scale(load(new_ui, "Zoom Out Button.png"), circle_size, circle_size)
        self.img_btn_exit = self._crop_and_scale(load(ui_btn, "Close Game Button.png"), circle_size, circle_size)

        self.hud_btn_rects: dict[str, pygame.Rect] = {}

    def run(self) -> int:
        menu_result = self._run_menu()
        if menu_result == MenuResult.QUIT:
            return 0

        self.screen = pygame.display.set_mode(self._window_size())
        pygame.display.set_caption("9 to 5")

        running = True
        while running:
            dt_ms = self.clock.tick(60)
            self._update_flash(dt_ms)
            self._update_auto_advance(dt_ms)

            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    running = False
                elif ev.type == pygame.KEYDOWN:
                    running = self._on_keydown(ev.key)
                elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    click_result = self._on_mouse_click(ev.pos)
                    if click_result is False:
                        running = False

            self._draw()
        return 0

    def _run_menu(self) -> MenuResult:
        art_images_root = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "GameArtImages"
        )
        menu = MainMenu(art_images_root)
        menu_screen = pygame.display.set_mode(menu.get_window_size())
        pygame.display.set_caption("9 to 5 — Get to Work!")

        while True:
            self.clock.tick(60)
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    return MenuResult.QUIT
                result = menu.handle_event(ev)
                if result in (MenuResult.PLAY, MenuResult.QUIT):
                    return result

            menu_screen.fill((200, 215, 235))
            menu.draw(menu_screen)
            pygame.display.flip()

    def _update_auto_advance(self, dt_ms: int) -> None:
        if self.auto_advance_ms is None:
            return
        self.auto_advance_ms = max(0, self.auto_advance_ms - dt_ms)
        if self.auto_advance_ms > 0:
            return
        self.auto_advance_ms = None
        if self.level_idx + 1 < len(self.levels):
            self._load_level(self.level_idx + 1)

    def _update_flash(self, dt_ms: int) -> None:
        if self.flash_ms > 0:
            self.flash_ms = max(0, self.flash_ms - dt_ms)
            if self.flash_ms == 0:
                self.flash_color = None

    def _set_flash(self, rgb: tuple[int, int, int], ms: int = 120) -> None:
        self.flash_color = rgb
        self.flash_ms = ms

    def _reset_level(self) -> None:
        self.a.start = self.level.a_start
        self.b.start = self.level.b_start
        self.a.reset()
        self.b.reset()
        self.move_count = 0
        self.completed = False
        self.auto_advance_ms = None

    def _load_level(self, idx: int) -> None:
        self.level_idx = max(0, min(idx, len(self.levels) - 1))
        self.level = self.levels[self.level_idx]
        self._fit_layout_to_screen(self.level)
        self._load_hud_buttons()
        self.art = ArtLibrary(self.art_root, tile_px=self.tile_px)
        self.screen = pygame.display.set_mode(self._window_size())
        self._reset_level()

    def _generate_and_load(self) -> None:
        cfg = random_theme_config(self.rng)
        lvl = generate_level(self.rng, cfg)
        self.levels.append(lvl)
        self._load_level(len(self.levels) - 1)

    def _on_keydown(self, key: int) -> bool:
        if key == pygame.K_ESCAPE:
            return False
        if key == pygame.K_r:
            self._reset_level()
            return True
        # Level progression is locked: you must beat the current level to advance.
        if key in (pygame.K_LEFTBRACKET, pygame.K_RIGHTBRACKET):
            return True
        if key == pygame.K_g:
            self._generate_and_load()
            return True
        if key in (pygame.K_EQUALS, pygame.K_PLUS, pygame.K_KP_PLUS):
            self.user_zoom_offset = min(36, self.user_zoom_offset + 4)
            self._fit_layout_to_screen(self.level)
            self._load_hud_buttons()
            self.art = ArtLibrary(self.art_root, tile_px=self.tile_px)
            self.screen = pygame.display.set_mode(self._window_size())
            return True
        if key in (pygame.K_MINUS, pygame.K_KP_MINUS):
            self.user_zoom_offset = max(-24, self.user_zoom_offset - 4)
            self._fit_layout_to_screen(self.level)
            self._load_hud_buttons()
            self.art = ArtLibrary(self.art_root, tile_px=self.tile_px)
            self.screen = pygame.display.set_mode(self._window_size())
            return True

        if self.completed:
            # Allow navigation/reset/generation even when completed, but no moves.
            return True

        direction: str | None = None
        if key in (pygame.K_w, pygame.K_UP):
            direction = "up"
        elif key in (pygame.K_s, pygame.K_DOWN):
            direction = "down"
        elif key in (pygame.K_a, pygame.K_LEFT):
            direction = "left"
        elif key in (pygame.K_d, pygame.K_RIGHT):
            direction = "right"

        if direction is not None:
            self._step(direction)
        return True

    def _on_mouse_click(self, pos_px: tuple[int, int]) -> bool | None:
        """Returns False to quit, None otherwise."""
        for action, rect in self.hud_btn_rects.items():
            if rect.collidepoint(pos_px):
                if action == "reset":
                    self._reset_level()
                elif action == "generate":
                    self._generate_and_load()
                elif action == "zoom_in":
                    self.user_zoom_offset = min(36, self.user_zoom_offset + 4)
                    self._fit_layout_to_screen(self.level)
                    self._load_hud_buttons()
                    self.art = ArtLibrary(self.art_root, tile_px=self.tile_px)
                    self.screen = pygame.display.set_mode(self._window_size())
                elif action == "zoom_out":
                    self.user_zoom_offset = max(-24, self.user_zoom_offset - 4)
                    self._fit_layout_to_screen(self.level)
                    self._load_hud_buttons()
                    self.art = ArtLibrary(self.art_root, tile_px=self.tile_px)
                    self.screen = pygame.display.set_mode(self._window_size())
                elif action == "exit":
                    return False
                return None

        if self.completed:
            return None
        grid_p = self._px_to_grid(pos_px)
        if grid_p is None:
            return None
        dx = grid_p.x - self.a.pos.x
        dy = grid_p.y - self.a.pos.y
        if dx == 0 and dy == 0:
            return None
        if abs(dx) > abs(dy):
            direction = "right" if dx > 0 else "left"
        else:
            direction = "down" if dy > 0 else "up"
        self._step(direction)
        return None

    def _step(self, direction: str) -> None:
        step = move_characters(self.level, self.a.pos, self.b.pos, direction)
        if step.fell_off:
            self._set_flash((220, 70, 70), ms=220)
            self._reset_level()
            return

        if step.overlapped_prevented:
            self._set_flash((230, 190, 70), ms=120)

        self.a.pos = step.a_to
        self.b.pos = step.b_to
        self.move_count += 1

        if self.level.tile_at(self.a.pos) == Tile.GOAL_A and self.level.tile_at(self.b.pos) == Tile.GOAL_B:
            self.completed = True
            self._set_flash((70, 200, 120), ms=250)
            self._record_completion()
            self.auto_advance_ms = 700

    def _record_completion(self) -> None:
        stars = self._compute_stars()
        st = self.stats.get(self.level_idx) or LevelStats()
        st.completed = True
        st.best_moves = self.move_count if st.best_moves is None else min(st.best_moves, self.move_count)
        st.best_stars = stars if st.best_stars is None else max(st.best_stars, stars)
        self.stats[self.level_idx] = st

    def _compute_stars(self) -> int:
        if not self.completed:
            return 0
        if self.level.par_moves is None:
            return 1
        if self.move_count <= self.level.par_moves:
            return 3
        if self.move_count <= self.level.par_moves + 3:
            return 2
        return 1

    def _grid_origin_px(self) -> tuple[int, int]:
        return (self.pad_px, self.pad_px)

    def _grid_rect_px(self) -> pygame.Rect:
        x0, y0 = self._grid_origin_px()
        return pygame.Rect(x0, y0, self.level.w * self.tile_px, self.level.h * self.tile_px)

    def _px_to_grid(self, pos_px: tuple[int, int]) -> Vec2 | None:
        gx0, gy0 = self._grid_origin_px()
        x, y = pos_px
        if x < gx0 or y < gy0:
            return None
        x -= gx0
        y -= gy0
        if x >= self.level.w * self.tile_px or y >= self.level.h * self.tile_px:
            return None
        return Vec2(x // self.tile_px, y // self.tile_px)

    def _theme_palette(self) -> dict[str, tuple[int, int, int]]:
        # White background across themes (requested).
        bg_white = (255, 255, 255)
        t = self.level.theme
        if t == "Elevator":
            return {"bg": bg_white, "floor": (230, 233, 240)}
        if t == "Office":
            return {"bg": bg_white, "floor": (232, 238, 234)}
        if t == "Bathroom":
            return {"bg": bg_white, "floor": (232, 236, 238)}
        if t == "Break Room":
            return {"bg": bg_white, "floor": (238, 232, 230)}
        if t == "Parking Lot":
            return {"bg": bg_white, "floor": (230, 230, 232)}
        return {"bg": bg_white, "floor": (236, 236, 240)}

    def _draw(self) -> None:
        pal = self._theme_palette()
        self.screen.fill(pal["bg"])

        self._draw_grid(pal)
        self._draw_hud()

        if self.flash_color is not None:
            overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
            alpha = 90 if self.flash_ms > 0 else 0
            overlay.fill((*self.flash_color, alpha))
            self.screen.blit(overlay, (0, 0))

        pygame.display.flip()

    def _draw_grid(self, pal: dict[str, tuple[int, int, int]]) -> None:
        x0, y0 = self._grid_origin_px()
        bucket = self.art.bucket_for_theme(self.level.theme)

        # Tiles
        for y in range(self.level.h):
            for x in range(self.level.w):
                t = self.level.grid[y][x]
                r = pygame.Rect(x0 + x * self.tile_px, y0 + y * self.tile_px, self.tile_px, self.tile_px)

                # Choose art if available; otherwise fall back to colors.
                surf: pygame.Surface | None = None
                if t == Tile.EMPTY and bucket.floor:
                    surf = bucket.floor[(x + y * 31) % len(bucket.floor)]
                elif t == Tile.WALL and bucket.wall and (x * 7 + y * 13 + self.level_idx * 53) % 5 == 0:
                    surf = bucket.wall[(x * 7 + y * 13) % len(bucket.wall)]
                elif t == Tile.BLOCKER and bucket.blocker:
                    surf = bucket.blocker[(x * 11 + y * 19) % len(bucket.blocker)]
                elif t == Tile.GOAL_A and (bucket.goal_a or bucket.goal):
                    src = bucket.goal_a or bucket.goal
                    surf = src[(x + y * 17) % len(src)]
                elif t == Tile.GOAL_B and (bucket.goal_b or bucket.goal):
                    src = bucket.goal_b or bucket.goal
                    surf = src[(x + y * 23) % len(src)]
                elif t == Tile.HAZARD and bucket.hazard:
                    surf = bucket.hazard[(x + y * 29) % len(bucket.hazard)]
                elif t == Tile.INTERACTIVE and bucket.interactive:
                    surf = bucket.interactive[(x + y * 37) % len(bucket.interactive)]

                if surf is not None:
                    self.screen.blit(surf, r.topleft)
                    pygame.draw.rect(self.screen, (10, 10, 12), r, width=2, border_radius=6)
                else:
                    base = pal["floor"]
                    if t == Tile.WALL:
                        base = (80, 84, 96)
                    elif t == Tile.BLOCKER:
                        base = (110, 92, 60)
                    elif t == Tile.GOAL_A:
                        base = (68, 120, 210)
                    elif t == Tile.GOAL_B:
                        base = (190, 90, 210)
                    elif t == Tile.HAZARD:
                        base = (170, 55, 55)
                    elif t == Tile.INTERACTIVE:
                        base = (55, 140, 120)

                    pygame.draw.rect(self.screen, base, r, border_radius=6)
                    pygame.draw.rect(self.screen, (10, 10, 12), r, width=2, border_radius=6)

                # Use "decor" images as occasional overlays so every image can show up even
                # if not named with a specific role.
                if t == Tile.EMPTY and bucket.decor:
                    # Deterministic sparse placement.
                    stamp = (x * 97 + y * 193 + self.level_idx * 389) % 23
                    if stamp == 0:
                        deco = bucket.decor[(x * 3 + y * 5) % len(bucket.decor)]
                        self.screen.blit(deco, r.topleft)

        # Characters
        def draw_char(p: Vec2, fallback_color: tuple[int, int, int], label: str, sprites: list[pygame.Surface]) -> None:
            r = pygame.Rect(
                x0 + p.x * self.tile_px + 6,
                y0 + p.y * self.tile_px + 6,
                self.tile_px - 12,
                self.tile_px - 12,
            )
            if sprites:
                s = sprites[(p.x + p.y * 17) % len(sprites)]
                # Sprites are already tile-sized; inset them a bit.
                inset = pygame.Rect(r.x - 6, r.y - 6, self.tile_px, self.tile_px)
                self.screen.blit(s, inset.topleft)
                pygame.draw.rect(self.screen, (10, 10, 12), inset, width=2, border_radius=10)
            else:
                pygame.draw.rect(self.screen, fallback_color, r, border_radius=10)
                txt = self.font_big.render(label, True, (10, 10, 12))
                self.screen.blit(txt, txt.get_rect(center=r.center))

        draw_char(self.a.pos, (120, 175, 255), "A", bucket.char_a)
        draw_char(self.b.pos, (220, 135, 255), "B", bucket.char_b)

        # Grid border
        pygame.draw.rect(self.screen, (10, 10, 12), self._grid_rect_px(), width=3, border_radius=10)

    def _draw_hud(self) -> None:
        w, h = self.screen.get_size()
        hud_x = w - self.hud_w_px

        # --- Desk surface background ---
        desk = pygame.Rect(hud_x, 0, self.hud_w_px, h)
        pygame.draw.rect(self.screen, (162, 123, 82), desk)
        for stripe_y in range(0, h, 18):
            c = (152, 115, 74) if (stripe_y // 18) % 2 == 0 else (168, 130, 88)
            pygame.draw.rect(self.screen, c, (hud_x, stripe_y, self.hud_w_px, 9))

        # --- Clipboard ---
        clip_margin = 10
        clip_rect = pygame.Rect(hud_x + clip_margin, 20, self.hud_w_px - clip_margin * 2, h - 30)
        pygame.draw.rect(self.screen, (178, 144, 96), clip_rect, border_radius=10)
        pygame.draw.rect(self.screen, (148, 118, 72), clip_rect, width=3, border_radius=10)

        # Metal clip at top
        clip_w, clip_h = 40, 18
        clip_top = pygame.Rect(clip_rect.centerx - clip_w // 2, clip_rect.top - 6, clip_w, clip_h)
        pygame.draw.rect(self.screen, (170, 175, 180), clip_top, border_radius=6)
        pygame.draw.rect(self.screen, (130, 135, 140), clip_top, width=2, border_radius=6)
        pygame.draw.circle(self.screen, (150, 155, 160), (clip_top.centerx, clip_top.top + 6), 4)

        # Paper sheet on clipboard
        paper_margin = 8
        paper = pygame.Rect(
            clip_rect.x + paper_margin,
            clip_rect.y + 16,
            clip_rect.width - paper_margin * 2,
            clip_rect.height - 24,
        )
        pygame.draw.rect(self.screen, (248, 244, 235), paper, border_radius=4)
        pygame.draw.rect(self.screen, (200, 192, 178), paper, width=1, border_radius=4)

        # Faint ruled lines on the paper
        for ly in range(paper.top + 24, paper.bottom - 4, 20):
            pygame.draw.line(self.screen, (220, 215, 205), (paper.left + 6, ly), (paper.right - 6, ly))

        # --- Text on paper ---
        text_x = paper.x + 10
        y = paper.y + 8

        dark = (42, 36, 28)
        accent = (90, 70, 45)
        green = (35, 120, 60)

        def line(text: str, big: bool = False, color: tuple[int, int, int] = dark) -> None:
            nonlocal y
            f = self.font_big if big else self.font
            surf = f.render(text, True, color)
            self.screen.blit(surf, (text_x, y))
            y += surf.get_height() + (8 if big else 5)

        line("9 to 5", big=True, color=accent)
        line(f"Level {self.level_idx + 1}/{len(self.levels)}")
        line(f"Theme: {self.level.theme}")
        y += 6

        line(f"Moves: {self.move_count}", color=dark)
        if self.level.par_moves is not None:
            line(f"Par: {self.level.par_moves}", color=accent)
        if self.completed:
            stars = self._compute_stars()
            line(f"Completed: {stars} star(s)", color=green)
            if self.level_idx + 1 < len(self.levels):
                line("Next level starting...", color=accent)
            else:
                line("All levels complete!", color=accent)
        y += 10

        st = self.stats.get(self.level_idx)
        if st and st.completed:
            line("Best:", color=accent)
            if st.best_moves is not None:
                line(f"  Moves: {st.best_moves}", color=accent)
            if st.best_stars is not None:
                line(f"  Stars: {st.best_stars}", color=accent)
            y += 6

        # --- Buttons on paper ---
        hud_cx = hud_x + self.hud_w_px // 2
        y += 4

        def place_btn(name: str, img: pygame.Surface) -> None:
            nonlocal y
            r = img.get_rect(centerx=hud_cx, top=y)
            self.screen.blit(img, r)
            self.hud_btn_rects[name] = r
            y += r.height + 8

        place_btn("reset", self.img_btn_reset)
        place_btn("generate", self.img_btn_generate)

        y += 4
        gap = 12
        total_w = self.img_btn_zoom_in.get_width() + gap + self.img_btn_zoom_out.get_width()
        zx = hud_cx - total_w // 2

        r_in = self.img_btn_zoom_in.get_rect(topleft=(zx, y))
        self.screen.blit(self.img_btn_zoom_in, r_in)
        self.hud_btn_rects["zoom_in"] = r_in

        r_out = self.img_btn_zoom_out.get_rect(topleft=(zx + self.img_btn_zoom_in.get_width() + gap, y))
        self.screen.blit(self.img_btn_zoom_out, r_out)
        self.hud_btn_rects["zoom_out"] = r_out

        # Exit button in top-right corner of the desk
        exit_r = self.img_btn_exit.get_rect(topright=(w - clip_margin - 4, 24))
        self.screen.blit(self.img_btn_exit, exit_r)
        self.hud_btn_rects["exit"] = exit_r

