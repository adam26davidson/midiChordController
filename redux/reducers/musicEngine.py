from pyrsistent import freeze
from constants import SPREAD_STEPS_PER_OCTAVE


def reducer(state, action):
    if state is None:
        return freeze({
            'availableMidiPorts': [],
            'connectedMidiPort': '',
            'bassChannel': 0,
            'chordChannel': 0,
            'distributeChannels': False,
            'velocity': 100,
            'velocityMode': 'random',
            'velocityDeviation': 10,
            'aftertouchMode': 'channel',

            'settingsList': [],
            'setting': 0,
            'settingLoading': False,
            'key': 0,
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
            'setting': 0,
            'chordOctave': 0,
            'voiceCount': 0,
            'modulation': {'side': 'none', 'scale': []},
            'secondary': 'none',
            'bassNote': 0,
            'bassShadow': 0,
            'chordNotes': [],
            'chordType': {'chord': [], 'root': 0},
            'chordShadow': []
        })

    if action['type'] == 'me/settingsListChanged':
        return state.set('settingsList', action['data']['settingsList'])

    elif action['type'] == 'me/settingChanged':
        return state.set('setting', action['data']['setting'])

    elif action['type'] == 'me/settingLoadingChanged':
        return state.set('settingLoading', action['data']['settingLoading'])

    if action['type'] == 'me/keyChanged':
        return state.set('key', action['data']['key'])

    if action['type'] == 'me/scaleChanged':
        return state.set('scale', action['data']['scale'])

    elif action['type'] == 'me/spreadChanged':
        return state.set('spread', action['data']['spread'])

    elif action['type'] == 'me/inversionChanged':
        return state.set('inversion', action['data']['inversion'])

    elif action['type'] == 'me/inversionModeChanged':
        return state.set('inversionMode', action['data']['inversionMode'])

    elif action['type'] == 'me/inversionRangeChanged':
        return state.set('inversionRange', action['data']['inversionRange'])

    elif action['type'] == 'me/bassPositionChanged':
        return state.set('bassPosition', action['data']['bassPosition'])

    elif action['type'] == 'me/bassModeChanged':
        return state.set('bassMode', action['data']['bassMode'])

    elif action['type'] == 'me/bassRangeChanged':
        return state.set('bassRange', action['data']['bassRange'])

    elif action['type'] == 'me/chordOctaveChanged':
        return state.set('chordOctave', action['data']['chordOctave'])

    elif action['type'] == 'me/voiceCountChanged':
        return state.set('voiceCount', action['data']['voiceCount'])

    elif action['type'] == 'me/modulationChanged':
        return state.set('modulation', action['data']['modulation'])

    elif action['type'] == 'me/secondaryChanged':
        return state.set('secondary', action['data']['secondary'])

    elif action['type'] == 'me/bassPlayed':
        return state.set('bassNote', action['data']['bassNote'])

    elif action['type'] == 'me/bassStopped':
        return state.set('bassNote', None)

    elif action['type'] == 'me/bassShadowChanged':
        return state.set('bassShadow', action['data']['bassShadow'])

    elif action['type'] == 'me/chordPlayed':
        return state.set('chordNotes', action['data']['chordNotes'])

    elif action['type'] == 'me/chordStopped':
        return state.set('chordNotes', [])

    elif action['type'] == 'me/chordTypeChanged':
        return state.set('chordType', action['data']['chordType'])

    elif action['type'] == 'me/chordShadowChanged':
        return state.set('chordShadow', action['data']['chordShadow'])

    elif action['type'] == 'me/chordChannelChanged':
        return state.set('chordChannel', action['data']['chordChannel'])

    elif action['type'] == 'me/bassChannelChanged':
        return state.set('bassChannel', action['data']['bassChannel'])

    elif action['type'] == 'me/distributeChannelsChanged':
        return state.set('distributeChannels', action['data']['distributeChannels'])

    elif action['type'] == 'me/velocityChanged':
        return state.set('velocity', action['data']['velocity'])

    elif action['type'] == 'me/velocityModeChanged':
        return state.set('velocityMode', action['data']['velocityMode'])

    elif action['type'] == 'me/velocityDeviationChanged':
        return state.set('velocityDeviation', action['data']['velocityDeviation'])
    
    elif action['type'] == 'me/aftertouchModeChanged':
        return state.set('aftertouchMode', action['data']['aftertouchMode'])

    elif action['type'] == 'me/holdChanged':
        return state.set('hold', action['data']['hold'])

    elif action['type'] == 'me/inversionLockChanged':
        return state.set('inversionLock', action['data']['inversionLock'])

    else:
        return state
