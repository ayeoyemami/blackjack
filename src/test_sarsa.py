from Game import Game
from RLAgents import SARSAAgent

# create the SARSA agent
agent = SARSAAgent()

# train the agent for 1000 games
for i in range(1000):
    agent.next_state = None
    agent.next_action = None

    game = Game(agent, lambda message: None)
    game.run()

print("Training completed!")
print("States and actions learned:", len(agent.q_table))

# test one game without exploration
agent.epsilon = 0

agent.next_state = None
agent.next_action = None

print("\nTesting one game:")
game = Game(agent, print)
game.run()
