# main.py

import Game
from Agents import PlayerAgent, RandomAgent, PlayerObserver

agent = PlayerObserver()
game = Game.Game(agent)

outcome = game.run()
print(outcome)
