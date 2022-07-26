from .default import default
from .gyroInversions import gyroInversions
from .touchpadBass import touchpadBass

meMaps = {
  default['name']: default,
  gyroInversions['name']: gyroInversions,
  touchpadBass['name']: touchpadBass
}
