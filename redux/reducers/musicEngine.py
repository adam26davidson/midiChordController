from pyrsistent import freeze, thaw, m, pmap, v, pvector

def reducer(state, action):
  if state is None:
    return freeze({
      'availableMidiPorts': [],
      'connectedMidiPort': '',

      'settingsList': [],
      'key': 0,
      'scale': [],
      'spread': 0,
      'inversion': 0,
      'inversionMode': 'incremental',
      'inversionRange': 0,
      'bassPosition': 0,
      'bassMode': 'incremental',
      'bassRange': 0,
      'setting': 0,
      'octave': 0,
      'voiceCount': 0,
      'modulation': 'none',
      'secondary': 'none',
      'bassNote': 0,
      'bassShadow': 0,
      'chordNotes': [],
      'chordType': {'notes': [], 'root': 0},
      'chordShadow': []
    })

  if action['type'] == 'me/settingsListChanged':
    return state.set('settingsList', v(action['data']['settingsList']))

  elif action['type'] == 'me/settingChanged':
    return state.set('setting', action['data']['setting'])

  elif action['type'] == 'me/settingLoadingChanged':
    return state.set('settingLoading', action['data']['settingLoading'])

  if action['type'] == 'me/keyChanged':
    return state.set('key', action['data']['key'])

  if action['type'] == 'me/scaleChanged':
    print('scale change dispatched')
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
    return state.set('bassNote', action['data']['bass'])

  elif action['type'] == 'me/bassStopped':
    return state.set('bassNote', None)

  elif action['type'] == 'me/bassShadowChanged':
    return state.set('bassShadow', action['data']['bassShadow'])

  elif action['type'] == 'me/chordPlayed':
    return state.set('chordNotes', v(action['data']['chordNotes']))

  elif action['type'] == 'me/chordStopped':
    return state.set('chordNotes', v())

  elif action['type'] == 'me/chordTypeChanged':
    return state.set('chordType', action['data']['chordType'])

  elif action['type'] == 'me/chordShadowChanged':
    return state.set('chordShadow', v(action['data']['chordShadow']))

  elif action['type'] == 'me/chordChannelChanged':
    return state.set('chordChannel', action['data']['chordChannel'])

  elif action['type'] == 'me/bassChannelChanged':
    return state.set('bassChannel', action['data']['bassChannel'])

  elif action['type'] == 'me/distributeChannelsChanged':
    return state.set('distributeChannels', action['data']['distributeChannels'])
  
  elif action['type'] == 'me/noteVelocityChanged':
    return state.set('distributeChannels', action['data']['distributeChannels'])

  elif action['type'] == 'me/holdChanged':
    return state.set('hold', action['data']['hold'])

  elif action['type'] == 'me/inversionLockChanged':
    return state.set('inversionLock', action['data']['inversionLock'])
    
  else: return state
  