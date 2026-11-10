# main.py

from Game import Game
from Agents import PlayerAgent, RandomAgent, PlayerObserver

Game(PlayerObserver()).run()
