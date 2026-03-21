import json
from pathlib import Path

from pyrsistent import thaw

from constants import PARENT_PATH
from redux import store
from redux.actions import music_engine as actions


class SettingsStorageUtility:

    loading_settings = True

    settings_file_directory = f'{PARENT_PATH}/userSettings.json'

    saved_music_engine_settings = {
        'bassChannel': actions.change_bass_channel,
        'chordChannel': actions.change_chord_channel,
        'distributeChannels': actions.change_distribute_channels,
        'velocity': actions.change_velocity,
        'velocityMode': actions.change_velocity_mode,
        'velocityDeviation': actions.change_velocity_deviation,
        'aftertouchMode': actions.change_aftertouch_mode,
        'strumMode': actions.change_strum_mode,
        'strumInterval': actions.change_strum_interval,
        'strumOrder': actions.change_strum_order,

        'inversionRange': actions.change_inversion_range,
        'bassRange': actions.change_bass_range,
        'transposeIncrement': actions.change_transpose_increment,

        'key': actions.change_key,
        'spread': actions.change_spread,
        'voiceCount': actions.change_voice_count,
        'chordOctave': actions.change_chord_octave
    }

    def load_settings(self):
        self.loading_settings = True
        settings_file_path = Path(self.settings_file_directory)

        if ( not settings_file_path.is_file()):
            return

        with open(self.settings_file_directory) as f:
            settings_from_file = json.load(f)

        for setting in self.saved_music_engine_settings:
            if setting in settings_from_file:
                print(f'loading {setting} = {settings_from_file[setting]}')
                store.dispatch(self.saved_music_engine_settings[setting](settings_from_file[setting]))

        self.loading_settings = False

    def save_settings(self):
        if not self.loading_settings:
            settings_to_save = {}

            state = store.get_state()
            me_state = thaw(state['musicEngine'])
            for setting in self.saved_music_engine_settings:
                settings_to_save[setting] = me_state[setting]

            with open(self.settings_file_directory, "w") as outfile:
                json.dump(settings_to_save, outfile)


settings_storage_utility = SettingsStorageUtility()
