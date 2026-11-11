# main.py

from Game import Game
from Agents import PlayerAgent, RandomAgent, PlayerLoggerAgent

while True:
    print("---NEW GAME---")
    Game(PlayerLoggerAgent(), print).run()
