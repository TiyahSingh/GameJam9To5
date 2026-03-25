import sys

import pygame

from game.app import GameApp


def main() -> int:
    pygame.init()
    try:
        app = GameApp()
        return app.run()
    finally:
        pygame.quit()


if __name__ == "__main__":
    raise SystemExit(main())

