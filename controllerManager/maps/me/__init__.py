from .default import default
from .gyroInversions import gyro_inversions
from .touchpadBass import touchpad_bass

me_maps = {
  default['name']: default,
  gyro_inversions['name']: gyro_inversions,
  touchpad_bass['name']: touchpad_bass
}
