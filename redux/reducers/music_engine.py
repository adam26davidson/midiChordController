from __future__ import annotations

from typing import TYPE_CHECKING

from pyrsistent import freeze

from constants import SPREAD_STEPS_PER_OCTAVE
from redux.types import ReduxAction

if TYPE_CHECKING:
    from pyrsistent.typing import PMap


def reducer(state: PMap[str, object] | None, action: ReduxAction) -> PMap[str, object]:
    if state is None:
        return freeze({
            'chordEngineControl': 'internal',

            'availableMidiPorts': [],
            'connectedMidiPort': '',
            'bassChannel': 0,
            'chordChannel': 0,
            'distributeChannels': False,
            'velocity': 100,
            'velocityMode': 'random',
            'velocityDeviation': 10,
            'aftertouchMode': 'poly',

            'strumMode': 'regular', # 'random', 'regular', 'off'
            'strumInterval': 0.02, # time beween notes or spread of distribution
            'strumOrder' : 'random', # 'up', 'down', or 'random'

            'settingsList': [],
            'setting': 0,
            'settingLoading': False,
            'key': 0,
            'transposeIncrement': 1,
            'scale': [],
            'spread': SPREAD_STEPS_PER_OCTAVE,
            'inversion': 0,
            'inversionMode': 'continuous',  # incremental or continuous
            'inversionRange': 0,
            'inversionLock': False,
            'hold': False,
            'bassPosition': 0,
            'bassMode': 'incremental',
            'bassRange': 0,
            'chordOctave': 0,
            'voiceCount': 0,
            'modulation': {'side': 'none', 'scale': []},
            'secondary': 'none',
            'bassNote': 0,
            'bassShadow': 0,
            'chordNotes': [],
            'chordType': {'chord': [], 'root': 0},
            'chordShadow': [],
        })

    if action['type'] == 'me/settingsListChanged':
        return state.set('settingsList', action['data']['settingsList'])

    if action['type'] == 'me/settingChanged':
        return state.set('setting', action['data']['setting'])

    if action['type'] == 'me/settingLoadingChanged':
        return state.set('settingLoading', action['data']['settingLoading'])

    if action['type'] == 'me/keyChanged':
        return state.set('key', action['data']['key'])

    if action['type'] == 'me/scaleChanged':
        return state.set('scale', action['data']['scale'])

    if action['type'] == 'me/spreadChanged':
        return state.set('spread', action['data']['spread'])

    if action['type'] == 'me/inversionChanged':
        return state.set('inversion', action['data']['inversion'])

    if action['type'] == 'me/inversionModeChanged':
        return state.set('inversionMode', action['data']['inversionMode'])

    if action['type'] == 'me/inversionRangeChanged':
        return state.set('inversionRange', action['data']['inversionRange'])

    if action['type'] == 'me/bassPositionChanged':
        return state.set('bassPosition', action['data']['bassPosition'])

    if action['type'] == 'me/bassModeChanged':
        return state.set('bassMode', action['data']['bassMode'])

    if action['type'] == 'me/bassRangeChanged':
        return state.set('bassRange', action['data']['bassRange'])

    if action['type'] == 'me/chordOctaveChanged':
        return state.set('chordOctave', action['data']['chordOctave'])

    if action['type'] == 'me/voiceCountChanged':
        return state.set('voiceCount', action['data']['voiceCount'])

    if action['type'] == 'me/modulationChanged':
        return state.set('modulation', action['data']['modulation'])

    if action['type'] == 'me/secondaryChanged':
        return state.set('secondary', action['data']['secondary'])

    if action['type'] == 'me/bassPlayed':
        return state.set('bassNote', action['data']['bassNote'])

    if action['type'] == 'me/bassStopped':
        return state.set('bassNote', None)

    if action['type'] == 'me/bassShadowChanged':
        return state.set('bassShadow', action['data']['bassShadow'])

    if action['type'] == 'me/chordPlayed':
        return state.set('chordNotes', action['data']['chordNotes'])

    if action['type'] == 'me/chordStopped':
        return state.set('chordNotes', [])

    if action['type'] == 'me/chordTypeChanged':
        return state.set('chordType', action['data']['chordType'])

    if action['type'] == 'me/chordShadowChanged':
        return state.set('chordShadow', action['data']['chordShadow'])

    if action['type'] == 'me/chordChannelChanged':
        return state.set('chordChannel', action['data']['chordChannel'])

    if action['type'] == 'me/bassChannelChanged':
        return state.set('bassChannel', action['data']['bassChannel'])

    if action['type'] == 'me/distributeChannelsChanged':
        return state.set('distributeChannels', action['data']['distributeChannels'])

    if action['type'] == 'me/velocityChanged':
        return state.set('velocity', action['data']['velocity'])

    if action['type'] == 'me/velocityModeChanged':
        return state.set('velocityMode', action['data']['velocityMode'])

    if action['type'] == 'me/velocityDeviationChanged':
        return state.set('velocityDeviation', action['data']['velocityDeviation'])

    if action['type'] == 'me/aftertouchModeChanged':
        return state.set('aftertouchMode', action['data']['aftertouchMode'])

    if action['type'] == 'me/holdChanged':
        return state.set('hold', action['data']['hold'])

    if action['type'] == 'me/inversionLockChanged':
        return state.set('inversionLock', action['data']['inversionLock'])

    if action['type'] == 'me/strumModeChanged':
        return state.set('strumMode', action['data']['strumMode'])

    if action['type'] == 'me/strumIntervalChanged':
        return state.set('strumInterval', action['data']['strumInterval'])

    if action['type'] == 'me/strumOrderChanged':
        return state.set('strumOrder', action['data']['strumOrder'])

    if action['type'] == 'me/transposeIncrementChanged':
        return state.set('transposeIncrement', action['data']['transposeIncrement'])

    if action['type'] == 'me/chordEngineControlChanged':
        return state.set('chordEngineControl', action['data']['chordEngineControl'])

    return state
