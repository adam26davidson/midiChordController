import json
import logging
import os
import sys
from typing import TypedDict

logger = logging.getLogger(__name__)


class SettingPreset(TypedDict):
    """Schema for a single chord preset loaded from settings.json.

    Each preset defines a scale, chord voicings per button, modulation
    transformations, and secondary (chromatic) chord overlays.
    """
    name: str
    scale: list[int]
    chords: dict[str, dict]
    modulations: dict[str, dict]
    secondaries: dict[str, dict]

PARENT_PATH = os.path.dirname(os.path.abspath(__file__))
FULLSCREEN = True
MIN_NOTE = 21
MAX_NOTE = 108
MAX_VOICE_COUNT = 10
MAX_SPREAD_OCTAVES = 5
SPREAD_STEPS_PER_OCTAVE = 6
MAX_INVERSION_RANGE = 20
MAX_BASS_RANGE = 15
MAX_OCTAVE_SHIFT = 3
INVERSION_SNAP = 0.15  # hysteresis dead zone for analog-to-discrete inversion snapping
ANIMATION_STEP = 1.0/60.0
MIDI_OUTPUT_STEP = 1.0/20.0
MIDI_INPUT_STEP = 1.0/200.0
CENTER_NOTE = 65  # MIDI note at center of chord voicing range (F4)
BASS_CENTER = 42  # MIDI note at center of bass voicing range (F#2)
BASS_OCTAVE_RANGE = {"min": 36, "max": 47}

VOICING_PATTERN_PATH = \
    "/music_engine/chord_engine/modules/voicing_patterns/voicing_patterns.json"
try:
    with open(PARENT_PATH + VOICING_PATTERN_PATH) as _f:
        VOICING_PATTERNS: dict[str, dict[str, list[list[int]]]] = json.load(_f)['voicingPatterns']
except (OSError, json.JSONDecodeError, KeyError) as e:
    logger.critical("Failed to load voicing patterns from %s: %s", VOICING_PATTERN_PATH, e)
    sys.exit(1)

try:
    with open(PARENT_PATH + "/music_engine/chord_engine/internal_chord_engine/modules/settings/settings.json") as _f:
        SETTINGS: list[SettingPreset] = json.load(_f)
except (OSError, json.JSONDecodeError) as e:
    logger.critical("Failed to load settings presets: %s", e)
    sys.exit(1)
