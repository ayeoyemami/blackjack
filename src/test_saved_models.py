import pickle
from pathlib import Path

from Game import Game


def test_model(filename):
    path = Path("models") / filename

    with open(path, "rb") as file:
        agent = pickle.load(file)

    agent.training = False
    agent.epsilon = 0

    print(f"\nTesting {filename}")
    print(f"Learned Q-table entries: {len(agent.q_table)}")

    reward = Game(agent, print).run()

    if reward == 1:
        print("Result: WIN")
    elif reward == -1:
        print("Result: LOSS")
    else:
        print("Result: DRAW")


test_model("q_learning.pkl")
test_model("sarsa.pkl")
