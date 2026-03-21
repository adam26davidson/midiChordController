import json
from pathlib import Path

from pyrsistent import thaw

from constants import PARENT_PATH
from redux import store
from redux.actions import musicEngine as actions


class SettingsStorageUtility:

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
            return

        with open(self.settingsFileDirectory) as f:
            settingsFromFile = json.load(f)

        for setting in self.savedMusicEngineSettings:
            if setting in settingsFromFile:
                print(f'loading {setting} = {settingsFromFile[setting]}')
                store.dispatch(self.savedMusicEngineSettings[setting](settingsFromFile[setting]))

        self.loadingSettings = False

    def saveSettings(self):
        if not self.loadingSettings:
            settingsToSave = {}

            state = store.get_state()
            meState = thaw(state['musicEngine'])
            for setting in self.savedMusicEngineSettings:
                settingsToSave[setting] = meState[setting]

            with open(self.settingsFileDirectory, "w") as outfile:
                json.dump(settingsToSave, outfile)


settingsStorageUtility = SettingsStorageUtility()
