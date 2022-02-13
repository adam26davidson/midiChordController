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

  if action == 'me/settingsListChanged':
    return state.set('settingsList', v(action['data']['settingsList']))

  elif action == 'me/settingChanged':
    return state.set('setting', action['data']['setting'])

  elif action == 'me/settingLoadingChanged':
    return state.set('settingLoading', action['data']['settingLoading'])

  if action == 'me/keyChanged':
    return state.set('key', action['data']['key'])

  if action == 'me/scaleChanged':
    print('scale change dispatched')
    return state.set('scale', action['data']['scale'])

  elif action == 'me/spreadChanged':
    return state.set('spread', action['data']['spread'])

  elif action == 'me/inversionChanged':
    return state.set('inversion', action['data']['inversion'])
  
  elif action == 'me/inversionModeChanged':
    return state.set('inversionMode', action['data']['inversionMode'])

  elif action == 'me/inversionRangeChanged':
    return state.set('inversionRange', action['data']['inversionRange'])

  elif action == 'me/bassPositionChanged':
    return state.set('bassPosition', action['data']['bassPosition'])

  elif action == 'me/bassModeChanged':
    return state.set('bassMode', action['data']['bassMode'])

  elif action == 'me/bassRangeChanged':
    return state.set('bassRange', action['data']['bassRange'])

  elif action == 'me/chordOctaveChanged':
    return state.set('chordOctave', action['data']['chordOctave'])

  elif action == 'me/voiceCountChanged':
    return state.set('voiceCount', action['data']['voiceCount'])

  elif action == 'me/modulationChanged':
    return state.set('modulation', action['data']['modulation'])

  elif action == 'me/secondaryChanged':
    return state.set('secondary', action['data']['secondary'])

  elif action == 'me/bassPlayed':
    return state.set('bassNote', action['data']['bass'])

  elif action == 'me/bassStopped':
    return state.set('bassNote', None)

  elif action == 'me/bassShadowChanged':
    return state.set('bassShadow', action['data']['bassShadow'])

  elif action == 'me/chordPlayed':
    return state.set('chordNotes', v(action['data']['chordNotes']))

  elif action == 'me/chordStopped':
    return state.set('chordNotes', v())

  elif action == 'me/chordTypeChanged':
    return state.set('chordType', action['data']['chordType'])

  elif action == 'me/chordShadowChanged':
    return state.set('chordShadow', v(action['data']['chordShadow']))

  elif action == 'me/chordChannelChanged':
    return state.set('chordChannel', action['data']['chordChannel'])

  elif action == 'me/bassChannelChanged':
    return state.set('bassChannel', action['data']['bassChannel'])

  elif action == 'me/distributeChannelsChanged':
    return state.set('distributeChannels', action['data']['distributeChannels'])
  
  elif action == 'me/noteVelocityChanged':
    return state.set('distributeChannels', action['data']['distributeChannels'])

  elif action == 'me/holdChanged':
    return state.set('hold', action['data']['hold'])

  elif action == 'me/inversionLockChanged':
    return state.set('inversionLock', action['data']['inversionLock'])
    
  else: return state
  