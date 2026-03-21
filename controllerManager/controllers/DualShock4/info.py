from controllerManager.models.controllerConfig import ControllerConfig
from controllerManager.models.polarOrientation import PolarOrientation
from controllerManager.models.rawControl import RawControl
from controllerManager.models.rawControlConfig import RawControlConfig
from controllerManager.models.rawControlEvent import RawControlEvent as Event
from controllerManager.models.rawControlType import RawControlType as Type

controller_config = ControllerConfig(
    name="DualShock4",
    vendor=1356,
    product=2508,
    me_map="touchpadBass",
    ui_map="default",
    compatible_me_maps=['gyroInversions', 'default', 'touchpadBass'],
    controls={
        "main": [
            # MAIN BUTTONS
            RawControl(
                key="SOUTH_BUTTON",
                label="South Button",
                ev_dev_key=304,
                type=Type.BUTTON,
            ),
            RawControl(
                key="WEST_BUTTON",
                label="West Button",
                ev_dev_key=308,
                type=Type.BUTTON,
            ),
            RawControl(
                key="NORTH_BUTTON",
                label="North Button",
                ev_dev_key=307,
                type=Type.BUTTON,
            ),
            RawControl(
                key="EAST_BUTTON",
                label="East Button",
                ev_dev_key=305,
                type=Type.BUTTON,
            ),

            # BUMPERS
            RawControl(
                key="RIGHT_BUMPER",
                label="Right Bumper",
                ev_dev_key=311,
                type=Type.BUTTON,
            ),
            RawControl(
                key="LEFT_BUMPER",
                label="Left Bumper",
                ev_dev_key=310,
                type=Type.BUTTON,
            ),

            # TRIGGERS
            RawControl(
                key="RIGHT_TRIGGER",
                label="Right Trigger",
                ev_dev_key=313,
                type=Type.BUTTON,
            ),
            RawControl(
                key="RIGHT_TRIGGER_ANALOG",
                label="Right Trigger Analog",
                ev_dev_key=5,
                type=Type.ANALOG,
                config=RawControlConfig(
                    top_value=255,
                    bottom_value=0,
                    expose_on_off_events = False,
                    expose_polar_events = False,
                    average_count=1,
                    threshold=0.2,
                )
            ),
            RawControl(
                key="LEFT_TRIGGER",
                label="Left Trigger",
                ev_dev_key=312,
                type=Type.BUTTON,
            ),
            RawControl(
                key="LEFT_TRIGGER_ANALOG",
                label="Left Trigger Analog",
                ev_dev_key=2,
                type=Type.ANALOG,
                config=RawControlConfig(
                    top_value=255,
                    bottom_value=0,
                    expose_on_off_events = False,
                    expose_polar_events = False,
                    average_count=1,
                    threshold=0.2,
                )
            ),

            # OPTIONS
            RawControl(
                key="RIGHT_OPTION",
                label="Right Option",
                ev_dev_key=315,
                type=Type.BUTTON,
            ),
            RawControl(
                key="LEFT_OPTION",
                label="Left Option",
                ev_dev_key=314,
                type=Type.BUTTON,
            ),

            # DPAD
            RawControl(
                key="DPAD_X",
                label="DPad X",
                ev_dev_key=16,
                type=Type.PAD,
                config=RawControlConfig(
                    expose_on_off_events = True,
                    expose_polar_events = True,
                    polar_event_map={1: Event.RIGHT, 0: Event.OFF, -1: Event.LEFT},
                    polar_orientation=PolarOrientation.HORIZONTAL
                )
            ),
            RawControl(
                key="DPAD_Y",
                label="DPad Y",
                ev_dev_key=17,
                type=Type.PAD,
                config=RawControlConfig(
                    expose_on_off_events = True,
                    expose_polar_events = True,
                    polar_event_map={1: Event.DOWN, 0: Event.OFF, -1: Event.UP},
                    polar_orientation=PolarOrientation.VERTICAL
                )
            ),

            # START BUTTON
            RawControl(
                key="START_BUTTON",
                label="Start Button",
                ev_dev_key=316,
                type=Type.BUTTON,
            ),

            # ANALOG STICKS
            RawControl(
                key="LEFT_STICK_BUTTON",
                label="Left Stick Button",
                ev_dev_key=317,
                type=Type.BUTTON,
            ),
            RawControl(
                key="LEFT_STICK_X",
                label="Left Stick X",
                ev_dev_key=0,
                type=Type.ANALOG,
                config=RawControlConfig(
                    top_value=0,
                    bottom_value=255,
                    expose_on_off_events = True,
                    expose_polar_events = True,
                    average_count=1,
                    centered_threshold=0.6,
                    ignore_values=[0],
                    polar_event_map={-1: Event.RIGHT, 0: Event.OFF, 1: Event.LEFT},
                    polar_orientation=PolarOrientation.HORIZONTAL
                )
            ),
            RawControl(
                key="LEFT_STICK_Y",
                label="Left Stick Y",
                ev_dev_key=1,
                type=Type.ANALOG,
                config=RawControlConfig(
                    top_value=0,
                    bottom_value=255,
                    expose_on_off_events = True,
                    expose_polar_events = True,
                    average_count=1,
                    centered_threshold=0.6,
                    ignore_values=[0],
                    polar_event_map={1: Event.UP, 0: Event.OFF, -1: Event.DOWN},
                    polar_orientation=PolarOrientation.VERTICAL
                )
            ),
            RawControl(
                key="RIGHT_STICK_BUTTON",
                label="Right Stick Button",
                ev_dev_key=318,
                type=Type.BUTTON,
            ),
            RawControl(
                key="RIGHT_STICK_X",
                label="Right Stick X",
                ev_dev_key=3,
                type=Type.ANALOG,
                config=RawControlConfig(
                    top_value=0,
                    bottom_value=255,
                    expose_on_off_events = True,
                    expose_polar_events = True,
                    average_count=1,
                    centered_threshold=0.6,
                    ignore_values=[0],
                    polar_event_map={-1: Event.RIGHT, 0: Event.OFF, 1: Event.LEFT},
                    polar_orientation=PolarOrientation.HORIZONTAL
                )
            ),
            RawControl(
                key="RIGHT_STICK_Y",
                label="Right Stick Y",
                ev_dev_key=4,
                type=Type.ANALOG,
                config=RawControlConfig(
                    top_value=0,
                    bottom_value=255,
                    expose_on_off_events = True,
                    expose_polar_events = True,
                    average_count=1,
                    centered_threshold=0.6,
                    ignore_values=[0],
                    polar_event_map={1: Event.UP, 0: Event.OFF, -1: Event.DOWN},
                    polar_orientation=PolarOrientation.VERTICAL
                )
            )
        ],
        "motion": [
            # GYROSCOPE
            RawControl(
                key="GYRO_PITCH",
                label="Gyro Pitch",
                ev_dev_key=2,
                type=Type.ANALOG,
                config=RawControlConfig(
                    top_value=-8050,
                    bottom_value=8050,
                    expose_on_off_events = True,
                    expose_polar_events = True,
                    average_count=1,
                    centered_threshold=0.6,
                    ignore_values=[0],
                    polar_event_map={1: Event.UP, 0: Event.OFF, -1: Event.DOWN},
                    polar_orientation=PolarOrientation.VERTICAL
                )
            ),
            RawControl(
                key="GYRO_ROLL",
                label="Gyro Roll",
                ev_dev_key=0,
                type=Type.ANALOG,
                config=RawControlConfig(
                    top_value=-8050,
                    bottom_value=8050,
                    expose_on_off_events = True,
                    expose_polar_events = True,
                    average_count=1,
                    centered_threshold=0.6,
                    ignore_values=[0],
                    polar_event_map={1: Event.RIGHT, 0: Event.OFF, -1: Event.LEFT},
                    polar_orientation=PolarOrientation.HORIZONTAL
                )
            )
        ],
        "touch": [
            # TOUCH PAD
            RawControl(
                key="TOUCHPAD_BUTTON",
                label="Touchpad Button",
                ev_dev_key=272,
                type=Type.BUTTON,
            ),
            RawControl(
                key="TOUCHPAD_TOUCH",
                label="Touchpad Touch",
                ev_dev_key=325,
                type=Type.BUTTON,
            ),
            RawControl(
                key="TOUCHPAD_X",
                label="Touchpad X",
                ev_dev_key=0,
                type=Type.ANALOG,
                config=RawControlConfig(
                    top_value=1900,
                    bottom_value=0,
                    expose_on_off_events = False,
                    expose_polar_events = False,
                    average_count=1,
                    ignore_values=[0]
                )
            ),
            RawControl(
                key="TOUCHPAD_Y",
                label="Touchpad Y",
                ev_dev_key=1,
                type=Type.ANALOG,
                config=RawControlConfig(
                    top_value=0,
                    bottom_value=900,
                    expose_on_off_events = False,
                    expose_polar_events = False,
                    average_count=1
                )
            )
        ]
    }
)

info = {
    "key": "DualShock4",
    "vendor": 1356,
    "product": 2508,
    "meMap": "touchpadBass",
    'uiMap': 'default',
    "compatibleMeMaps": ['gyroInversions', 'default', 'touchpadBass'],
    "controls": {
        "main": {
            # MAIN BUTTONS
            304: {
                "key": "SOUTH_BUTTON",
                "type": Type.BUTTON,
                "events": {1: Event.ON, 0: Event.OFF}
            },
            308: {
                "key": "WEST_BUTTON",
                "type": Type.BUTTON,
                "events": {1: Event.ON, 0: Event.OFF}
            },
            307: {
                "key": "NORTH_BUTTON",
                "type": Type.BUTTON,
                "events": {1: Event.ON, 0: Event.OFF}
            },
            305: {
                "key": "EAST_BUTTON",
                "type": Type.BUTTON,
                "events": {1: Event.ON, 0: Event.OFF}
            },

            # BUMPERS
            311: {
                "key": "RIGHT_BUMPER",
                "type": Type.BUTTON,
                "events": {1: Event.ON, 0: Event.OFF}
            },
            310: {
                "key": "LEFT_BUMPER",
                "type": Type.BUTTON,
                "events": {1: Event.ON, 0: Event.OFF}
            },

            # TRIGGERS
            313: {
                "key": "RIGHT_TRIGGER",
                "type": Type.BUTTON,
                "events": {1: Event.ON, 0: Event.OFF}
            },
            5: {
                "key": "RIGHT_TRIGGER_ANALOG",
                "type": Type.ANALOG,
                "range": {"top": 255, "bottom": 0},
                "events": {
                    "value": Event.UPDATE,
                    "threshold": {
                        1: Event.DOWN,
                        0: Event.OFF
                    }
                },
                "config": {"averageCount": 1, "threshold": 0.2}
            },
            312: {
                "key": "LEFT_TRIGGER",
                "type": Type.BUTTON,
                "events": {1: Event.ON, 0: Event.OFF}
            },
            2: {
                "key": "LEFT_TRIGGER_ANALOG",
                "type": Type.ANALOG,
                "range": {"top": 255, "bottom": 0},
                "events": {
                    "value": Event.UPDATE,
                    "threshold": {
                        1: Event.DOWN,
                        0: Event.OFF
                    }
                },
                "config": {"averageCount": 1, "threshold": 0.2}
            },

            # OPTIONS
            315: {
                "key": "RIGHT_OPTION",
                "type": Type.BUTTON,
                "events": {1: Event.ON, 0: Event.OFF}
            },
            314: {
                "key": "LEFT_OPTION",
                "type": Type.BUTTON,
                "events": {1: Event.ON, 0: Event.OFF}
            },

            # DPAD
            16: {
                "key": "DPAD_X",
                "type": Type.PAD,
                "events": {1: Event.RIGHT, 0: Event.OFF, -1: Event.LEFT}
            },
            17: {
                "key": "DPAD_Y",
                "type": Type.PAD,
                "events": {1: Event.DOWN, 0: Event.OFF, -1: Event.UP}
            },

            # START BUTTON
            316: {
                "key": "START_BUTTON",
                "type": Type.BUTTON,
                "events": {1: Event.ON, 0: Event.OFF}
            },


            # ANALOG STICKS
            317: {
                "key": "LEFT_STICK_BUTTON",
                "type": Type.BUTTON,
                "events": {1: Event.ON, 0: Event.OFF}
            },
            0: {
                "key": "LEFT_STICK_X",
                "type": Type.ANALOG,
                "range": {"top": 0, "bottom": 255},
                "events": {
                    "value": Event.UPDATE,
                    "threshold": {
                        -1: Event.RIGHT,
                        0: Event.OFF,
                        1: Event.LEFT
                    }
                },
                "config": {
                    "averageCount": 1,
                    "centeredThreshold": 0.6,
                    "ignoreValues": [0]
                }
            },
            1: {
                "key": "LEFT_STICK_Y",
                "type": Type.ANALOG,
                "range": {"top": 0, "bottom": 255},
                "events": {
                    "value": Event.UPDATE,
                    "threshold": {
                        1: Event.UP,
                        0: Event.OFF,
                        -1: Event.DOWN
                    }
                },
                "config": {
                    "averageCount": 1,
                    "centeredThreshold": 0.6,
                    "ignoreValues": [0]
                }
            },
            318: {
                "key": "RIGHT_STICK_BUTTON",
                "type": Type.BUTTON,
                "events": {1: Event.ON, 0: Event.OFF}
            },
            3: {
                "key": "RIGHT_STICK_X",
                "type": Type.ANALOG,
                "range": {"top": 0, "bottom": 255},
                "events": {
                    "value": Event.UPDATE,
                    "threshold": {
                        -1: Event.RIGHT,
                        0: Event.OFF,
                        1: Event.LEFT
                    }
                },
                "config": {
                    "averageCount": 1,
                    "centeredThreshold": 0.6,
                    "ignoreValues": [0]
                }
            },
            4: {
                "key": "RIGHT_STICK_Y",
                "type": Type.ANALOG,
                "range": {"top": 0, "bottom": 255},
                "events": {
                    "value": Event.UPDATE,
                    "threshold": {
                        1: Event.UP,
                        0: Event.OFF,
                        -1: Event.DOWN
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
                "key": "GYRO_PITCH",
                "type": Type.ANALOG,
                "range": {"top": -8050, "bottom": 8050},
                "events": {
                    "value": Event.UPDATE,
                    "threshold": {
                        1: Event.UP,
                        0: Event.OFF,
                        -1: Event.DOWN
                    }
                },
                "config": {
                    "averageCount": 1,
                    "centeredThreshold": 0.6,
                    "ignoreValues": [0]
                }
            },
            0: {
                "key": "GYRO_ROLL",
                "type": Type.ANALOG,
                "range": {"top": -8050, "bottom": 8050},
                "events": {
                    "value": Event.UPDATE,
                    "threshold": {
                        1: Event.RIGHT,
                        0: Event.OFF,
                        -1: Event.LEFT
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
            # TOUCH PAD
            272: {
                "key": "TOUCHPAD_BUTTON",
                "type": Type.BUTTON,
                "events": {1: Event.ON, 0: Event.OFF}
            },
            325: {
                "key": "TOUCHPAD_TOUCH",
                "type": Type.BUTTON,
                "events": {1: Event.ON, 0: Event.OFF}
            },

            0: {
                "key": "TOUCHPAD_X",
                "type": Type.ANALOG,
                "range": {"top": 1900, "bottom": 0},
                "events": {
                    "value": Event.UPDATE
                },
                "config": {
                    "averageCount": 1,
                    "ignoreValues": [0]
                }
            },
            1: {
                "key": "TOUCHPAD_Y",
                "type": Type.ANALOG,
                "range": {"top": 0, "bottom": 900},
                "events": {
                    "value": Event.UPDATE
                },
                "config": {"averageCount": 1}
            }
        }
    }
}
