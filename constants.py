import json, os
PARENT_PATH = os.path.dirname(os.path.abspath(__file__))
FULLSCREEN = True
MIN_NOTE = 21
MAX_NOTE = 108
MAX_VOICE_COUNT = 8
MAX_SPREAD_OCTAVES = 5
SPREAD_STEPS_PER_OCTAVE = 6
MAX_INVERSION_RANGE = 20
MAX_BASS_RANGE = 15
MAX_OCTAVE_SHIFT = 3
INVERSION_SNAP = 0.15
ANIMATION_STEP = 1.0/30.0
MIDI_STEP = 1.0/20.0
CENTER_NOTE = 65 # center of home chord
BASS_OCTAVE_RANGE = {"min": 36, "max": 47}
VOICING_PATTERNS = json.load(open(PARENT_PATH + "/musicEngine/chordEngine/modules/voicingPatterns/testPatterns.json"))['voicingPatterns']
SETTINGS = json.load(open(PARENT_PATH + "/musicEngine/chordEngine/settings.json"))