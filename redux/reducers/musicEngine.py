from pyrsistent import freeze, thaw, m, pmap, v, pvector

def reducer(state, action):
  if state is None:
    return m()

  if action == 'me/settingListChanged':
    return state.set('settingsList', v(action['data']['settingsList']))

  if action == 'me/keyChanged':
    return state.set('key', action['data']['key'])

  if action == 'me/scaleChanged':
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

  elif action == 'me/settingChanged':
    return state.set('setting', action['data']['setting'])

  elif action == 'me/octaveChanged':
    return state.set('octave', action['data']['octave'])

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
  