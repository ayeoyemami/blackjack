import csv
import random

from Game import Game
from RLAgents import QLearningAgent, SARSAAgent


def reset_agent(agent):
    if isinstance(agent, SARSAAgent):
        agent.next_state = None
        agent.next_action = None


def train_agent(agent, episodes, schedule):
    agent.training = True
    history = []

    for i in range(episodes):
        if schedule == "fixed":
            agent.epsilon = 0.1
        else:
            agent.epsilon = max(0.05, 0.3 * (0.9995 ** i))

        reset_agent(agent)
        Game(agent, lambda message: None).run()

        # Evaluate the agent every 1000 episodes
        if (i + 1) % 1000 == 0:
            random_state = random.getstate()

            wins, losses, draws = evaluate_agent(agent, 1000)

            random.setstate(random_state)

            win_rate = wins / 1000 * 100
            history.append((i + 1, win_rate))

            print(f"Episode {i + 1}: {win_rate:.2f}%")

            # Resume training after evaluation
            agent.training = True

    return history


def evaluate_agent(agent, episodes):
    agent.training = False
    agent.epsilon = 0

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

    return wins, losses, draws


def run_experiments():
    training_episodes = 10000
    evaluation_episodes = 5000
    seeds = [42, 123, 456]

    results = []
    learning_results = []

    for name, agent_class in [
        ("Q-learning", QLearningAgent),
        ("SARSA", SARSAAgent)
    ]:
        for schedule in ["fixed", "decay"]:
            for seed in seeds:
                random.seed(seed)
                agent = agent_class()

                print(f"\nTraining {name} | {schedule} | seed {seed}")

                history = train_agent(
                    agent, training_episodes, schedule
                )

                for episode, win_rate in history:
                    learning_results.append([
                        name, schedule, seed, episode, win_rate
                    ])

                wins, losses, draws = evaluate_agent(
                    agent, evaluation_episodes
                )

                win_rate = wins / evaluation_episodes * 100
                average_reward = (wins - losses) / evaluation_episodes

                results.append([
                    name, schedule, seed,
                    wins, losses, draws,
                    win_rate, average_reward
                ])

                print(
                    f"{name} | {schedule} | seed {seed} | "
                    f"Final win rate: {win_rate:.2f}%"
                )

    # saving final evaluation results
    with open("experiment_results.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "algorithm", "schedule", "seed",
            "wins", "losses", "draws",
            "win_rate", "average_reward"
        ])
        writer.writerows(results)

    # saving learning curve results
    with open("learning_curves.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "algorithm", "schedule", "seed",
            "episode", "win_rate"
        ])
        writer.writerows(learning_results)

    print("\nExperiments completed!")
    print("Results saved to experiment_results.csv")
    print("Learning curves saved to learning_curves.csv")


if __name__ == "__main__":
    run_experiments()
