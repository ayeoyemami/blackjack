# Agents.py

from Card import get_value

# parent class
class Agent:
    def get_action(self, state):
        raise NotImplementedError("subclass must implement this method. agent parent class should not be used")

    def observe(self, state, action, reward, next_state, done):
        raise NotImplementedError("subclass must implement this method. agent parent class should not be used")

# subclass for player agent
class PlayerAgent(Agent):
    def get_action(self, state):
        input_action = input("input: ").strip().lower()
        if input_action in ["hit", "stand"]:
            return input_action 

    def observe(self, state, action, reward, next_state, done):
        pass

# this class uses player input
# observe() records results to a file so we can compare our agents to our human gameplay
class PlayerObserver(Agent):
    def get_action(self, state):
        input_action = input("input: ").strip().lower()
        if input_action in ["hit", "stand"]:
            return input_action

    def observe(self, state, action, reward, next_state, done):
        with open("game_results.csv", "a") as f:
            f.write(f"{state['hand_sum']},{get_value(state['upcard'])},{action},{reward},{next_state['hand_sum']},{get_value(next_state['upcard'])},{done}\n")

# subclass for random agent
class RandomAgent(Agent):
    def get_action(self, state):
        import random
        return random.choice(["hit", "stand"])
