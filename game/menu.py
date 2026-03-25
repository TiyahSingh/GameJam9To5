from __future__ import annotations

import os
from enum import Enum, auto

import pygame


class MenuResult(Enum):
    NONE = auto()
    PLAY = auto()
    QUIT = auto()


class _MenuState(Enum):
    START = auto()
    CONTROLS = auto()
    RULES = auto()


class _Button:
    def __init__(self, image: pygame.Surface, center: tuple[int, int], scale: float = 1.0) -> None:
        w = int(image.get_width() * scale)
        h = int(image.get_height() * scale)
        self.image = pygame.transform.smoothscale(image, (w, h))
        self.rect = self.image.get_rect(center=center)
        self.hover = False

    def draw(self, screen: pygame.Surface) -> None:
        if self.hover:
            scaled = pygame.transform.smoothscale(
                self.image,
                (int(self.rect.width * 1.08), int(self.rect.height * 1.08)),
            )
            r = scaled.get_rect(center=self.rect.center)
            screen.blit(scaled, r)
        else:
            screen.blit(self.image, self.rect)

    def check_hover(self, pos: tuple[int, int]) -> None:
        self.hover = self.rect.collidepoint(pos)

    def clicked(self, pos: tuple[int, int]) -> bool:
        return self.rect.collidepoint(pos)


def _load_image(path: str) -> pygame.Surface:
    return pygame.image.load(path).convert_alpha()


class MainMenu:
    """Full-screen landing page shown before gameplay begins."""

    def __init__(self, art_root: str) -> None:
        info = pygame.display.Info()
        self.display_w = max(800, info.current_w - 40)
        self.display_h = max(600, info.current_h - 80)

        bg_dir = os.path.join(art_root, "Backrounds & Menus")
        btn_dir = os.path.join(art_root, "UI and Buttons")

        self.bg_start = _load_image(os.path.join(bg_dir, "Start Screen.png"))
        self.bg_controls = _load_image(os.path.join(bg_dir, "Controls Menu Background.png"))
        self.bg_rules = _load_image(os.path.join(bg_dir, "Rules Menu Background.png"))

        self.img_play = _load_image(os.path.join(btn_dir, "Play Button.png"))
        self.img_controls = _load_image(os.path.join(btn_dir, "Controls Button.png"))
        self.img_rules = _load_image(os.path.join(btn_dir, "Rules Button.png"))
        self.img_back = _load_image(os.path.join(btn_dir, "Back Button.png"))
        self.img_close = _load_image(os.path.join(btn_dir, "Close Game Button.png"))

        self.menu_w = min(940, self.display_w)
        self.menu_h = min(788, self.display_h)

        self._scale_backgrounds()

        self.state = _MenuState.START
        self._build_start_buttons()

    def _scale_backgrounds(self) -> None:
        self.bg_start_scaled = pygame.transform.smoothscale(self.bg_start, (self.menu_w, self.menu_h))
        self.bg_controls_scaled = pygame.transform.smoothscale(self.bg_controls, (self.menu_w, self.menu_h))
        self.bg_rules_scaled = pygame.transform.smoothscale(self.bg_rules, (self.menu_w, self.menu_h))

    def _build_start_buttons(self) -> None:
        cx = self.menu_w // 2
        btn_y = int(self.menu_h * 0.82)
        btn_scale = min(0.18, self.menu_w / 5000)

        self.btn_play = _Button(self.img_play, (cx, btn_y), scale=btn_scale)
        self.btn_controls = _Button(self.img_controls, (cx - int(self.menu_w * 0.2), btn_y), scale=btn_scale * 0.8)
        self.btn_rules = _Button(self.img_rules, (cx + int(self.menu_w * 0.2), btn_y), scale=btn_scale * 0.8)
        self.btn_close = _Button(self.img_close, (self.menu_w - 40, 36), scale=btn_scale * 0.55)

    def _build_overlay_buttons(self) -> None:
        btn_scale = min(0.16, self.menu_w / 5500)
        self.btn_back = _Button(self.img_back, (60, self.menu_h - 50), scale=btn_scale)

    def get_window_size(self) -> tuple[int, int]:
        return self.menu_w, self.menu_h

    def handle_event(self, ev: pygame.event.Event) -> MenuResult:
        if ev.type == pygame.MOUSEMOTION:
            self._update_hover(ev.pos)
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            return self._handle_click(ev.pos)
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                if self.state in (_MenuState.CONTROLS, _MenuState.RULES):
                    self.state = _MenuState.START
                    return MenuResult.NONE
                return MenuResult.QUIT
            if ev.key == pygame.K_RETURN and self.state == _MenuState.START:
                return MenuResult.PLAY
        return MenuResult.NONE

    def _update_hover(self, pos: tuple[int, int]) -> None:
        if self.state == _MenuState.START:
            self.btn_play.check_hover(pos)
            self.btn_controls.check_hover(pos)
            self.btn_rules.check_hover(pos)
            self.btn_close.check_hover(pos)
        elif self.state in (_MenuState.CONTROLS, _MenuState.RULES):
            self.btn_back.check_hover(pos)

    def _handle_click(self, pos: tuple[int, int]) -> MenuResult:
        if self.state == _MenuState.START:
            if self.btn_play.clicked(pos):
                return MenuResult.PLAY
            if self.btn_controls.clicked(pos):
                self.state = _MenuState.CONTROLS
                self._build_overlay_buttons()
            elif self.btn_rules.clicked(pos):
                self.state = _MenuState.RULES
                self._build_overlay_buttons()
            elif self.btn_close.clicked(pos):
                return MenuResult.QUIT
        elif self.state in (_MenuState.CONTROLS, _MenuState.RULES):
            if self.btn_back.clicked(pos):
                self.state = _MenuState.START
        return MenuResult.NONE

    def draw(self, screen: pygame.Surface) -> None:
        if self.state == _MenuState.START:
            self._draw_start(screen)
        elif self.state == _MenuState.CONTROLS:
            self._draw_overlay(screen, self.bg_controls_scaled)
        elif self.state == _MenuState.RULES:
            self._draw_overlay(screen, self.bg_rules_scaled)

    def _draw_start(self, screen: pygame.Surface) -> None:
        screen.blit(self.bg_start_scaled, (0, 0))
        self.btn_play.draw(screen)
        self.btn_controls.draw(screen)
        self.btn_rules.draw(screen)
        self.btn_close.draw(screen)

    def _draw_overlay(self, screen: pygame.Surface, bg: pygame.Surface) -> None:
        screen.blit(bg, (0, 0))
        self.btn_back.draw(screen)
