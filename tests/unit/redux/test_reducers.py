"""Tests for Redux reducers — each is a pure (state, action) → state function."""

from pyrsistent import thaw

from redux.actions import controller_coupler as cc_actions
from redux.actions import music_engine as me_actions
from redux.reducers import controller_coupler as cc_reducer
from redux.reducers import controller_manager as cm_reducer
from redux.reducers import display as display_reducer
from redux.reducers import music_engine as me_reducer


class TestMusicEngineReducer:
    def _init_state(self):
        return me_reducer.reducer(None, {"type": "@@INIT"})

    def test_initial_state(self):
        state = self._init_state()
        s = thaw(state)
        assert s["key"] == 0
        assert s["velocity"] == 100
        assert s["hold"] is False
        assert s["chordEngineControl"] == "internal"

    def test_change_key(self):
        state = self._init_state()
        state = me_reducer.reducer(state, me_actions.change_key(5))
        assert thaw(state)["key"] == 5

    def test_change_scale(self):
        state = self._init_state()
        state = me_reducer.reducer(state, me_actions.change_scale([0, 2, 4, 5, 7, 9, 11]))
        assert thaw(state)["scale"] == [0, 2, 4, 5, 7, 9, 11]

    def test_change_spread(self):
        state = self._init_state()
        state = me_reducer.reducer(state, me_actions.change_spread(10))
        assert thaw(state)["spread"] == 10

    def test_change_inversion(self):
        state = self._init_state()
        state = me_reducer.reducer(state, me_actions.change_inversion(3))
        assert thaw(state)["inversion"] == 3

    def test_change_inversion_range(self):
        state = self._init_state()
        state = me_reducer.reducer(state, me_actions.change_inversion_range(8))
        assert thaw(state)["inversionRange"] == 8

    def test_change_bass_position(self):
        state = self._init_state()
        state = me_reducer.reducer(state, me_actions.change_bass_position(2))
        assert thaw(state)["bassPosition"] == 2

    def test_change_chord_octave(self):
        state = self._init_state()
        state = me_reducer.reducer(state, me_actions.change_chord_octave(-1))
        assert thaw(state)["chordOctave"] == -1

    def test_change_voice_count(self):
        state = self._init_state()
        state = me_reducer.reducer(state, me_actions.change_voice_count(6))
        assert thaw(state)["voiceCount"] == 6

    def test_change_hold(self):
        state = self._init_state()
        state = me_reducer.reducer(state, me_actions.change_hold(True))
        assert thaw(state)["hold"] is True

    def test_change_velocity(self):
        state = self._init_state()
        state = me_reducer.reducer(state, me_actions.change_velocity(80))
        assert thaw(state)["velocity"] == 80

    def test_change_velocity_mode(self):
        state = self._init_state()
        state = me_reducer.reducer(state, me_actions.change_velocity_mode("constant"))
        assert thaw(state)["velocityMode"] == "constant"

    def test_change_strum_mode(self):
        state = self._init_state()
        state = me_reducer.reducer(state, me_actions.change_strum_mode("random"))
        assert thaw(state)["strumMode"] == "random"

    def test_change_strum_interval(self):
        state = self._init_state()
        state = me_reducer.reducer(state, me_actions.change_strum_interval(0.05))
        assert thaw(state)["strumInterval"] == 0.05

    def test_change_strum_order(self):
        state = self._init_state()
        state = me_reducer.reducer(state, me_actions.change_strum_order("up"))
        assert thaw(state)["strumOrder"] == "up"

    def test_play_chord(self):
        state = self._init_state()
        state = me_reducer.reducer(state, me_actions.play_chord([60, 64, 67]))
        assert thaw(state)["chordNotes"] == [60, 64, 67]

    def test_stop_chord(self):
        state = self._init_state()
        state = me_reducer.reducer(state, me_actions.play_chord([60]))
        state = me_reducer.reducer(state, me_actions.stop_chord())
        assert thaw(state)["chordNotes"] == []

    def test_play_bass(self):
        state = self._init_state()
        state = me_reducer.reducer(state, me_actions.play_bass(36))
        assert thaw(state)["bassNote"] == 36

    def test_stop_bass(self):
        state = self._init_state()
        state = me_reducer.reducer(state, me_actions.play_bass(36))
        state = me_reducer.reducer(state, me_actions.stop_bass())
        assert thaw(state)["bassNote"] is None

    def test_change_chord_type(self):
        state = self._init_state()
        ct = {"chord": [0, 4, 7], "root": 0}
        state = me_reducer.reducer(state, me_actions.change_chord_type(ct))
        assert thaw(state)["chordType"] == ct

    def test_change_chord_channel(self):
        state = self._init_state()
        state = me_reducer.reducer(state, me_actions.change_chord_channel(3))
        assert thaw(state)["chordChannel"] == 3

    def test_change_bass_channel(self):
        state = self._init_state()
        state = me_reducer.reducer(state, me_actions.change_bass_channel(2))
        assert thaw(state)["bassChannel"] == 2

    def test_change_distribute_channels(self):
        state = self._init_state()
        state = me_reducer.reducer(state, me_actions.change_distribute_channels(True))
        assert thaw(state)["distributeChannels"] is True

    def test_change_transpose_increment(self):
        state = self._init_state()
        state = me_reducer.reducer(state, me_actions.change_transpose_increment(7))
        assert thaw(state)["transposeIncrement"] == 7

    def test_change_chord_engine_control(self):
        state = self._init_state()
        state = me_reducer.reducer(state, me_actions.change_chord_engine_control("external"))
        assert thaw(state)["chordEngineControl"] == "external"

    def test_change_setting(self):
        state = self._init_state()
        state = me_reducer.reducer(state, me_actions.change_setting(2))
        assert thaw(state)["setting"] == 2

    def test_unknown_action_returns_state_unchanged(self):
        state = self._init_state()
        new_state = me_reducer.reducer(state, {"type": "unknown/action"})
        assert state is new_state

    def test_change_inversion_lock(self):
        state = self._init_state()
        state = me_reducer.reducer(state, me_actions.change_inversion_lock(True))
        assert thaw(state)["inversionLock"] is True


class TestControllerCouplerReducer:
    def _init_state(self):
        return cc_reducer.reducer(None, {"type": "@@INIT"})

    def test_initial_state(self):
        state = self._init_state()
        s = thaw(state)
        assert s["activeControlMap"] is None
        assert s["appParameters"] == {}
        assert s["controls"] == {}

    def test_update_control_map(self):
        state = self._init_state()
        state = cc_reducer.reducer(state, cc_actions.update_control_map("test_map"))
        assert thaw(state)["activeControlMap"] == "test_map"

    def test_update_app_parameters(self):
        state = self._init_state()
        params = {"KEY_1": "param1", "KEY_2": "param2"}
        state = cc_reducer.reducer(state, cc_actions.update_app_parameters(params))
        assert thaw(state)["appParameters"] == params

    def test_update_controls(self):
        state = self._init_state()
        controls = {"ctrl1": {"key": "val"}}
        state = cc_reducer.reducer(state, cc_actions.update_controls(controls))
        assert thaw(state)["controls"] == controls

    def test_music_engine_parameters_loaded(self):
        state = self._init_state()
        state = cc_reducer.reducer(state, cc_actions.music_engine_app_parameters_loaded())
        assert thaw(state)["musicEngineAppParametersLoaded"] is True


class TestControllerManagerReducer:
    def _init_state(self):
        return cm_reducer.reducer(None, {"type": "@@INIT"})

    def test_initial_state(self):
        state = self._init_state()
        s = thaw(state)
        assert s["waitingForConnection"] is False
        assert s["controllers"] == []

    def test_add_controller(self):
        state = self._init_state()
        action = {
            "type": "controllerManager/controllerAdded",
            "data": {
                "id": "ctrl1",
                "name": "DualShock4",
                "role": "primary",
                "compatibleMeMaps": [],
                "meMap": {"map": {}},
                "uiMap": {"map": {}},
            },
        }
        state = cm_reducer.reducer(state, action)
        controllers = thaw(state["controllers"])
        assert len(controllers) == 1
        assert controllers[0]["id"] == "ctrl1"
        assert controllers[0]["name"] == "DualShock4"

    def test_remove_controller(self):
        state = self._init_state()
        add_action = {
            "type": "controllerManager/controllerAdded",
            "data": {
                "id": "ctrl1",
                "name": "DualShock4",
                "role": "primary",
                "compatibleMeMaps": [],
                "meMap": {"map": {}},
                "uiMap": {"map": {}},
            },
        }
        state = cm_reducer.reducer(state, add_action)
        remove_action = {
            "type": "controllerManager/controllerRemoved",
            "data": {"id": "ctrl1"},
        }
        state = cm_reducer.reducer(state, remove_action)
        assert len(thaw(state["controllers"])) == 0

    def test_remove_nonexistent_controller(self):
        state = self._init_state()
        action = {
            "type": "controllerManager/controllerRemoved",
            "data": {"id": "nonexistent"},
        }
        new_state = cm_reducer.reducer(state, action)
        assert new_state is state

    def test_started_waiting(self):
        state = self._init_state()
        action = {"type": "controllerManager/startedWaitingForConnection"}
        state = cm_reducer.reducer(state, action)
        assert thaw(state)["waitingForConnection"] is True

    def test_stopped_waiting(self):
        state = self._init_state()
        action = {"type": "controllerManager/startedWaitingForConnection"}
        state = cm_reducer.reducer(state, action)
        action = {"type": "controllerManager/stoppedWaitingForConnection"}
        state = cm_reducer.reducer(state, action)
        assert thaw(state)["waitingForConnection"] is False


class TestDisplayReducer:
    def _init_state(self):
        return display_reducer.reducer(None, {"type": "@@INIT"})

    def test_initial_state(self):
        state = self._init_state()
        assert thaw(state)["activeFrame"] == "PERFORM"

    def test_change_frame(self):
        state = self._init_state()
        action = {
            "type": "ui/activeFrameChanged",
            "data": {"activeFrame": "SETTINGS"},
        }
        state = display_reducer.reducer(state, action)
        assert thaw(state)["activeFrame"] == "SETTINGS"

    def test_unknown_action_unchanged(self):
        state = self._init_state()
        new_state = display_reducer.reducer(state, {"type": "unknown"})
        assert state is new_state
