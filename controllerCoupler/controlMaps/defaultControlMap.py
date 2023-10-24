from controllerCoupler.models.controlMap import ControlMap


defaultControlMap = ControlMap(
    name = "default",
    displayName = "Default",
    inversionMode = "continuous",
    bassMode = "continuous",
    map = {
      
        #MAIN BUTTONS
        "SOUTH_BUTTON": ["SOUTH_CHORD", "UI_SOUTH_BUTTON"],
        "WEST_BUTTON": ["WEST_CHORD", "UI_WEST_BUTTON"],
        "NORTH_BUTTON": ["NORTH_CHORD", "UI_NORTH_BUTTON"],
        "EAST_BUTTON": ["EAST_CHORD", "UI_EAST_BUTTON"],

        #DPAD
        "DPAD_X_LEFT": ["LEFT_SECONDARY", "UI_DPAD_LEFT"],
        "DPAD_X_RIGHT": ["RIGHT_SECONDARY", "UI_DPAD_RIGHT"],

        "DPAD_Y": ["OCTAVE"],
        "DPAD_Y_UP": ["UI_DPAD_UP"],
        "DPAD_Y_DOWN": ["UI_DPAD_DOWN"],

        #LEFT STICK
        "LEFT_STICK_Y_POLAR": ["OCTAVE"],
        "LEFT_STICK_X_POLAR": ["VOICE_COUNT"],

        "LEFT_STICK_Y_DOWN": ["UI_LEFT_STICK_DOWN"],
        "LEFT_STICK_Y_UP": ["UI_LEFT_STICK_UP"],
        "LEFT_STICK_X_LEFT": ["UI_LEFT_STICK_LEFT"],
        "LEFT_STICK_X_RIGHT": ["UI_LEFT_STICK_RIGHT"],

        #STICK BUTTONS
        "RIGHT_STICK_BUTTON": ["INCREMENT_SETTING", "UI_RIGHT_STICK_BUTTON"],
        "LEFT_STICK_BUTTON": ["DECREMENT_SETTING", "UI_LEFT_STICK_BUTTON"],

        #RIGHT STICK
        "RIGHT_STICK_Y_POLAR": ["KEY"],
        "RIGHT_STICK_X_POLAR": ["SPREAD"],

        "RIGHT_STICK_Y_DOWN": ["UI_RIGHT_STICK_DOWN"],
        "RIGHT_STICK_Y_UP": ["UI_RIGHT_STICK_UP"],
        "RIGHT_STICK_X_LEFT": ["UI_RIGHT_STICK_LEFT"],
        "RIGHT_STICK_X_RIGHT": ["UI_RIGHT_STICK_RIGHT"],

        #BUMPERS
        "RIGHT_BUMPER": ["RIGHT_MODULATION", "UI_RIGHT_BUMPER"],
        "LEFT_BUMPER": ["LEFT_MODULATION", "UI_LEFT_BUMPER"],

        #TRIGGERS
        "RIGHT_TRIGGER": ["ALTERNATE", "UI_RIGHT_TRIGGER"],
        "LEFT_TRIGGER": ["BASS", "UI_LEFT_TRIGGER"],

        #OPTIONS
        "LEFT_OPTION": ["INVERSION_LOCK", "UI_LEFT_OPTION"],
        "RIGHT_OPTION": ["HOLD", "UI_RIGHT_OPTION"],

        #TOUCHPAD
        "TOUCHPAD_X": ["BASS_POSITION", "UI_TOUCHPAD_X", "UI_BASS_THUMB"],
        "TOUCHPAD_Y": ["UI_TOUCHPAD_Y"],

        #UI
        "START_BUTTON": ["MENU"],

        #GYROSCOPE
        "GYRO_PITCH": ["INVERSION", "UI_INVERSION_THUMB"],
        "GYRO_ROLL": ["BASS"],
  }
)