from __future__ import annotations

from typing import Any

from redux.types import ReduxAction


def change_settings_list(list: list[str]) -> ReduxAction:
  return{
    'type': 'me/settingsListChanged',
    'data': {'settingsList': list}
  }

def change_setting(setting: int) -> ReduxAction:
  return{
    'type': 'me/settingChanged',
    'data': {'setting': setting}
  }

def change_setting_loading(is_loading: bool) -> ReduxAction:
  return {
    'type': 'me/settingLoadingChanged',
    'data': {'settingLoading': is_loading}
  }

def change_key(key: int) -> ReduxAction:
  return{
    'type': 'me/keyChanged',
    'data': {'key': key}
  }

def change_scale(scale: list[int]) -> ReduxAction:
  return{
    'type': 'me/scaleChanged',
    'data': {'scale': scale}
  }

def change_spread(spread: int) -> ReduxAction:
  return{
    'type': 'me/spreadChanged',
    'data': {'spread': spread}
  }

def change_inversion(inversion: int) -> ReduxAction:
  return{
    'type': 'me/inversionChanged',
    'data': {'inversion': inversion}
  }

def change_inversion_mode(inversion_mode: str) -> ReduxAction:
  return{
    'type': 'me/inversionModeChanged',
    'data': {'inversionMode': inversion_mode}
  }

def change_inversion_range(inversion_range: int) -> ReduxAction:
  return{
    'type': 'me/inversionRangeChanged',
    'data': {'inversionRange': inversion_range}
  }

def change_bass_position(bass_position: int) -> ReduxAction:
  return{
    'type': 'me/bassPositionChanged',
    'data': {'bassPosition': bass_position}
  }

def change_bass_mode(bass_mode: str) -> ReduxAction:
  return{
    'type': 'me/bassModeChanged',
    'data': {'bassMode': bass_mode}
  }

def change_bass_range(bass_range: int) -> ReduxAction:
  return{
    'type': 'me/bassRangeChanged',
    'data': {'bassRange': bass_range}
  }

def change_chord_octave(octave: int) -> ReduxAction:
  return{
    'type': 'me/chordOctaveChanged',
    'data': {'chordOctave': octave}
  }

def change_voice_count(voice_count: int) -> ReduxAction:
  return{
    'type': 'me/voiceCountChanged',
    'data': {'voiceCount': voice_count}
  }

def change_modulation(modulation: dict[str, Any]) -> ReduxAction:
  return{
    'type': 'me/modulationChanged',
    'data': {'modulation': modulation}
  }

def change_secondary(secondary: str) -> ReduxAction:
  return{
    'type': 'me/secondaryChanged',
    'data': {'secondary': secondary}
  }

def play_bass(bass_note: int) -> ReduxAction:
  return{
    'type': 'me/bassPlayed',
    'data': {'bassNote': bass_note}
  }

def stop_bass() -> ReduxAction:
  return{
    'type': 'me/bassStopped'
  }

def change_bass_shadow(bass_shadow: int) -> ReduxAction:
  return {
    'type': 'me/bassShadowChanged',
    'data': {'bassShadow': bass_shadow}
  }

def play_chord(chord_notes: list[int]) -> ReduxAction:
  return {
    'type': 'me/chordPlayed',
    'data': {'chordNotes': chord_notes}
  }

def stop_chord() -> ReduxAction:
  return{
    'type': 'me/chordStopped'
  }

def change_chord_type(chord_type: dict[str, Any]) -> ReduxAction:
  return {
    'type': 'me/chordTypeChanged',
    'data': {'chordType': chord_type}
  }

def change_chord_shadow(chord_shadow: list[int]) -> ReduxAction:
  return {
    'type': 'me/chordShadowChanged',
    'data': {'chordShadow': chord_shadow}
  }

def change_chord_channel(channel: int) -> ReduxAction:
  return {
    'type': 'me/chordChannelChanged',
    'data': {'chordChannel': channel}
  }

def change_bass_channel(channel: int) -> ReduxAction:
  return {
    'type': 'me/bassChannelChanged',
    'data': {'bassChannel': channel}
  }

def change_distribute_channels(distribute_channels: bool) -> ReduxAction:
  return {
    'type': 'me/distributeChannelsChanged',
    'data': {'distributeChannels': distribute_channels}
  }

def change_velocity(velocity: int | float) -> ReduxAction:
  return {
    'type': 'me/velocityChanged',
    'data': {'velocity': velocity}
  }

def change_velocity_mode(mode: str) -> ReduxAction:
  return {
    'type': 'me/velocityModeChanged',
    'data': {'velocityMode': mode}
  }

def change_velocity_deviation(deviation: int | float) -> ReduxAction:
  return {
    'type': 'me/velocityDeviationChanged',
    'data': {'velocityDeviation': deviation}
  }

def change_aftertouch_mode(aftertouch_mode: str) -> ReduxAction:
  return {
    'type': 'me/aftertouchModeChanged',
    'data': {'aftertouchMode': aftertouch_mode}
  }

def change_hold(hold: bool) -> ReduxAction:
  return {
    'type': 'me/holdChanged',
    'data': {'hold': hold}
  }

def change_inversion_lock(lock: bool) -> ReduxAction:
  return {
    'type': 'me/inversionLockChanged',
    'data': {'inversionLock': lock}
  }

def change_strum_mode(mode: str) -> ReduxAction:
  return {
    'type': 'me/strumModeChanged',
    'data': {'strumMode': mode}
  }

def change_strum_interval(interval: float) -> ReduxAction:
  return {
    'type': 'me/strumIntervalChanged',
    'data': {'strumInterval': interval}
  }

def change_strum_order(order: str) -> ReduxAction:
  return {
    'type': 'me/strumOrderChanged',
    'data': {'strumOrder': order}
  }

def change_transpose_increment(increment: int) -> ReduxAction:
  return {
    'type': 'me/transposeIncrementChanged',
    'data': {'transposeIncrement': increment}
  }

def change_chord_engine_control(control: str) -> ReduxAction:
    return {
        'type': 'me/chordEngineControlChanged',
        'data': {'chordEngineControl': control}
    }
