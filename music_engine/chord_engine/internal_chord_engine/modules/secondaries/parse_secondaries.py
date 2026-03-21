
from music_engine.chord_engine.state.chords_state import ChordButton
from music_engine.chord_engine.state.modulations_state import ModulationSide
from music_engine.chord_engine.state.secondaries_state import SecondarySide

from ....modules.chords.dual_chord import DualChord

mod_key_map = {
    "default": ModulationSide.NONE,
    "leftModulation": ModulationSide.LEFT,
    "rightModulation": ModulationSide.RIGHT
}


def parse_secondaries(settings) -> dict[SecondarySide, dict[ChordButton, dict[ModulationSide, DualChord]]]:
    def parse_secondary(setting) -> dict[ChordButton, dict[ModulationSide, DualChord]]:
        secondaries = {}
        default = DualChord(setting, is_secondary=True)
        buttons_keys = [ChordButton.SOUTH, ChordButton.WEST, ChordButton.NORTH, ChordButton.EAST]

        def get_override_secondary(overrides):
            override_settings = setting.copy()
            for key in overrides:
                override_settings[key] = overrides[key]
            return DualChord(override_settings, is_secondary=True)

        for button_key in buttons_keys:
            if button_key.value not in setting:
                secondaries[button_key] = {
                    ModulationSide.NONE: default,
                    ModulationSide.LEFT: default,
                    ModulationSide.RIGHT: default
                }
            else:
                secondaries[button_key] = {}
                for key in mod_key_map:
                    if key in setting[button_key.value]:
                        secondaries[button_key][mod_key_map[key]] = get_override_secondary(
                            setting[button_key.value][key])
                    else:
                        secondaries[button_key][mod_key_map[key]] = default
        return secondaries

    return {
        SecondarySide.LEFT: parse_secondary(settings["left"]),
        SecondarySide.RIGHT: parse_secondary(settings["right"])
    }
