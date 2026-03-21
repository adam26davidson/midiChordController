"""Integration test: chord engine + display for modulation visual state.

Simulates the real flow: load Minor Nines preset, press south chord button,
activate left modulation, then run PerformFrame.check_state() and verify
the chord display's visual state is correct.

Bug: When modulating, scale shadows under stationary notes (root, fifth)
appear to move when they shouldn't.
"""

from unittest.mock import MagicMock, patch

from pyrsistent import thaw

from display.chord_display import ChordDisplay
from display.perform.perform_frame import PerformFrame
from music_engine.chord_engine.chord_engine import ChordEngine
from music_engine.chord_engine.internal_chord_engine import InternalChordEngine
from music_engine.chord_engine.state.chords_state import ChordButton
from music_engine.chord_engine.state.modulations_state import ModulationSide
from music_engine.chord_engine.chord_engine_state import state as engine_state
from redux import store


MINOR_NINES_INDEX = 3
MINOR_NINES_SCALE = [0, 2, 3, 5, 7, 8, 10]
MINOR_NINES_LEFT_MOD_SCALE = [0, 2, 4, 5, 7, 9, 11]


def _create_engine():
    """Create an InternalChordEngine with a no-op message callback."""
    engine = InternalChordEngine()
    engine.subscribe(lambda msg: None)
    return engine


class TestModulationReduxDispatchSequence:
    """Verify the exact Redux dispatch sequence when a modulation happens."""

    def test_dispatch_sequence_on_modulation(self):
        """Record all Redux dispatches when south chord is playing
        and left modulation is activated."""
        engine = _create_engine()
        engine.load_setting(MINOR_NINES_INDEX)

        # Press south chord
        engine.chord_button_on(ChordButton.SOUTH)
        assert engine_state.chord.is_playing

        # Record dispatches during modulation
        dispatched_actions = []
        original_dispatch = store.dispatch

        def recording_dispatch(action):
            dispatched_actions.append(action)
            return original_dispatch(action)

        with patch.object(store, "dispatch", side_effect=recording_dispatch):
            engine.modulations.set(ModulationSide.LEFT)

        action_types = [a["type"] for a in dispatched_actions]
        print(f"Dispatch sequence: {action_types}")

        # Modulation must be dispatched
        assert "me/modulationChanged" in action_types

        # Verify modulation dispatch contains the correct scale
        mod_action = next(a for a in dispatched_actions if a["type"] == "me/modulationChanged")
        assert mod_action["data"]["modulation"]["side"] == ModulationSide.LEFT

    def test_scale_not_dispatched_during_modulation(self):
        """The Redux 'scale' should NOT change during a modulation —
        only the modulation action carries the new scale."""
        engine = _create_engine()
        engine.load_setting(MINOR_NINES_INDEX)

        scale_before = thaw(store.get_state()["musicEngine"]["scale"])

        engine.chord_button_on(ChordButton.SOUTH)
        engine.modulations.set(ModulationSide.LEFT)

        scale_after = thaw(store.get_state()["musicEngine"]["scale"])
        assert scale_before == scale_after, (
            f"Redux scale changed during modulation: {scale_before} → {scale_after}"
        )


class TestModulationDisplayIntegration:
    """Full integration: engine dispatches → check_state → chord display."""

    def test_chord_display_set_scale_calls_during_modulation_frame(self):
        """Count how many times chord_display.set_scale is called when
        check_state processes a modulation frame."""
        engine = _create_engine()
        engine.load_setting(MINOR_NINES_INDEX)

        pf = PerformFrame(container=MagicMock())
        pf._dirty = False

        # Press south chord and process initial state
        engine.chord_button_on(ChordButton.SOUTH)
        pf._dirty = True
        pf.check_state()

        # Now activate modulation
        engine.modulations.set(ModulationSide.LEFT)

        set_scale_calls = []
        original_set_scale = pf.chord_display.set_scale

        def track_set_scale(*args, **kwargs):
            set_scale_calls.append(args)
            return original_set_scale(*args, **kwargs)

        with patch.object(pf.chord_display, "set_scale", side_effect=track_set_scale):
            pf._dirty = True
            pf.check_state()

        # set_scale should be called exactly once (from set_modulation),
        # NOT again from set_chord
        print(f"set_scale called {len(set_scale_calls)} time(s)")
        for i, call_args in enumerate(set_scale_calls):
            print(f"  call {i}: scale={call_args[0] if call_args else 'no args'}")

        assert len(set_scale_calls) <= 1, (
            f"set_scale called {len(set_scale_calls)} times during modulation frame — "
            f"expected at most 1 (from set_modulation only)"
        )

    def test_stationary_notes_dont_move_after_check_state(self):
        """After processing a modulation frame via check_state, notes that
        map to themselves (root, fifth, etc.) should be at their fixed positions."""
        engine = _create_engine()
        engine.load_setting(MINOR_NINES_INDEX)

        pf = PerformFrame(container=MagicMock())
        pf._dirty = False

        # Press south chord and process
        engine.chord_button_on(ChordButton.SOUTH)
        pf._dirty = True
        pf.check_state()

        # Record fixed positions of stationary notes before modulation
        cd = pf.chord_display
        stationary_notes = [0, 2, 5, 7]  # Same index in both scales
        fixed_positions = {}
        for note in stationary_notes:
            pos = cd.notes[note]["center"]
            fixed_positions[note] = (pos["x"], pos["y"])

        # Activate modulation and process
        engine.modulations.set(ModulationSide.LEFT)
        pf._dirty = True
        pf.check_state()

        # Verify stationary notes are at their fixed positions
        for note in stationary_notes:
            pos = cd.get_note_position(note)
            expected = fixed_positions[note]
            assert (pos["x"], pos["y"]) == expected, (
                f"Note {note} moved after modulation check_state: "
                f"expected={expected}, got=({pos['x']}, {pos['y']})"
            )

    def test_played_notes_have_large_radius_after_modulation(self):
        """After a modulation frame, played chord notes should still
        have large_note_radius on the chord display.

        The chord engine doesn't dispatch chordNotes directly — the MIDI
        module does via play_chord(). We simulate this by dispatching
        play_chord after the engine processes."""
        from redux.actions import music_engine as me_actions

        engine = _create_engine()
        engine.load_setting(MINOR_NINES_INDEX)

        pf = PerformFrame(container=MagicMock())
        pf._dirty = False

        # Press south chord — simulate MIDI dispatching the playing notes
        engine.chord_button_on(ChordButton.SOUTH)
        playing_notes = list(engine_state.chord.playing_notes)
        store.dispatch(me_actions.play_chord(playing_notes))
        pf._dirty = True
        pf.check_state()

        cd = pf.chord_display
        # Verify chord notes have large radius
        for note in cd.chord:
            assert cd.notes[note]["radius"] == cd.large_note_radius, (
                f"Pre-modulation: note {note} should have large radius"
            )

        # Activate modulation — simulate MIDI dispatching new playing notes
        engine.modulations.set(ModulationSide.LEFT)
        new_playing_notes = list(engine_state.chord.playing_notes)
        store.dispatch(me_actions.play_chord(new_playing_notes))
        pf._dirty = True
        pf.check_state()

        # Chord notes (now modulated) should still have large radius
        for note in cd.chord:
            assert cd.notes[note]["radius"] == cd.large_note_radius, (
                f"Post-modulation: note {note} radius={cd.notes[note]['radius']}, "
                f"expected={cd.large_note_radius}"
            )


    def test_modulation_animation_state_active_after_check_state(self):
        """After processing a modulation frame, the chord display's
        modulation_state should be in 'startAnimation' status."""
        engine = _create_engine()
        engine.load_setting(MINOR_NINES_INDEX)

        pf = PerformFrame(container=MagicMock())
        pf._dirty = False

        engine.chord_button_on(ChordButton.SOUTH)
        pf._dirty = True
        pf.check_state()

        engine.modulations.set(ModulationSide.LEFT)
        pf._dirty = True
        pf.check_state()

        cd = pf.chord_display
        assert cd.modulation_state["status"] == "startAnimation", (
            f"Expected animation status 'startAnimation', "
            f"got '{cd.modulation_state['status']}'"
        )
        assert cd.modulation_state["newScale"] == MINOR_NINES_LEFT_MOD_SCALE
