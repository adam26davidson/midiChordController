from .dualChord import DualChord


def parseSecondaries(settings):
    def parseSecondary(setting):
        secondaries = {}
        default = DualChord(setting, isSecondary=True)
        buttons = ["south", "west", "north", "east"]

        def getOverrideSecondary(overides):
            overideSettings = setting.copy()
            for key in overides:
                overideSettings[key] = overides[key]
            return DualChord(overideSettings, isSecondary=True)

        for button in buttons:
            if not (button in setting):
                secondaries[button] = {
                    "default": default,
                    "leftModulation": default,
                    "rightModulation": default
                }
            else:
                secondaries[button] = {}
                for key in "default", "leftModulation", "rightModulation":
                    if key in setting[button]:
                        secondaries[button][key] = getOverrideSecondary(
                            setting[button][key])
                    else:
                        secondaries[button][key] = default
        return secondaries

    left = parseSecondary(settings["left"])
    right = parseSecondary(settings["right"])
    return {"left": left, "right": right}
