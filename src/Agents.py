# Agents.py

# parent class
class Agent:
    def get_action(self, hand_sum, dealer_card):
        raise NotImplementedError("subclass must implement this method. agent parent class should not be used")

    def observe(self, hand_sum, dealer_card, a):
        raise NotImplementedError("subclass must implement this method. agent parent class should not be used")

# subclass for player agent
class PlayerAgent(Agent):
    def get_action(self, hand_sum, dealer_card):
        input_action = input("input: ").strip().lower()
        if input_action in ["hit", "stand"]:
            return input_action

# subclass for random agent
class RandomAgent(Agent):
    def get_action(self, hand_sum, dealer_card):
        import random
        return random.choice(["hit", "stand"])
