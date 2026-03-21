from .default import default
from .gyro_inversions import gyro_inversions
from .touchpad_bass import touchpad_bass

me_maps = {
  default['name']: default,
  gyro_inversions['name']: gyro_inversions,
  touchpad_bass['name']: touchpad_bass
}
