from controllerManager import ControllerManager
from display import Display
from redux import store
import asyncio
import argparse

def parse_arguments():
  parser = argparse.ArgumentParser(description='Parse arguments')
  parser.add_argument("--display", dest="display", action="store_true")
  parser.add_argument("--no-display", dest="display", action="store_false")
  parser.set_defaults(display=True)
  return parser.parse_args()

if __name__ == "__main__":

  # args = parse_arguments()
  # display = Display() if args.display else None

  from test.controllerManagerTest import controllerManagerTest
  controllerManagerTest()

  asyncio.get_event_loop().run_forever()