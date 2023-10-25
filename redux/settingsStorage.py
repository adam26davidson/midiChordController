from pathlib import Path
from constants import PARENT_PATH
from redux.actions import musicEngine as actions
from pyrsistent import thaw
from redux import store
import json

class SettingsStorageUtility():

    loadingSettings = True

    settingsFileDirectory = f'{PARENT_PATH}/userSettings.json'

    savedMusicEngineSettings = {
        'bassChannel': actions.changeBassChannel,
        'chordChannel': actions.changeChordChannel,
        'distributeChannels': actions.changeDistributeChannels,
        'velocity': actions.changeVelocity,
        'velocityMode': actions.changeVelocityMode,
        'velocityDeviation': actions.changeVelocityDeviation,
        'aftertouchMode': actions.changeAftertouchMode,
        'strumMode': actions.changeStrumMode,
        'strumInterval': actions.changeStrumInterval,
        'strumOrder': actions.changeStrumOrder,
        
        'inversionRange': actions.changeInversionRange,
        'bassRange': actions.changeBassRange,
        'transposeIncrement': actions.changeTransposeIncrement,

        'key': actions.changeKey,
        'spread': actions.changeSpread,
        'voiceCount': actions.changeVoiceCount,
        'chordOctave': actions.changeChordOctave
    }
    
    def loadSettings(self):
        self.loadingSettings = True
        settingsFilePath = Path(self.settingsFileDirectory)

        if ( not settingsFilePath.is_file()):
            return None

        settingsFromFile = json.load(open(self.settingsFileDirectory))

        for setting in self.savedMusicEngineSettings.keys():
            if setting in settingsFromFile.keys():
                print(f'loading {setting} = {settingsFromFile[setting]}')
                store.dispatch(self.savedMusicEngineSettings[setting](settingsFromFile[setting]))
        
        self.loadingSettings = False

    def saveSettings(self):
        if not self.loadingSettings:
            settingsToSave = {}

            state = store.get_state()
            meState = thaw(state['musicEngine'])
            for setting in self.savedMusicEngineSettings.keys():
                settingsToSave[setting] = meState[setting]

            with open(self.settingsFileDirectory, "w") as outfile:
                json.dump(settingsToSave, outfile)


settingsStorageUtility = SettingsStorageUtility()