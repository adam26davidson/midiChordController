info = {
  "name": "DualShock4",
  "vendor": 1356,
  "product": 2508,
  "meMap": "gyroInversions",
  'uiMap': 'default',
  "compatibleMeMaps": ['gyroInversions', 'default'],
  "controls": {
    "main": {
      # MAIN BUTTONS
      304: {
        "name": "SOUTH_BUTTON",
        "type": "BUTTON",
        "events":{ 1: "SOUTH_BUTTON_DOWN", 0: "SOUTH_BUTTON_UP" }
      },
      308: {
        "name": "WEST_BUTTON",
        "type": "BUTTON",
        "events":{ 1: "WEST_BUTTON_DOWN", 0: "WEST_BUTTON_UP" }
      },
      307: {
        "name": "NORTH_BUTTON",
        "type": "BUTTON",
        "events":{ 1: "NORTH_BUTTON_DOWN", 0: "NORTH_BUTTON_UP" }
      },
      305: {
        "name": "EAST_BUTTON",
        "type": "BUTTON",
        "events":{ 1: "EAST_BUTTON_DOWN", 0: "EAST_BUTTON_UP" }
      },

      # BUMPERS
      311: {
        "name": "RIGHT_BUMPER",
        "type": "BUTTON",
        "events":{ 1: "RIGHT_BUMPER_DOWN", 0: "RIGHT_BUMPER_UP" }
      },
      310: {
        "name": "LEFT_BUMPER",
        "type": "BUTTON",
        "events":{ 1: "LEFT_BUMPER_DOWN", 0: "LEFT_BUMPER_UP" }
      },

      # TRIGGERS
      313: {
        "name": "RIGHT_TRIGGER",
        "type": "BUTTON",
        "events":{ 1: "RIGHT_TRIGGER_DOWN", 0: "RIGHT_TRIGGER_UP" }
      },
      5: {
        "name": "RIGHT_TRIGGER_ANALOG",
        "type": "ANALOG",
        "range": {"top": 255, "bottom": 0},
        "events":{ 
          "value": "RIGHT_TRIGGER_UPDATE",
          "threshold": {
            1: "RIGHT_TRIGGER_DOWN",
            0: "RIGHT_TRIGGER_UP"
          }
        },
        "config": { "averageCount": 1, "threshold": 0.2}
      },
      312: {
        "name": "LEFT_TRIGGER",
        "type": "BUTTON",
        "events":{ 1: "LEFT_TRIGGER_DOWN", 0: "LEFT_TRIGGER_UP" }
      },
      2: {
        "name": "LEFT_TRIGGER_ANALOG",
        "type": "ANALOG",
        "range": {"top": 255, "bottom": 0},
        "events":{ 
          "value": "LEFT_TRIGGER_UPDATE",
          "threshold": {
            1: "LEFT_TRIGGER_DOWN",
            0: "LEFT_TRIGGER_UP"
          }
        },
        "config": { "averageCount": 1, "threshold": 0.2}
      },

      # OPTIONS
      315: {
        "name": "RIGHT_OPTION",
        "type": "BUTTON",
        "events":{ 1: "RIGHT_OPTION_DOWN", 0: "RIGHT_OPTION_UP" }
      },
      314: {
        "name": "LEFT_OPTION",
        "type": "BUTTON",
        "events":{ 1: "LEFT_OPTION_DOWN", 0: "LEFT_OPTION_UP" }
      },

      # DPAD
      16: {
        "name": "DPAD_X",
        "type": "PAD",
        "events":{ 1: "DPAD_RIGHT", 0: "DPAD_X_OFF", -1: "DPAD_LEFT"}
      },
      17: {
        "name": "DPAD_Y",
        "type": "PAD",
        "events":{ 1: "DPAD_DOWN", 0: "DPAD_Y_OFF", -1: "DPAD_UP"}
      },

      316: {
        "name": "START_BUTTON",
        "type": "BUTTON",
        "events":{ 1: "START_BUTTON_DOWN", 0: "START_BUTTON_UP"}
      },


      # ANALOG STICKS
      317: {
        "name": "LEFT_STICK_BUTTON",
        "type": "BUTTON",
        "events":{ 1: "LEFT_STICK_BUTTON_DOWN", 0: "LEFT_STICK_BUTTON_UP"}
      },
      0: {
        "name": "LEFT_STICK_X",
        "type": "ANALOG",
        "range": {"top": 0, "bottom": 255},
        "events":{ 
          "value": "LEFT_STICK_X_UPDATE", 
          "threshold": { 
            -1: "LEFT_STICK_RIGHT",
            0: "LEFT_STICK_X_OFF",
            1: "LEFT_STICK_LEFT"
          }
        },
        "config": { 
          "averageCount": 1, 
          "centeredThreshold": 0.6,
          "ignoreValues": [0] 
        }
      },
      1: {
        "name": "LEFT_STICK_Y",
        "type": "ANALOG",
        "range": {"top": 0, "bottom": 255},
        "events":{ 
          "value": "LEFT_STICK_Y_UPDATE", 
          "threshold": { 
            1: "LEFT_STICK_UP",
            0: "LEFT_STICK_Y_OFF",
            -1: "LEFT_STICK_DOWN"
          }
        },
        "config": { 
          "averageCount": 1, 
          "centeredThreshold": 0.6,
          "ignoreValues": [0] 
        }
      },
      318: {
        "name": "RIGHT_STICK_BUTTON",
        "type": "BUTTON",
        "events":{ 1: "RIGHT_STICK_BUTTON_DOWN", 0: "RIGHT_STICK_BUTTON_UP"}
      },
      3: {
        "name": "RIGHT_STICK_X",
        "type": "ANALOG",
        "range": {"top": 0, "bottom": 255},
        "events":{ 
          "value": "RIGHT_STICK_X_UPDATE", 
          "threshold": { 
            -1: "RIGHT_STICK_RIGHT",
            0: "RIGHT_STICK_X_OFF",
            1: "RIGHT_STICK_LEFT"
          }
        },
        "config": { 
          "averageCount": 1, 
          "centeredThreshold": 0.6,
          "ignoreValues": [0] 
        }
      },
      4: {
        "name": "RIGHT_STICK_Y",
        "type": "ANALOG",
        "range": {"top": 0, "bottom": 255},
        "events":{ 
          "value": "RIGHT_STICK_Y_UPDATE", 
          "threshold": { 
            1: "RIGHT_STICK_UP",
            0: "RIGHT_STICK_Y_OFF",
            -1: "RIGHT_STICK_DOWN"
          }
        },
        "config": { 
          "averageCount": 1, 
          "centeredThreshold": 0.6,
          "ignoreValues": [0] 
        }
      }

    },
    "motion": {
      # GYROSCOPE
      2: {
        "name": "GYRO_PITCH",
        "type": "ANALOG",
        "range": {"top": -8050, "bottom": 8050},
        "events":{ 
          "value": "GYRO_PITCH_UPDATE",
          "threshold": { 
            1: "GYRO_PITCH_UP",
            0: "GYRO_PITCH_OFF",
            -1: "GYRO_PITCH_DOWN"
          }
        },
        "config": { 
          "averageCount": 1, 
          "centeredThreshold": 0.6,
          "ignoreValues": [0] 
        }
      },
      0: {
        "name": "GYRO_ROLL",
        "type": "ANALOG",
        "range": {"top": -8050, "bottom": 8050},
        "events":{ 
          "value": "GYRO_ROLL_UPDATE", 
          "threshold": {
            1: "GYRO_ROLL_RIGHT",
            0: "GYRO_ROLL_OFF",
            -1: "GYRO_ROLL_LEFT"
          }
        },
        "config": { 
          "averageCount": 1, 
          "centeredThreshold": 0.6,
          "ignoreValues": [0] 
        }
      },
    },
    "touch": {
      #TOUCH PAD 
      272: {
        "name": "TOUCHPAD_BUTTON",
        "type": "BUTTON",
        "events":{ 1: "TOUCHPAD_BUTTON_DOWN", 0: "TOUCHPAD_BUTTON_UP" }
      },
      325: {
        "name": "TOUCHPAD_TOUCH",
        "type": "BUTTON",
        "events":{ 1: "TOUCHPAD_TOUCH_DOWN", 0: "TOUCHPAD_TOUCH_UP" }
      },

      0: {
        "name": "TOUCHPAD_X",
        "type": "ANALOG",
        "range": {"top": 1919, "bottom": 0},
        "events":{ 
          "value": "TOUCHPAD_X_UPDATE"
        },
        "config": { 
          "averageCount": 1,
          "ignoreValues": [0]
        }
      },
      1: {
        "name": "TOUCHPAD_Y",
        "type": "ANALOG",
        "range": {"top": 0, "bottom": 1500},
        "events":{ 
          "value": "TOUCHPAD_Y_UPDATE"
        },
        "config": { "averageCount": 1}
      }
    }
  }
}