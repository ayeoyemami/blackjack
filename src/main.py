# main.py

from Game import Game
from Agents import PlayerAgent, RandomAgent, PlayerLoggerAgent

Game(PlayerLoggerAgent()).run()
