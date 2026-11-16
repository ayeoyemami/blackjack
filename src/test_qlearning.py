from Game import Game
from RLAgents import QLearningAgent

# create our Q-learning agent
agent = QLearningAgent()

# train the agent by playing 1000 games
for i in range(1000):
    game = Game(agent, lambda message: None)
    game.run()

print("Training completed!")
print("States and actions learned:", len(agent.q_table))

# turn off exploration to test the learned strategy
agent.epsilon = 0

print("\nTesting one game:")
game = Game(agent, print)
game.run()
