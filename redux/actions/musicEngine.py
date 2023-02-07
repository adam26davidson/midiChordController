
def changeSettingsList(list):
  return{
    'type': 'me/settingsListChanged',
    'data': {'settingsList': list}
  }

def changeSetting(setting):
  return{
    'type': 'me/settingChanged',
    'data': {'setting': setting}
  }

def changeSettingLoading(isLoading):
  return {
    'type': 'me/settingLoadingChanged',
    'data': {'settingLoading': isLoading}
  }

def changeKey(key):
  return{
    'type': 'me/keyChanged',
    'data': {'key': key}
  }

def changeScale(scale):
  return{
    'type': 'me/scaleChanged',
    'data': {'scale': scale}
  }

def changeSpread(spread):
  return{
    'type': 'me/spreadChanged',
    'data': {'spread': spread}
  }

def changeInversion(inversion):
  return{
    'type': 'me/inversionChanged',
    'data': {'inversion': inversion}
  }

def changeInversionMode(inversionMode):
  return{
    'type': 'me/inversionModeChanged',
    'data': {'inversionMode': inversionMode}
  }
  
def changeInversionRange(inversionRange):
  return{
    'type': 'me/inversionRangeChanged',
    'data': {'inversionRange': inversionRange}
  }

def changeBassPosition(bassPosition):
  return{
    'type': 'me/bassPositionChanged',
    'data': {'bassPosition': bassPosition}
  }

def changeBassMode(bassMode):
  return{
    'type': 'me/bassModeChanged',
    'data': {'bassMode': bassMode}
  }

def changeBassRange(bassRange):
  return{
    'type': 'me/bassRangeChanged',
    'data': {'bassRange': bassRange}
  }

def changeChordOctave(octave):
  return{
    'type': 'me/chordOctaveChanged',
    'data': {'chordOctave': octave}
  }

def changeVoiceCount(voiceCount):
  return{
    'type': 'me/voiceCountChanged',
    'data': {'voiceCount': voiceCount}
  }

def changeModulation(modulation):
  return{
    'type': 'me/modulationChanged',
    'data': {'modulation': modulation}
  }

def changeSecondary(secondary):
  return{
    'type': 'me/secondaryChanged',
    'data': {'secondary': secondary}
  }

def playBass(bassNote):
  return{
    'type': 'me/bassPlayed',
    'data': {'bassNote': bassNote}
  }

def stopBass():
  return{
    'type': 'me/bassStopped'
  }

def changeBassShadow(bassShadow):
  return {
    'type': 'me/bassShadowChanged',
    'data': {'bassShadow': bassShadow}
  }

def playChord(chordNotes):
  return {
    'type': 'me/chordPlayed',
    'data': {'chordNotes': chordNotes}
  }

def stopChord():
  return{
    'type': 'me/chordStopped'
  }

def changeChordType(chordType):
  return {
    'type': 'me/chordTypeChanged',
    'data': {'chordType': chordType}
  }

def changeChordShadow(chordShadow):
  return {
    'type': 'me/chordShadowChanged',
    'data': {'chordShadow': chordShadow}
  }

def changeChordChannel(channel):
  return {
    'type': 'me/chordChannelChanged',
    'data': {'chordChannel': channel}
  }
  
def changeBassChannel(channel):
  return {
    'type': 'me/bassChannelChanged',
    'data': {'bassChannel': channel}
  }

def changeDistributeChannels(distributeChannels):
  return {
    'type': 'me/distributeChannelsChanged',
    'data': {'distributeChannels': distributeChannels}
  }

def changeVelocity(velocity):
  return {
    'type': 'me/velocityChanged',
    'data': {'velocity': velocity}
  }

def changeVelocityMode(mode):
  return {
    'type': 'me/velocityModeChanged',
    'data': {'velocityMode': mode}
  }

def changeVelocityDeviation(deviation):
  return {
    'type': 'me/velocityDeviationChanged',
    'data': {'velocityDeviation': deviation}
  }

def changeAftertouchMode(aftertouchMode):
  return {
    'type': 'me/aftertouchModeChanged',
    'data': {'aftertouchMode': aftertouchMode}
  }

def changeHold(hold):
  return {
    'type': 'me/holdChanged',
    'data': {'hold': hold}
  }

def changeInversionLock(lock):
  return {
    'type': 'me/inversionLockChanged',
    'data': {'inversionLock': lock}
  }