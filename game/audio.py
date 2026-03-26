"""
Procedural audio manager — generates all sounds at runtime so no .wav/.ogg
files are needed.  Uses pygame.mixer for playback.
"""
from __future__ import annotations

import math
import struct

import pygame


_TWO_PI = 2.0 * math.pi


def _make_samples(sample_rate: int, duration_s: float) -> int:
    return int(sample_rate * duration_s)


def _sine(freq: float, t: float) -> float:
    return math.sin(_TWO_PI * freq * t)


def _generate_tone(
    freq: float,
    duration_ms: int,
    volume: float = 0.25,
    fade_ms: int = 30,
    sample_rate: int = 44100,
) -> pygame.mixer.Sound:
    n = _make_samples(sample_rate, duration_ms / 1000)
    fade_n = _make_samples(sample_rate, fade_ms / 1000)
    buf = bytearray(n * 4)  # 16-bit stereo
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


def _generate_ambient(
    root_freqs: list[float],
    duration_ms: int,
    volume: float = 0.06,
    detune_cents: float = 6.0,
    lfo_hz: float = 0.15,
    lfo_depth: float = 0.35,
    pan_hz: float = 0.05,
    pan_amount: float = 0.20,
    fade_ms: int = 2500,
    sample_rate: int = 44100,
) -> pygame.mixer.Sound:
    """
    Rich ambient pad — detuned oscillator pairs per note, sub-octave warmth,
    slow LFO tremolo, and gentle stereo panning for spatial movement.
    """
    n = _make_samples(sample_rate, duration_ms / 1000)
    fade_n = _make_samples(sample_rate, fade_ms / 1000)
    detune_ratio = 2.0 ** (detune_cents / 1200.0)

    voices: list[tuple[float, float, float]] = []
    for f in root_freqs:
        voices.append((f, f * detune_ratio, 1.0))
        voices.append((f * 0.5, f * 0.5 * detune_ratio, 0.35))
        voices.append((f * 2.0, f * 2.0 * detune_ratio, 0.10))

    mix = 1.0 / max(1, len(voices))
    buf = bytearray(n * 4)

    for i in range(n):
        t = i / sample_rate

        lfo = 1.0 - lfo_depth * (0.5 + 0.5 * math.sin(_TWO_PI * lfo_hz * t))
        pan_lfo = math.sin(_TWO_PI * pan_hz * t) * pan_amount

        val = 0.0
        for f1, f2, gain in voices:
            val += (math.sin(_TWO_PI * f1 * t) + math.sin(_TWO_PI * f2 * t)) * 0.5 * gain
        val *= mix * lfo

        env = 1.0
        if i < fade_n:
            env = i / max(1, fade_n)
        elif i > n - fade_n:
            env = (n - i) / max(1, fade_n)

        mono = val * volume * 32767 * env
        left = int(max(-32767, min(32767, mono * (1.0 + pan_lfo))))
        right = int(max(-32767, min(32767, mono * (1.0 - pan_lfo))))
        struct.pack_into("<hh", buf, i * 4, left, right)

    return pygame.mixer.Sound(buffer=bytes(buf))


class AudioManager:
    """Singleton-style audio manager initialised once."""

    DEFAULT_VOLUME = 0.7

    def __init__(self) -> None:
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
            self._available = True
        except pygame.error:
            self._available = False
            return

        self.music_on = True
        self.sfx_on = True
        self._master_volume: float = self.DEFAULT_VOLUME
        self._music_channel: pygame.mixer.Channel | None = None

        self._build_sfx()
        self._build_music()
        self._apply_volume()

    @property
    def available(self) -> bool:
        return self._available

    @property
    def volume(self) -> float:
        return self._master_volume

    def set_volume(self, vol: float) -> None:
        self._master_volume = max(0.0, min(1.0, vol))
        self._apply_volume()

    def _apply_volume(self) -> None:
        if not self._available:
            return
        v = self._master_volume
        for attr in dir(self):
            if attr.startswith("sfx_"):
                snd = getattr(self, attr)
                if isinstance(snd, pygame.mixer.Sound):
                    snd.set_volume(v)
        if self._music_channel is not None:
            self._music_channel.set_volume(v * 0.8)

    # ── SFX ───────────────────────────────────────────────────────────
    def _build_sfx(self) -> None:
        self.sfx_click = _generate_tone(660, 60, volume=0.15, fade_ms=15)
        self.sfx_move = _generate_tone(440, 50, volume=0.10, fade_ms=10)
        self.sfx_clue = _generate_ambient(
            [523, 659, 784], 250, volume=0.14, fade_ms=60, lfo_depth=0.0,
        )
        self.sfx_complete = _generate_ambient(
            [523, 659, 784, 1047], 600, volume=0.18, fade_ms=120, lfo_depth=0.0,
        )
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
        dur = 20000

        self._music_tracks["Office"] = _generate_ambient(
            [261.6, 329.6, 392.0, 493.9],
            dur, volume=0.32, detune_cents=8.0,
            lfo_hz=0.10, lfo_depth=0.28, pan_hz=0.04, pan_amount=0.18,
            fade_ms=3500,
        )
        self._music_tracks["Elevator"] = _generate_ambient(
            [220.0, 261.6, 329.6, 493.9],
            dur, volume=0.28, detune_cents=5.0,
            lfo_hz=0.06, lfo_depth=0.22, pan_hz=0.03, pan_amount=0.22,
            fade_ms=5000,
        )
        self._music_tracks["_default"] = _generate_ambient(
            [246.9, 293.7, 370.0, 440.0],
            dur, volume=0.30, detune_cents=6.0,
            lfo_hz=0.08, lfo_depth=0.25, pan_hz=0.035, pan_amount=0.20,
            fade_ms=4000,
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
            self._music_channel.set_volume(self._master_volume * 0.8)

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
