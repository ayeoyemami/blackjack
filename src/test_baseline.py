import random

from Game import Game
from Agents import RandomAgent


def test_baseline(episodes=5000):
    agent = RandomAgent()

    wins = 0
    losses = 0
    draws = 0

    for _ in range(episodes):
        reward = Game(agent, lambda message: None).run()

        if reward == 1:
            wins += 1
        elif reward == -1:
            losses += 1
        else:
            draws += 1

    print("Random Agent Results:")
    print(f"Wins: {wins}")
    print(f"Losses: {losses}")
    print(f"Draws: {draws}")
    print(f"Win rate: {wins / episodes * 100:.2f}%")
    print(f"Average reward: {(wins - losses) / episodes:.3f}")


random.seed(42)
test_baseline()
