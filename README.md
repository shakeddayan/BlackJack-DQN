# Blackjack AI: Dual-DQN Agent

A reinforcement learning project developed on Windows using Python and Pygame. This project implements an intelligent agent trained to master Blackjack through Deep Q-Learning (DQN), featuring a specialized architecture to handle complex decision-making.

## 🧠 Architecture: The Dual-Model Approach

Unlike standard implementations, this project utilizes two distinct Deep Q-Networks (DQN) that operate simultaneously to optimize the agent's strategy:

* **The Min Model:** Responsible for standard play and point-total optimization.
* **The Split Model:** A specialized network dedicated to analyzing "Split" opportunities, ensuring the agent understands when to deviate from standard play to maximize expected value. also helps maintain the simplicity in the Min Model, while making sure the model has full capability of making the decision of whether to split or not.

By decoupling these logic paths, the agent can achieve a higher degree of accuracy in its strategy grid, especially in edge cases where standard models often struggle.

## 🛠️ Tech Stack

* **Language:** Python 3.12.4
* **Deep Learning:** PyTorch (DQN Implementation)
* **GUI & Visualization:** Pygame
* **Experiment Tracking:** Weights & Biases (W&B)
* **Environment:** Windows 11

## ⚙️ Installation & Setup

1. **Clone the repository:**
```bash
git clone https://github.com/shakeddayan/BlackJack-DQN.git
cd Blackjack-DQN
```

2. **Install dependencies:**
It is recommended to use a virtual environment, but you can install the required libraries directly using:

```bash
pip install -r requirements.txt
```


3. **Run the project**:

```bash
python launcher.py
```

## 📁 Project Structure

* `checkpoints/`: Saved weights for the Min  networks.
* `checkpoints-split/`: Saved weights for the Split  networks.
* `fonts/`: fonts used in the GUI of the game. not all are used, but are there for customization possibilities.
* `img/`: High-quality SVG card assets and UI elements.
* `screenObjects/`: Pygame UI element classes i created to use in the graphical game interface.
* `strategies/`: A folder full of csv files, listing each model's playing strategy. Good for testing the models, and there is an excel file that can compare the strategy to an "ideal model".
* `.gitignore`: Configured to exclude system noise, `__pycache__`, and large log folders like `wandb`.

## ⚙️ How it Works

The agent observes the current game state - including the player's hand sum, whether or not the player's hand contains an ace(11/1) and the dealer's open card - and selects an action based on the combined policy of the Min and Split models. The rewards are calculated based on hand outcomes, reinforcing "Perfect Strategy" decisions over time.

---
*Developed as part of a deep dive into Reinforcement Learning and Computer Science.*