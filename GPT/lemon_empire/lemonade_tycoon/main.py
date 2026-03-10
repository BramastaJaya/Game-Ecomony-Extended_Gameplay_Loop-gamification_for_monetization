#!/usr/bin/env python3
# main.py  —  Lemon Empire entry point

import os, sys
sys.path.insert(0, os.path.dirname(__file__))

import pygame
from core.game_loop import GameLoop


def main():
    game = GameLoop()
    game.run()


if __name__ == "__main__":
    main()
