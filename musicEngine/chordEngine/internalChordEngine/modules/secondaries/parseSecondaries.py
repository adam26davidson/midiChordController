from typing import Dict
from musicEngine.chordEngine.state.modulationsState import ModulationSide
from musicEngine.chordEngine.state.secondariesState import SecondarySide
from musicEngine.chordEngine.state.chordsState import ChordButton
from ....modules.chords.dualChord import DualChord

modKeyMap = {
    "default": ModulationSide.NONE,
    "leftModulation": ModulationSide.LEFT,
    "rightModulation": ModulationSide.RIGHT
}


def parseSecondaries(settings) -> Dict[SecondarySide, Dict[ChordButton, Dict[ModulationSide, DualChord]]]:
    def parseSecondary(setting) -> Dict[ChordButton, Dict[ModulationSide, DualChord]]:
        secondaries = {}
        default = DualChord(setting, isSecondary=True)
        buttonsKeys = [ChordButton.SOUTH, ChordButton.WEST, ChordButton.NORTH, ChordButton.EAST]

        def getOverrideSecondary(overides):
            overideSettings = setting.copy()
            for key in overides:
                overideSettings[key] = overides[key]
            return DualChord(overideSettings, isSecondary=True)

        for buttonKey in buttonsKeys:
            if not (buttonKey.value in setting):
                secondaries[buttonKey] = {
                    ModulationSide.NONE: default,
                    ModulationSide.LEFT: default,
                    ModulationSide.RIGHT: default
                }
            else:
                secondaries[buttonKey] = {}
                for key in modKeyMap.keys():
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
