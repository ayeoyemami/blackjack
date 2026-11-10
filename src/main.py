# main.py

import Controller
import GameState
from Agents import PlayerAgent, RandomAgent, PlayerObserver

agent = PlayerObserver()
# agent = RandomAgent()
game_state = GameState.GameState()
controller = Controller.Controller(game_state, agent)

outcome = controller.run()
print(outcome)
