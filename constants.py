import json

MIN_NOTE = 21
MAX_NOTE = 108
MAX_SPREAD_OCTAVES = 5
SPREAD_STEPS_PER_OCTAVE = 6
MAX_INVERSION_RANGE = 20
INVERSION_SNAP = 0.4
CENTER_NOTE = 60 # center of home chord range
BASS_OCTAVE_RANGE = {"min": 31, "max": 42}
VOICING_PATTERNS = json.load(open("voicingPatterns.json"))
SETTINGS = json.load(open("settings.json"))