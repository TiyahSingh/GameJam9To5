"""
Procedural audio manager — generates all sounds at runtime so no .wav/.ogg
files are needed.  Uses pygame.mixer for playback.
"""
from __future__ import annotations

import math
import struct

import pygame


def _make_samples(sample_rate: int, duration_s: float) -> int:
    return int(sample_rate * duration_s)


def _sine(freq: float, t: float) -> float:
    return math.sin(2.0 * math.pi * freq * t)


def _generate_tone(
    freq: float,
    duration_ms: int,
    volume: float = 0.25,
    fade_ms: int = 30,
    sample_rate: int = 44100,
) -> pygame.mixer.Sound:
    n = _make_samples(sample_rate, duration_ms / 1000)
    fade_n = _make_samples(sample_rate, fade_ms / 1000)
    buf = bytearray(n * 2 * 2)  # 16-bit stereo
    for i in range(n):
        t = i / sample_rate
        val = _sine(freq, t)
        env = 1.0
        if i < fade_n:
            env = i / max(1, fade_n)
        elif i > n - fade_n:
            env = (n - i) / max(1, fade_n)
        sample = int(max(-32767, min(32767, val * volume * 32767 * env)))
        struct.pack_into("<hh", buf, i * 4, sample, sample)
    return pygame.mixer.Sound(buffer=bytes(buf))


def _generate_chord(
    freqs: list[float],
    duration_ms: int,
    volume: float = 0.12,
    fade_ms: int = 200,
    sample_rate: int = 44100,
) -> pygame.mixer.Sound:
    n = _make_samples(sample_rate, duration_ms / 1000)
    fade_n = _make_samples(sample_rate, fade_ms / 1000)
    mix = 1.0 / max(1, len(freqs))
    buf = bytearray(n * 2 * 2)
    for i in range(n):
        t = i / sample_rate
        val = sum(_sine(f, t) for f in freqs) * mix
        env = 1.0
        if i < fade_n:
            env = i / max(1, fade_n)
        elif i > n - fade_n:
            env = (n - i) / max(1, fade_n)
        sample = int(max(-32767, min(32767, val * volume * 32767 * env)))
        struct.pack_into("<hh", buf, i * 4, sample, sample)
    return pygame.mixer.Sound(buffer=bytes(buf))


class AudioManager:
    """Singleton-style audio manager initialised once."""

    def __init__(self) -> None:
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
            self._available = True
        except pygame.error:
            self._available = False
            return

        self.music_on = True
        self.sfx_on = True
        self._music_channel: pygame.mixer.Channel | None = None

        self._build_sfx()
        self._build_music()

    @property
    def available(self) -> bool:
        return self._available

    # ── SFX ───────────────────────────────────────────────────────────
    def _build_sfx(self) -> None:
        self.sfx_click = _generate_tone(660, 60, volume=0.15, fade_ms=15)
        self.sfx_move = _generate_tone(440, 50, volume=0.10, fade_ms=10)
        self.sfx_clue = _generate_chord([523, 659, 784], 200, volume=0.14)
        self.sfx_complete = _generate_chord([523, 659, 784, 1047], 500, volume=0.18, fade_ms=100)
        self.sfx_fail = _generate_tone(220, 180, volume=0.18, fade_ms=40)
        self.sfx_pause_open = _generate_tone(500, 80, volume=0.12, fade_ms=20)
        self.sfx_pause_close = _generate_tone(400, 80, volume=0.12, fade_ms=20)

    def play_sfx(self, name: str) -> None:
        if not self._available or not self.sfx_on:
            return
        snd: pygame.mixer.Sound | None = getattr(self, f"sfx_{name}", None)
        if snd is not None:
            snd.play()

    # ── Music ─────────────────────────────────────────────────────────
    def _build_music(self) -> None:
        self._music_tracks: dict[str, pygame.mixer.Sound] = {}
        dur = 8000

        self._music_tracks["Office"] = _generate_chord(
            [261.6, 329.6, 392.0, 523.2], dur, volume=0.06, fade_ms=1500,
        )
        self._music_tracks["Elevator"] = _generate_chord(
            [220.0, 277.2, 330.0, 440.0], dur, volume=0.05, fade_ms=2000,
        )
        self._music_tracks["_default"] = _generate_chord(
            [246.9, 311.1, 370.0, 493.9], dur, volume=0.05, fade_ms=1500,
        )

        self._current_theme: str | None = None

    def _track_for_theme(self, theme: str) -> pygame.mixer.Sound:
        return self._music_tracks.get(theme, self._music_tracks["_default"])

    def play_music(self, theme: str) -> None:
        if not self._available:
            return
        if not self.music_on:
            self.stop_music()
            return

        if self._current_theme == theme:
            return
        self._current_theme = theme

        self.stop_music()
        track = self._track_for_theme(theme)
        self._music_channel = track.play(loops=-1)
        if self._music_channel is not None:
            self._music_channel.set_volume(0.5)

    def stop_music(self) -> None:
        if self._music_channel is not None:
            self._music_channel.stop()
            self._music_channel = None

    def set_music_on(self, on: bool) -> None:
        self.music_on = on
        if not on:
            self.stop_music()
            self._current_theme = None
        elif self._current_theme is not None:
            theme = self._current_theme
            self._current_theme = None
            self.play_music(theme)
