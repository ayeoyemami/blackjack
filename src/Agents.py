# Agents.py

import random
import State

# parent class
class Agent:
    def get_action(self, state):
        raise NotImplementedError("subclass must implement this method. agent parent class should not be used")

    def observe(self, state: State, action, reward, next_state: State, done):
        pass

# subclass for player agent
class PlayerAgent(Agent):
    def get_action(self, state):
        input_action = input("input: ").strip().lower()
        if input_action in ["hit", "stand"]:
            return input_action 

# this class uses player input
# observe() records results to a file so we can compare our agents to our human gameplay
class PlayerLoggerAgent(Agent):
    def get_action(self, state):
        input_action = input("input: ").strip().lower()
        if input_action in ["hit", "stand"]:
            return input_action

    def observe(self, state: State, action, reward, next_state: State, done):
        with open("game_results.csv", "a") as f:
            f.write(f"{state.hand_sum},{state.upcard_rank.name},{state.has_high_ace},{action},{reward},{next_state.hand_sum},{next_state.upcard_rank.name},{next_state.has_high_ace},{done}\n")

# subclass for random agent
class RandomAgent(Agent):
    def get_action(self, state):
        return random.choice(["hit", "stand"])
