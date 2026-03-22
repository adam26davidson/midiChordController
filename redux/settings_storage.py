from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING

logger = logging.getLogger(__name__)

from constants import PARENT_PATH
from redux import get_music_engine_state, store
from redux.actions import music_engine as actions
from redux.types import ReduxAction

if TYPE_CHECKING:
    from collections.abc import Callable


class SettingsStorageUtility:

    loading_settings: bool = True

    settings_file_directory: str = f'{PARENT_PATH}/userSettings.json'

    saved_music_engine_settings: dict[str, Callable[..., ReduxAction]] = {
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

    def load_settings(self) -> None:
        self.loading_settings = True
        settings_file_path = Path(self.settings_file_directory)

        if not settings_file_path.is_file():
            self.loading_settings = False
            return

        try:
            with open(self.settings_file_directory) as f:
                settings_from_file = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            logger.warning("Failed to load settings from %s: %s", self.settings_file_directory, e)
            self.loading_settings = False
            return

        for setting in self.saved_music_engine_settings:
            if setting in settings_from_file:
                logger.info("Loading %s = %s", setting, settings_from_file[setting])
                store.dispatch(self.saved_music_engine_settings[setting](settings_from_file[setting]))

        self.loading_settings = False

    def save_settings(self) -> None:
        if not self.loading_settings:
            settings_to_save = {}

            me_state = get_music_engine_state()
            for setting in self.saved_music_engine_settings:
                settings_to_save[setting] = me_state[setting]  # type: ignore[literal-required]

            tmp_path = self.settings_file_directory + ".tmp"
            try:
                with open(tmp_path, "w") as outfile:
                    json.dump(settings_to_save, outfile)
                Path(tmp_path).replace(self.settings_file_directory)
            except OSError as e:
                logger.error("Failed to save settings to %s: %s", self.settings_file_directory, e)


settings_storage_utility = SettingsStorageUtility()
