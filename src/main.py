# main.py

import Controller
import GameState
from Agents import PlayerAgent, RandomAgent

agent = PlayerAgent()
# agent = RandomAgent()
game_state = GameState.GameState()
controller = Controller.Controller(game_state, agent)

controller.start_game()
