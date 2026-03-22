"""Tests for SettingsStorageUtility file I/O."""

import json

from redux import store
from redux.settings_storage import SettingsStorageUtility


class TestSettingsStorageLoad:
    def test_load_missing_file_does_not_crash(self, tmp_path):
        ssu = SettingsStorageUtility()
        ssu.settings_file_directory = str(tmp_path / "nonexistent.json")
        ssu.load_settings()  # Should not raise

    def test_load_applies_settings_to_store(self, tmp_path):
        settings = {"key": 5, "velocity": 80, "spread": 12}
        settings_file = tmp_path / "settings.json"
        settings_file.write_text(json.dumps(settings))

        ssu = SettingsStorageUtility()
        ssu.settings_file_directory = str(settings_file)
        ssu.load_settings()

        from pyrsistent import thaw
        state = thaw(store.get_state()["musicEngine"])
        assert state["key"] == 5
        assert state["velocity"] == 80
        assert state["spread"] == 12

    def test_load_ignores_unknown_keys(self, tmp_path):
        settings = {"unknownKey": "whatever", "key": 3}
        settings_file = tmp_path / "settings.json"
        settings_file.write_text(json.dumps(settings))

        ssu = SettingsStorageUtility()
        ssu.settings_file_directory = str(settings_file)
        ssu.load_settings()  # Should not raise


class TestSettingsStorageSave:
    def test_save_writes_valid_json(self, tmp_path):
        settings_file = tmp_path / "settings.json"

        ssu = SettingsStorageUtility()
        ssu.settings_file_directory = str(settings_file)
        ssu.loading_settings = False
        ssu.save_settings()

        data = json.loads(settings_file.read_text())
        assert "key" in data
        assert "velocity" in data
        assert "spread" in data

    def test_save_skipped_while_loading(self, tmp_path):
        settings_file = tmp_path / "settings.json"

        ssu = SettingsStorageUtility()
        ssu.settings_file_directory = str(settings_file)
        ssu.loading_settings = True
        ssu.save_settings()

        assert not settings_file.exists()

    def test_save_roundtrip(self, tmp_path):
        settings_file = tmp_path / "settings.json"

        ssu = SettingsStorageUtility()
        ssu.settings_file_directory = str(settings_file)
        ssu.loading_settings = False
        ssu.save_settings()

        data1 = json.loads(settings_file.read_text())

        # Reset store to initial state, then load saved settings back
        import pydux

        import redux
        fresh = pydux.create_store(redux.reducer)
        redux.store.update(fresh)  # type: ignore[unresolved-attribute]

        ssu2 = SettingsStorageUtility()
        ssu2.settings_file_directory = str(settings_file)
        ssu2.load_settings()

        # Save again and compare
        ssu2.loading_settings = False
        ssu2.save_settings()
        data2 = json.loads(settings_file.read_text())

        assert data1 == data2
