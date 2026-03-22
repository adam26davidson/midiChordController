from __future__ import annotations

import argparse

from app import App


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Parse arguments')
    parser.add_argument("--display", dest="display", action="store_true")
    parser.add_argument("--no-display", dest="display", action="store_false")
    parser.set_defaults(display=True)
    return parser.parse_args()


if __name__ == "__main__":

    args = parse_arguments()
    app = App(args)
    app.start()
