import csv
import random
import pickle
from pathlib import Path

from Game import Game
from RLAgents import QLearningAgent, SARSAAgent


# Checkpoints for measuring learning progress
CHECKPOINTS = [0, 10, 50, 100, 250, 500,
               1000, 2000, 3000, 5000, 7000, 10000]


def reset_agent(agent):
    if isinstance(agent, SARSAAgent):
        agent.next_state = None
        agent.next_action = None


def evaluate_agent(agent, episodes, seed=999):
    # Save current settings
    old_training = agent.training
    old_epsilon = agent.epsilon
    old_random_state = random.getstate()

    agent.training = False
    agent.epsilon = 0
    random.seed(seed)

    wins = 0
    losses = 0
    draws = 0

    for _ in range(episodes):
        reset_agent(agent)
        reward = Game(agent, lambda message: None).run()

        if reward == 1:
            wins += 1
        elif reward == -1:
            losses += 1
        else:
            draws += 1

    reset_agent(agent)

    # Restore training settings and randomness
    agent.training = old_training
    agent.epsilon = old_epsilon
    random.setstate(old_random_state)

    return {
        "win_rate": wins / episodes * 100,
        "loss_rate": losses / episodes * 100,
        "draw_rate": draws / episodes * 100,
        "average_reward": (wins - losses) / episodes
    }


def train_agent(agent, episodes, seed):
    agent.training = True
    agent.epsilon = 0.1

    history = []

    # Measure performance before any training
    metrics = evaluate_agent(agent, 5000, seed=999)

    history.append((0, metrics))
    print(f"Episode 0: {metrics['win_rate']:.2f}%")

    for i in range(1, episodes + 1):
        reset_agent(agent)
        Game(agent, lambda message: None).run()

        if i in CHECKPOINTS:
            metrics = evaluate_agent(
                agent, 5000, seed=999
            )

            history.append((i, metrics))

            print(
                f"Episode {i}: "
                f"Win {metrics['win_rate']:.2f}% | "
                f"Loss {metrics['loss_rate']:.2f}% | "
                f"Draw {metrics['draw_rate']:.2f}%"
            )

    return history



def save_model(agent, filename):
    models_folder = Path("models")
    models_folder.mkdir(exist_ok=True)

    agent.training = False
    agent.epsilon = 0
    reset_agent(agent)

    filepath = models_folder / filename

    with open(filepath, "wb") as file:
        pickle.dump(agent, file)

    print(f"Saved model: {filepath}")


def run_experiments():
    training_episodes = 10000
    seeds = [42, 123, 456]

    learning_results = []
    final_results = []

    for name, agent_class in [
        ("Q-learning", QLearningAgent),
        ("SARSA", SARSAAgent)
    ]:
        for seed in seeds:
            random.seed(seed)
            agent = agent_class()

            print(f"\nTraining {name} | seed {seed}")

            history = train_agent(
                agent, training_episodes, seed
            )

            if seed == 42:
                if name == "Q-learning":
                    save_model(agent, "q_learning.pkl")
                elif name == "SARSA":
                    save_model(agent, "sarsa.pkl")


            for episode, metrics in history:
                learning_results.append([
                    name,
                    seed,
                    episode,
                    metrics["win_rate"],
                    metrics["loss_rate"],
                    metrics["draw_rate"],
                    metrics["average_reward"]
                ])

            # Final evaluation
            final_metrics = evaluate_agent(
                agent, 5000, seed=999
            )

            final_results.append([
                name,
                seed,
                final_metrics["win_rate"],
                final_metrics["loss_rate"],
                final_metrics["draw_rate"],
                final_metrics["average_reward"]
            ])

    # Save learning curve data
    with open("learning_curves.csv", "w", newline="") as file:
        writer = csv.writer(file)

        writer.writerow([
            "algorithm",
            "seed",
            "episode",
            "win_rate",
            "loss_rate",
            "draw_rate",
            "average_reward"
        ])

        writer.writerows(learning_results)

    # Save final results
    with open("experiment_results.csv", "w", newline="") as file:
        writer = csv.writer(file)

        writer.writerow([
            "algorithm",
            "seed",
            "win_rate",
            "loss_rate",
            "draw_rate",
            "average_reward"
        ])

        writer.writerows(final_results)

    print("\nAll experiments completed!")
    print("Saved learning_curves.csv")
    print("Saved experiment_results.csv")


if __name__ == "__main__":
    run_experiments()
