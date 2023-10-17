from controllerCoupler.models.controlMap import ControlMap


defaultControlMap = ControlMap(
    name = "default",
    displayName = "Default",
    inversionMode = "continuous",
    bassMode = "continuous",
    map = {
      
        #MAIN BUTTONS
        "SOUTH_BUTTON": ["SOUTH_CHORD"],
        "WEST_BUTTON": ["WEST_CHORD"],
        "NORTH_BUTTON": ["NORTH_CHORD"],
        "EAST_BUTTON": ["EAST_CHORD"],

        #DPAD
        "DPAD_X_LEFT": ["LEFT_SECONDARY"],
        "DPAD_X_RIGHT": ["RIGHT_SECONDARY"],

        "DPAD_Y": ["OCTAVE"],

        #LEFT STICK
        "LEFT_STICK_Y_POLAR": ["OCTAVE"],
        "LEFT_STICK_X_POLAR": ["VOICE_COUNT"],

        #STICK BUTTONS
        "RIGHT_STICK_BUTTON": ["INCREMENT_SETTING"],
        "LEFT_STICK_BUTTON": ["DECREMENT_SETTING"],

        #RIGHT STICK
        "RIGHT_STICK_Y": ["KEY"],
        "RIGHT_STICK_X": ["SPREAD"],

        #BUMPERS
        "RIGHT_BUMPER": ["RIGHT_MODULATION"],
        "LEFT_BUMPER": ["LEFT_MODULATION"],

        #TRIGGERS
        "RIGHT_TRIGGER": ["ALTERNATE"],
        "LEFT_TRIGGER": ["BASS"],

        #OPTIONS
        "LEFT_OPTION": ["INVERSION_LOCK"],
        "RIGHT_OPTION": ["HOLD"],

        #TOUCHPAD
        "TOUCHPAD_X": ["BASS_POSITION"],

        #UI
        "MENU": ["MENU"],

        #GYROSCOPE
        "GYRO_PITCH": ["INVERSION", "UI_INVERSION_THUMB"],
        "GYRO_ROLL": ["BASS", "UI_BASS_THUMB"],
  }
)