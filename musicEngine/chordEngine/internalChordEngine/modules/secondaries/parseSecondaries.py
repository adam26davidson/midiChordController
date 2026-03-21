
from musicEngine.chordEngine.state.chordsState import ChordButton
from musicEngine.chordEngine.state.modulationsState import ModulationSide
from musicEngine.chordEngine.state.secondariesState import SecondarySide

from ....modules.chords.dualChord import DualChord

modKeyMap = {
    "default": ModulationSide.NONE,
    "leftModulation": ModulationSide.LEFT,
    "rightModulation": ModulationSide.RIGHT
}


def parseSecondaries(settings) -> dict[SecondarySide, dict[ChordButton, dict[ModulationSide, DualChord]]]:
    def parseSecondary(setting) -> dict[ChordButton, dict[ModulationSide, DualChord]]:
        secondaries = {}
        default = DualChord(setting, isSecondary=True)
        buttonsKeys = [ChordButton.SOUTH, ChordButton.WEST, ChordButton.NORTH, ChordButton.EAST]

        def getOverrideSecondary(overides):
            overideSettings = setting.copy()
            for key in overides:
                overideSettings[key] = overides[key]
            return DualChord(overideSettings, isSecondary=True)

        for buttonKey in buttonsKeys:
            if buttonKey.value not in setting:
                secondaries[buttonKey] = {
                    ModulationSide.NONE: default,
                    ModulationSide.LEFT: default,
                    ModulationSide.RIGHT: default
                }
            else:
                secondaries[buttonKey] = {}
                for key in modKeyMap:
                    if key in setting[buttonKey.value]:
                        secondaries[buttonKey][modKeyMap[key]] = getOverrideSecondary(
                            setting[buttonKey.value][key])
                    else:
                        secondaries[buttonKey][modKeyMap[key]] = default
        return secondaries

    return {
        SecondarySide.LEFT: parseSecondary(settings["left"]),
        SecondarySide.RIGHT: parseSecondary(settings["right"])
    }
