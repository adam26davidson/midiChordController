import json

MIN_NOTE = 21
MAX_NOTE = 108
MAX_SPREAD_OCTAVES = 5
SPREAD_STEPS_PER_OCTAVE = 6
MAX_INVERSION_RANGE = 20
MAX_BASS_RANGE = 15
INVERSION_SNAP = 0.2
ANIMATION_STEP = 1.0/20.0
CENTER_NOTE = 65 # center of home chord range
BASS_OCTAVE_RANGE = {"min": 34, "max": 45}
VOICING_PATTERNS = json.load(open("voicingPatterns.json"))
SETTINGS = json.load(open("settings.json"))