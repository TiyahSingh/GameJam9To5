from __future__ import annotations

import os
import random
from dataclasses import dataclass

import pygame

from game.assets import ArtLibrary
from game.audio import AudioManager
from game.generator import generate_level, random_theme_config
from game.level import Character, Level
from game.levels import static_levels
from game.menu import MainMenu, MenuResult
from game.movement import move_characters
from game.solver import solve_level_bfs
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
        self._load_pause_assets()

        self.audio = AudioManager()

        self.paused = False
        self.music_on = True
        self.pause_btn_rects: dict[str, pygame.Rect] = {}
        self._slider_rect: pygame.Rect | None = None
        self._dragging_slider = False

        self.clue_uses = 3
        self.clue_path: list[tuple[Vec2, Vec2, str]] | None = None
        self.clue_optimal_moves = 0

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
        self.img_btn_pause = self._crop_and_scale(load(new_ui, "Pause Button.png"), circle_size, circle_size)
        self.img_btn_clue = self._crop_and_scale(load(new_ui, "Clue Button.png"), btn_w, pill_h)

        self.hud_btn_rects: dict[str, pygame.Rect] = {}

    def _load_pause_assets(self) -> None:
        bg_dir = os.path.join(self.art_root, "Backrounds & Menus")
        pm_dir = os.path.join(self.art_root, "Pause Menu Buttons")

        def load(folder: str, name: str) -> pygame.Surface:
            return pygame.image.load(os.path.join(folder, name)).convert_alpha()

        self.pause_bg_raw = load(bg_dir, "Pause Menu Background.png")

        self.pm_back_raw = load(pm_dir, "Back Button.png")
        self.pm_home_raw = load(pm_dir, "Home Button.png")
        self.pm_sound_raw = load(pm_dir, "Sound Button.png")

        ui_btn = os.path.join(self.art_root, "UI and Buttons")
        self.pm_close_raw = load(ui_btn, "Close Game Button.png")

    def run(self) -> int:
        while True:
            menu_result = self._run_menu()
            if menu_result == MenuResult.QUIT:
                return 0

            game_result = self._run_game()
            if game_result == "quit":
                return 0
            # game_result == "home" → loop back to menu

    def _run_game(self) -> str:
        """Returns 'quit' to exit the app, 'home' to return to the main menu."""
        self.screen = pygame.display.set_mode(self._window_size())
        pygame.display.set_caption("9 to 5")
        self.paused = False
        self.audio.play_music(self.level.theme)

        while True:
            dt_ms = self.clock.tick(60)

            if self.paused:
                for ev in pygame.event.get():
                    if ev.type == pygame.QUIT:
                        return "quit"
                    elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                        self.paused = False
                        self._dragging_slider = False
                        self.audio.play_sfx("pause_close")
                    elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                        if self._slider_rect and self._slider_rect.collidepoint(ev.pos):
                            self._dragging_slider = True
                            self._update_slider_from_mouse(ev.pos[0])
                        else:
                            result = self._on_pause_click(ev.pos)
                            if result == "resume":
                                self.paused = False
                                self._dragging_slider = False
                                self.audio.play_sfx("pause_close")
                            elif result == "home":
                                self.audio.stop_music()
                                return "home"
                    elif ev.type == pygame.MOUSEMOTION and self._dragging_slider:
                        self._update_slider_from_mouse(ev.pos[0])
                    elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
                        self._dragging_slider = False
                self._draw()
                self._draw_pause_overlay()
                pygame.display.flip()
            else:
                self._update_flash(dt_ms)
                self._update_auto_advance(dt_ms)

                for ev in pygame.event.get():
                    if ev.type == pygame.QUIT:
                        return "quit"
                    elif ev.type == pygame.KEYDOWN:
                        if ev.key == pygame.K_ESCAPE:
                            self.paused = True
                            self.audio.play_sfx("pause_open")
                        elif not self._on_keydown(ev.key):
                            return "quit"
                    elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                        click_result = self._on_mouse_click(ev.pos)
                        if click_result is False:
                            return "quit"

                self._draw()

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
        self.clue_path = None
        self.clue_optimal_moves = 0

    def _load_level(self, idx: int) -> None:
        self.level_idx = max(0, min(idx, len(self.levels) - 1))
        self.level = self.levels[self.level_idx]
        self._fit_layout_to_screen(self.level)
        self._load_hud_buttons()
        self.art = ArtLibrary(self.art_root, tile_px=self.tile_px)
        self.screen = pygame.display.set_mode(self._window_size())
        self._reset_level()
        self.audio.play_music(self.level.theme)

    def _generate_and_load(self) -> None:
        cfg = random_theme_config(self.rng)
        lvl = generate_level(self.rng, cfg)
        self.levels.append(lvl)
        self._load_level(len(self.levels) - 1)

    def _on_keydown(self, key: int) -> bool:
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
                self.audio.play_sfx("click")
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
                elif action == "pause":
                    self.paused = True
                    self.audio.play_sfx("pause_open")
                elif action == "clue":
                    self._activate_clue()
                    self.audio.play_sfx("clue")
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
        self.clue_path = None
        step = move_characters(self.level, self.a.pos, self.b.pos, direction)
        if step.fell_off:
            self._set_flash((220, 70, 70), ms=220)
            self.audio.play_sfx("fail")
            self._reset_level()
            return

        if step.overlapped_prevented:
            self._set_flash((230, 190, 70), ms=120)

        self.a.pos = step.a_to
        self.b.pos = step.b_to
        self.move_count += 1
        self.audio.play_sfx("move")

        if self.level.tile_at(self.a.pos) == Tile.GOAL_A and self.level.tile_at(self.b.pos) == Tile.GOAL_B:
            self.completed = True
            self._set_flash((70, 200, 120), ms=250)
            self.audio.play_sfx("complete")
            self._record_completion()
            self.auto_advance_ms = 700

    def _record_completion(self) -> None:
        stars = self._compute_stars()
        st = self.stats.get(self.level_idx) or LevelStats()
        prev_best_stars = st.best_stars or 0
        st.completed = True
        st.best_moves = self.move_count if st.best_moves is None else min(st.best_moves, self.move_count)
        st.best_stars = stars if st.best_stars is None else max(st.best_stars, stars)
        self.stats[self.level_idx] = st
        if stars == 3 and prev_best_stars < 3:
            self.clue_uses += 1

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

    def _activate_clue(self) -> None:
        if self.clue_uses <= 0 or self.completed:
            return
        result = solve_level_bfs(
            self.level, a_start=self.a.pos, b_start=self.b.pos
        )
        if not result.found:
            return
        path: list[tuple[Vec2, Vec2, str]] = []
        a, b = self.a.pos, self.b.pos
        for direction in result.moves:
            path.append((a, b, direction))
            step = move_characters(self.level, a, b, direction)
            if step.fell_off:
                break
            a, b = step.a_to, step.b_to
        self.clue_path = path
        self.clue_optimal_moves = len(result.moves)
        self.clue_uses -= 1

    def _draw_clue_arrows(self, x0: int, y0: int) -> None:
        if not self.clue_path:
            return
        tp = self.tile_px
        total = len(self.clue_path)
        if total == 0:
            return

        dir_vecs = {
            "up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0),
        }
        color_a = (80, 160, 255)
        color_b = (200, 100, 255)

        def tile_center(pos: Vec2) -> tuple[int, int]:
            return x0 + pos.x * tp + tp // 2, y0 + pos.y * tp + tp // 2

        # Draw a connecting trail line for Player A
        trail_surf = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        for i in range(total):
            a_pos, _b, direction = self.clue_path[i]
            dx, dy = dir_vecs[direction]
            ax, ay = tile_center(a_pos)
            next_ax = ax + dx * (tp // 2)
            next_ay = ay + dy * (tp // 2)
            progress = i / max(1, total - 1)
            line_alpha = int(40 + 100 * progress)
            pygame.draw.line(
                trail_surf,
                (*color_a, line_alpha),
                (ax, ay), (next_ax, next_ay),
                max(2, int(3 + 3 * progress)),
            )
        self.screen.blit(trail_surf, (0, 0))

        # Draw arrows on each step for Player A — size and opacity increase near goal
        for i in range(total):
            a_pos, b_pos, direction = self.clue_path[i]
            dx, dy = dir_vecs[direction]
            progress = i / max(1, total - 1)

            # Alpha: 60 at start → 220 at end; size: 60% → 100% of tile quarter
            alpha = int(60 + 160 * progress)
            size_frac = 0.6 + 0.4 * progress

            ax, ay = tile_center(a_pos)
            self._blit_arrow(ax, ay, dx, dy, color_a, alpha, tp, size_frac)

            # Also draw on Player B for the last half of the path
            if progress >= 0.4:
                bx, by = tile_center(b_pos)
                b_alpha = int(40 + 140 * progress)
                self._blit_arrow(bx, by, dx, dy, color_b, b_alpha, tp, size_frac * 0.8)

        # Ring on the final destination tiles
        if total > 0:
            last_a, last_b, last_dir = self.clue_path[-1]
            final_step = move_characters(self.level, last_a, last_b, last_dir)
            if not final_step.fell_off:
                for pos, color in [(final_step.a_to, color_a), (final_step.b_to, color_b)]:
                    cx, cy = tile_center(pos)
                    ring = pygame.Surface((tp, tp), pygame.SRCALPHA)
                    mid = tp // 2
                    pygame.draw.circle(ring, (*color, 120), (mid, mid), tp // 3, 4)
                    pygame.draw.circle(ring, (*color, 60), (mid, mid), tp // 3 + 4, 2)
                    self.screen.blit(ring, (cx - mid, cy - mid))

    def _blit_arrow(
        self, cx: int, cy: int, dx: int, dy: int,
        color: tuple[int, int, int], alpha: int, tile_px: int,
        size_frac: float = 1.0,
    ) -> None:
        base_sz = max(8, tile_px // 4)
        sz = max(6, int(base_sz * size_frac))
        surf = pygame.Surface((tile_px, tile_px), pygame.SRCALPHA)
        mid = tile_px // 2
        if dx == 1:
            pts = [(mid + sz, mid), (mid - sz // 2, mid - sz), (mid - sz // 2, mid + sz)]
        elif dx == -1:
            pts = [(mid - sz, mid), (mid + sz // 2, mid - sz), (mid + sz // 2, mid + sz)]
        elif dy == -1:
            pts = [(mid, mid - sz), (mid - sz, mid + sz // 2), (mid + sz, mid + sz // 2)]
        else:
            pts = [(mid, mid + sz), (mid - sz, mid - sz // 2), (mid + sz, mid - sz // 2)]
        pygame.draw.polygon(surf, (*color, min(255, alpha)), pts)
        # Outline for extra clarity on final steps
        if alpha > 150:
            pygame.draw.polygon(surf, (*color, min(255, alpha + 30)), pts, 2)
        self.screen.blit(surf, (cx - mid, cy - mid))

    def _draw_star(self, cx: int, cy: int, radius: int, filled: bool) -> None:
        """Draw a 5-pointed star procedurally. Gold if filled, grey if empty."""
        import math
        color = (230, 190, 50) if filled else (170, 170, 170)
        outline = (180, 140, 20) if filled else (130, 130, 130)
        pts: list[tuple[float, float]] = []
        for i in range(10):
            angle = math.radians(-90 + i * 36)
            r = radius if i % 2 == 0 else radius * 0.42
            pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
        pygame.draw.polygon(self.screen, color, pts)
        pygame.draw.polygon(self.screen, outline, pts, 2)

    def _draw_stars_row(self, cx: int, y: int, count: int, star_r: int = 11) -> int:
        """Draw 3 stars centred at cx, returning the y below them."""
        gap = star_r * 2 + 6
        total_w = gap * 2
        sx = cx - total_w // 2
        for i in range(3):
            self._draw_star(sx + i * gap, y + star_r, star_r, filled=(i < count))
        return y + star_r * 2 + 4

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

        if not self.paused:
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

        # Goal tile glow highlights (visual only — no gameplay impact)
        glow_a = pygame.Surface((self.tile_px, self.tile_px), pygame.SRCALPHA)
        glow_b = pygame.Surface((self.tile_px, self.tile_px), pygame.SRCALPHA)
        glow_a.fill((80, 160, 255, 45))
        glow_b.fill((200, 100, 255, 45))
        for y in range(self.level.h):
            for x in range(self.level.w):
                t = self.level.grid[y][x]
                if t == Tile.GOAL_A or t == Tile.GOAL_B:
                    r = pygame.Rect(x0 + x * self.tile_px, y0 + y * self.tile_px, self.tile_px, self.tile_px)
                    g = glow_a if t == Tile.GOAL_A else glow_b
                    self.screen.blit(g, r.topleft)
                    color = (80, 160, 255) if t == Tile.GOAL_A else (200, 100, 255)
                    pygame.draw.rect(self.screen, color, r, width=3, border_radius=6)

        # Characters — colour identity matches goal tiles
        color_a = (80, 160, 255)
        color_b = (200, 100, 255)

        def draw_char(
            p: Vec2,
            fallback_color: tuple[int, int, int],
            label: str,
            sprites: list[pygame.Surface],
            identity_color: tuple[int, int, int],
        ) -> None:
            tile_r = pygame.Rect(x0 + p.x * self.tile_px, y0 + p.y * self.tile_px, self.tile_px, self.tile_px)

            # Glow overlay on the tile beneath the character
            glow = pygame.Surface((self.tile_px, self.tile_px), pygame.SRCALPHA)
            glow.fill((*identity_color, 50))
            self.screen.blit(glow, tile_r.topleft)
            pygame.draw.rect(self.screen, identity_color, tile_r, width=3, border_radius=8)

            r = tile_r.inflate(-12, -12)
            if sprites:
                s = sprites[(p.x + p.y * 17) % len(sprites)]
                self.screen.blit(s, tile_r.topleft)
                pygame.draw.rect(self.screen, identity_color, tile_r, width=3, border_radius=10)
            else:
                pygame.draw.rect(self.screen, fallback_color, r, border_radius=10)
                txt = self.font_big.render(label, True, (10, 10, 12))
                self.screen.blit(txt, txt.get_rect(center=r.center))

        draw_char(self.a.pos, (120, 175, 255), "A", bucket.char_a, color_a)
        draw_char(self.b.pos, (220, 135, 255), "B", bucket.char_b, color_b)

        self._draw_clue_arrows(x0, y0)

        # Grid border
        pygame.draw.rect(self.screen, (10, 10, 12), self._grid_rect_px(), width=3, border_radius=10)

    def _update_slider_from_mouse(self, mx: int) -> None:
        if self._slider_rect is None:
            return
        hr = max(10, self._slider_rect.height // 2)
        track_x = self._slider_rect.x + hr
        track_w = self._slider_rect.width - hr * 2
        rel = (mx - track_x) / max(1, track_w)
        vol = max(0.0, min(1.0, rel))
        self.audio.set_volume(vol)

    def _on_pause_click(self, pos_px: tuple[int, int]) -> str | None:
        """Returns 'resume', 'home', or None."""
        for action, rect in self.pause_btn_rects.items():
            if rect.collidepoint(pos_px):
                self.audio.play_sfx("click")
                if action in ("back", "close"):
                    return "resume"
                if action == "home":
                    self.audio.stop_music()
                    return "home"
                if action == "sound":
                    self.music_on = not self.music_on
                    self.audio.set_music_on(self.music_on)
        return None

    def _draw_pause_overlay(self) -> None:
        w, h = self.screen.get_size()
        self.pause_btn_rects.clear()

        dim = pygame.Surface((w, h), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 140))
        self.screen.blit(dim, (0, 0))

        # Aspect-ratio-preserving fit — generous sizing (up to 75% of screen)
        raw_w, raw_h = self.pause_bg_raw.get_size()
        aspect = raw_w / max(1, raw_h)
        max_panel_w = int(w * 0.75)
        max_panel_h = int(h * 0.85)
        if max_panel_w / aspect <= max_panel_h:
            panel_w = max_panel_w
            panel_h = int(panel_w / aspect)
        else:
            panel_h = max_panel_h
            panel_w = int(panel_h * aspect)

        bg_scaled = pygame.transform.smoothscale(self.pause_bg_raw, (panel_w, panel_h))
        panel_x = (w - panel_w) // 2
        panel_y = (h - panel_h) // 2
        self.screen.blit(bg_scaled, (panel_x, panel_y))

        # Close button — top-right corner of the clipboard board (right edge 72.5%, top ~13%)
        close_sz = max(28, int(panel_h * 0.07))
        img_close = self._crop_and_scale(self.pm_close_raw, close_sz, close_sz)
        board_right = panel_x + int(panel_w * 0.715)
        board_top = panel_y + int(panel_h * 0.125)
        close_r = img_close.get_rect(topright=(board_right, board_top))
        self.screen.blit(img_close, close_r)
        self.pause_btn_rects["close"] = close_r

        # Paper area within the clipboard image (measured from actual white region)
        paper_x = panel_x + int(panel_w * 0.306)
        paper_y = panel_y + int(panel_h * 0.22)
        paper_w = int(panel_w * 0.383)
        paper_h = int(panel_h * 0.68)
        paper_cx = panel_x + int(panel_w * 0.497)

        # ── Layout: buttons centred in paper (pushed down from title area) ──
        btn_zone_top = paper_y + int(paper_h * 0.20)
        btn_zone_bot = paper_y + int(paper_h * 0.75)
        slider_zone_bot = paper_y + paper_h - int(paper_h * 0.06)

        btn_avail = btn_zone_bot - btn_zone_top
        btn_size = max(28, int(btn_avail * 0.26))
        btn_gap = max(4, int(btn_avail * 0.06))

        img_home = self._crop_and_scale(self.pm_home_raw, btn_size, btn_size)
        img_sound = self._crop_and_scale(self.pm_sound_raw, btn_size, btn_size)
        img_back = self._crop_and_scale(self.pm_back_raw, btn_size, btn_size)

        btns: list[tuple[str, pygame.Surface]] = [
            ("home", img_home),
            ("sound", img_sound),
            ("back", img_back),
        ]
        btns_total = btn_size * 3 + btn_gap * 2
        by = btn_zone_top + max(0, (btn_avail - btns_total) // 2)

        for name, img in btns:
            r = img.get_rect(centerx=paper_cx, top=by)
            surf = img
            if name == "sound" and not self.music_on:
                surf = img.copy()
                sw, sh = surf.get_size()
                pygame.draw.line(surf, (200, 40, 40), (4, 4), (sw - 4, sh - 4), 4)
                pygame.draw.line(surf, (255, 60, 60), (5, 5), (sw - 5, sh - 5), 2)
            self.screen.blit(surf, r)
            self.pause_btn_rects[name] = r
            by += img.get_height() + btn_gap

        # ── Volume Slider — tiny, bottom-center of paper ──────────────
        track_h = max(4, int(paper_h * 0.016))
        handle_r = max(4, int(track_h * 0.8))
        s_font = pygame.font.SysFont("consolas", max(8, int(paper_h * 0.028)))

        vol_pct = int(self.audio.volume * 100)
        lbl = s_font.render(f"Vol {vol_pct}%", True, (80, 130, 200))

        track_w = max(30, int(paper_w * 0.60))
        track_x = paper_cx - track_w // 2
        track_y = slider_zone_bot - track_h - handle_r
        lbl_y = track_y - lbl.get_height() - 2

        self.screen.blit(lbl, lbl.get_rect(centerx=paper_cx, top=lbl_y))

        hit_pad = max(handle_r + 2, 6)
        self._slider_rect = pygame.Rect(
            track_x - hit_pad, track_y - hit_pad,
            track_w + hit_pad * 2, track_h + hit_pad * 2,
        )

        tr = pygame.Rect(track_x, track_y, track_w, track_h)
        pygame.draw.rect(self.screen, (190, 210, 235), tr, border_radius=track_h // 2)
        pygame.draw.rect(self.screen, (100, 155, 215), tr, width=1, border_radius=track_h // 2)

        fill_w = max(0, min(track_w, int(track_w * self.audio.volume)))
        if fill_w > 0:
            pygame.draw.rect(
                self.screen, (80, 150, 230),
                pygame.Rect(track_x, track_y, fill_w, track_h),
                border_radius=track_h // 2,
            )

        hx = track_x + fill_w
        hy = track_y + track_h // 2
        pygame.draw.circle(self.screen, (255, 255, 255), (hx, hy), handle_r)
        pygame.draw.circle(self.screen, (70, 140, 225), (hx, hy), handle_r, 2)
        if self._dragging_slider:
            pygame.draw.circle(self.screen, (110, 175, 245), (hx, hy), max(1, handle_r - 2))

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
        hud_cx = hud_x + self.hud_w_px // 2
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

        if self.clue_path is not None and not self.completed:
            total_if_follow = self.move_count + self.clue_optimal_moves
            line(f"Hint: {self.clue_optimal_moves} moves to goal", color=(40, 100, 180))
            if self.level.par_moves is not None:
                if total_if_follow <= self.level.par_moves:
                    line("3-star still possible!", color=green)
                elif total_if_follow <= self.level.par_moves + 3:
                    line("2-star possible", color=accent)

        if self.completed:
            stars = self._compute_stars()
            y += 4
            y = self._draw_stars_row(hud_cx, y, stars)
            if self.level_idx + 1 < len(self.levels):
                line("Next level starting...", color=accent)
            else:
                line("All levels complete!", color=accent)
        y += 10

        st = self.stats.get(self.level_idx)
        if st and st.completed and not self.completed:
            line("Best:", color=accent)
            if st.best_moves is not None:
                line(f"  Moves: {st.best_moves}", color=accent)
            if st.best_stars is not None:
                y = self._draw_stars_row(hud_cx, y, st.best_stars, star_r=9)
            y += 6

        # --- Buttons on paper ---
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

        # Clue button below zoom, centred
        y += max(r_in.height, r_out.height) + 10
        clue_img = self.img_btn_clue
        if self.clue_uses <= 0:
            clue_img = clue_img.copy()
            grey_overlay = pygame.Surface(clue_img.get_size(), pygame.SRCALPHA)
            grey_overlay.fill((120, 120, 120, 140))
            clue_img.blit(grey_overlay, (0, 0))
        clue_r = clue_img.get_rect(centerx=hud_cx, top=y)
        self.screen.blit(clue_img, clue_r)
        self.hud_btn_rects["clue"] = clue_r
        y += clue_r.height + 3
        clue_txt = self.font.render(f"Clues: {self.clue_uses}", True, accent)
        self.screen.blit(clue_txt, clue_txt.get_rect(centerx=hud_cx, top=y))
        y += clue_txt.get_height() + 8

        # Pause button below clue, centred
        pause_r = self.img_btn_pause.get_rect(centerx=hud_cx, top=y)
        self.screen.blit(self.img_btn_pause, pause_r)
        self.hud_btn_rects["pause"] = pause_r

        # Close Game button — fixed top-right corner of HUD, outside the flow
        exit_r = self.img_btn_exit.get_rect(topright=(w - clip_margin - 4, 4))
        self.screen.blit(self.img_btn_exit, exit_r)
        self.hud_btn_rects["exit"] = exit_r

