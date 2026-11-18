import random
from Agents import Agent

class QLearningAgent(Agent):
    def __init__(self, alpha=0.1, gamma=0.9, epsilon=0.1):
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.training = True

        self.q_table = {}
        self.actions = ["hit", "stand"]
    
    def get_action(self, state):
        # explore: choose a random action
        if random.random() < self.epsilon:
            return random.choice(self.actions)

        # exploit: choose the action with the highest Q-value
        hit_value = self.q_table.get((state, "hit"), 0)
        stand_value = self.q_table.get((state, "stand"), 0)

        if hit_value > stand_value:
            return "hit"
        elif stand_value > hit_value:
            return "stand"
        else:
            return random.choice(self.actions)

    def observe(self, state, action, reward, next_state, done):
        if not self.training:
            return

        current_q = self.q_table.get((state, action), 0)

        if done:
            target = reward
        else:
            next_q = max(
                self.q_table.get((next_state, a), 0)
                for a in self.actions
            )
            target = reward + self.gamma * next_q

        new_q = current_q + self.alpha * (target - current_q)

        self.q_table[(state, action)] = new_q



class SARSAAgent(QLearningAgent):
    def __init__(self, alpha=0.1, gamma=0.9, epsilon=0.1):
        super().__init__(alpha, gamma, epsilon)
        self.next_action = None
        self.next_state = None

    def get_action(self, state):
        if self.next_state == state and self.next_action is not None:
            action = self.next_action
        else:
            action = super().get_action(state)

        self.next_state = None
        self.next_action = None

        return action

    def observe(self, state, action, reward, next_state, done):
        if not self.training:
            return

        current_q = self.q_table.get((state, action), 0)

        if done:
            target = reward
            self.next_state = None
            self.next_action = None
        else:
            next_action = super().get_action(next_state)

            next_q = self.q_table.get((next_state, next_action), 0)
            target = reward + self.gamma * next_q

            self.next_state = next_state
            self.next_action = next_action

        new_q = current_q + self.alpha * (target - current_q)

        self.q_table[(state, action)] = new_q
        