"""Generate original, kid-friendly instrumental rhyme tracks as local WAV files."""
from __future__ import annotations

import math
import random
import struct
import wave
from pathlib import Path

SAMPLE_RATE = 22050
BEAT = 0.68
OUT = Path(__file__).resolve().parent / "static" / "audio"

# Each tune is an original bright instrumental arrangement in C major.
# Notes use MIDI numbers; durations are in beats.
SONGS = {
    "twinkle": [(60,1),(60,1),(67,1),(67,1),(69,1),(69,1),(67,2),(65,1),(65,1),(64,1),(64,1),(62,1),(62,1),(60,2)],
    "wheels": [(67,.5),(67,.5),(67,1),(69,.5),(67,.5),(65,1),(64,.5),(64,.5),(64,1),(65,.5),(64,.5),(62,1),(60,.5),(62,.5),(64,1),(60,2)] * 2,
    "mary": [(64,.5),(62,.5),(60,1),(62,.5),(64,.5),(64,.5),(64,1),(62,.5),(62,.5),(62,1),(64,.5),(67,.5),(67,1),(64,.5),(62,.5),(60,1),(62,.5),(64,.5),(64,.5),(64,.5),(64,.5),(62,.5),(62,.5),(64,.5),(62,.5),(60,2)],
    "oldmacdonald": [(67,.5),(67,.5),(67,.5),(67,.5),(67,.5),(67,.5),(67,1),(64,.5),(64,.5),(64,.5),(64,.5),(64,1),(67,.5),(67,.5),(67,.5),(67,.5),(67,.5),(67,.5),(67,1),(67,.5),(67,.5),(67,.5),(67,.5),(67,.5),(67,.5),(67,1),(67,.5),(67,.5),(67,.5),(67,.5),(67,.5),(67,.5),(67,2)],
    "rowboat": [(60,.5),(60,.5),(60,1),(62,.5),(64,.5),(64,1),(62,.5),(64,.5),(67,1),(67,.5),(64,.5),(64,1),(60,.5),(60,.5),(60,2)],
    "itsybitsy": [(60,.5),(64,.5),(67,1),(67,.5),(69,.5),(67,1),(64,.5),(64,.5),(65,1),(64,.5),(62,.5),(60,1),(60,.5),(62,.5),(64,1),(60,2)],
}


def freq(midi: int) -> float:
    return 440.0 * (2.0 ** ((midi - 69) / 12.0))


def add_voice(mix: list[float], start: int, duration: int, frequency: float,
              amplitude: float, partials: tuple[tuple[int, float], ...],
              decay: float = 2.8, soft: bool = False) -> None:
    end = min(len(mix), start + duration)
    if end <= start:
        return
    attack = max(1, int(0.018 * SAMPLE_RATE))
    release = max(1, int(0.055 * SAMPLE_RATE))
    for frame in range(start, end):
        offset = frame - start
        t = offset / SAMPLE_RATE
        if soft:
            env = min(1.0, offset / (0.10 * SAMPLE_RATE)) * min(1.0, (end - frame) / (0.16 * SAMPLE_RATE))
        else:
            env = min(1.0, offset / attack) * math.exp(-decay * t)
            if end - frame < release:
                env *= max(0.0, (end - frame) / release)
        phase = 2.0 * math.pi * frequency * t
        tone = sum(weight * math.sin(harmonic * phase) for harmonic, weight in partials)
        mix[frame] += amplitude * env * tone


def make_song(song_id: str, notes: list[tuple[int, float]]) -> None:
    total_beats = sum(beats for _, beats in notes)
    total_frames = int((total_beats * BEAT + 1.1) * SAMPLE_RATE)
    mix = [0.0] * total_frames
    chord_roots = [48, 53, 55, 48]  # C, F, G, C
    cursor_beats = 0.0
    randomizer = random.Random(song_id)

    for note_index, (midi, beats) in enumerate(notes):
        start = int(cursor_beats * BEAT * SAMPLE_RATE)
        note_frames = int(beats * BEAT * SAMPLE_RATE * 0.94)
        # Bell-like marimba lead, soft enough to leave space for children singing.
        add_voice(mix, start, note_frames, freq(midi), 0.23,
                  ((1, 1.0), (2, 0.22), (3, 0.07)), decay=2.2)
        # Gentle bass and chord pad mark each four-beat bar.
        if cursor_beats % 4 == 0:
            root = chord_roots[int(cursor_beats // 4) % len(chord_roots)]
            bar_frames = int(min(4.0, total_beats - cursor_beats) * BEAT * SAMPLE_RATE)
            add_voice(mix, start, bar_frames, freq(root), 0.11, ((1, 1.0),), decay=0.5, soft=True)
            for interval in (4, 7):
                add_voice(mix, start, bar_frames, freq(root + interval), 0.026,
                          ((1, 1.0),), decay=0.5, soft=True)
        # A tiny wooden click on each beat gives the melody a playful pulse.
        click_frames = int(0.045 * SAMPLE_RATE)
        click_freq = 1250 + randomizer.randrange(-80, 81)
        add_voice(mix, start, click_frames, click_freq, 0.014,
                  ((1, 1.0),), decay=28.0)
        cursor_beats += beats

    peak = max(max(mix), -min(mix), 1e-9)
    gain = 0.88 / peak
    pcm = bytearray()
    for sample in mix:
        value = max(-1.0, min(1.0, sample * gain))
        pcm.extend(struct.pack("<h", int(value * 32767)))

    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"{song_id}.wav"
    with wave.open(str(path), "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(SAMPLE_RATE)
        audio.writeframes(pcm)
    print(f"Created {path.name} ({total_beats * BEAT:.1f} seconds)")


if __name__ == "__main__":
    for name, notes in SONGS.items():
        make_song(name, notes)