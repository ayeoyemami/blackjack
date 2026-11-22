import csv
import random

from Game import Game
from Agents import RandomAgent
from RLAgents import QLearningAgent, SARSAAgent

EVALUATION_CHECKPOINTS = (1, 50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1500, 2000, 3000, 4000, 5000,)


def reset_agent(agent):
    if isinstance(agent, SARSAAgent):
        agent.next_state = None
        agent.next_action = None


def train_agent(agent, episodes):
    agent.training = True
    history = []

    for i in range(episodes):
        agent.epsilon = 0.1

        reset_agent(agent)
        Game(agent, lambda message: None).run()

        # Evaluate every 100 episodes through episode 1000, then every 1000.
        episode = i + 1
        if episode in EVALUATION_CHECKPOINTS:
            random_state = random.getstate()

            wins, _, _ = evaluate_agent(agent, 1000)

            random.setstate(random_state)

            win_rate = wins / 1000 * 100
            history.append((episode, win_rate))

            print(f"Episode {episode}: {win_rate:.2f}%")

            # Resume training after evaluation
            agent.training = True

    return history


def evaluate_random_baseline(agent, episodes):
    history = []

    for episode in EVALUATION_CHECKPOINTS:
        if episode > episodes:
            break

        wins, _, _ = evaluate_agent(agent, 1000)
        win_rate = wins / 1000 * 100
        history.append((episode, win_rate))

        print(f"Episode {episode}: {win_rate:.2f}%")

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
    training_episodes = 5000
    evaluation_episodes = 1000
    seeds = [42, 123, 456]

    results = []
    learning_results = []

    for name, agent_class, should_train in [
        ("Q-learning", QLearningAgent, True),
        ("SARSA", SARSAAgent, True),
        ("Random", RandomAgent, False),
    ]:
        for seed in seeds:
            random.seed(seed)
            agent = agent_class()

            action = "Training" if should_train else "Evaluating"
            print(f"\n{action} {name} | seed {seed}")

            if should_train:
                history = train_agent(agent, training_episodes)
            else:
                history = evaluate_random_baseline(agent, training_episodes)

            for episode, win_rate in history:
                learning_results.append([
                    name, seed, episode, win_rate
                ])

            wins, losses, draws = evaluate_agent(
                agent, evaluation_episodes
            )

            win_rate = wins / evaluation_episodes * 100
            average_reward = (wins - losses) / evaluation_episodes

            results.append([
                name, seed,
                wins, losses, draws,
                win_rate, average_reward
            ])

            print(
                f"{name} | seed {seed} | "
                f"Final win rate: {win_rate:.2f}%"
            )

    # saving final evaluation results
    with open("data/experiment_results.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "algorithm", "seed",
            "wins", "losses", "draws",
            "win_rate", "average_reward"
        ])
        writer.writerows(results)

    # saving learning curve results
    with open("data/learning_curves.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "algorithm", "seed",
            "episode", "win_rate"
        ])
        writer.writerows(learning_results)

    print("\nExperiments completed!")
    print("Results saved to data/experiment_results.csv")
    print("Learning curves saved to data/learning_curves.csv")


if __name__ == "__main__":
    run_experiments()
