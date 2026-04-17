import pygame
import torch
import threading
import time
from env import Env
from DQN_Agent import DQN_Agent
from ReplayBuffer import ReplayBuffer

clock = pygame.time.Clock()
FPS = 60

# Global flag to terminate the game loop
terminate_game = False

def listen_for_input():
    global terminate_game
    while not terminate_game:
        user_input = input()  # Wait for user input
        if user_input.lower() == 'q':
            terminate_game = True
            print("\nTerminating game...")

def main():
    '''
    The main game loop
    '''
    
    global terminate_game
    
    # RUN VARIABLES
    run = 0
    win = 0
    balance = 10000
    env = Env(balance=balance)
    env.start()

    best_score = 0
    # if torch.cuda.is_available():
    #     device = torch.device('cuda')
    # else:
    #     device = torch.device('cpu')

    player = DQN_Agent()
    player_hat = DQN_Agent()
    player_hat.DQN = player.DQN.copy()
    batch_size = 128
    buffer = ReplayBuffer(path=None)
    learning_rate = 0.001
    epochs = 200000
    start_epoch = 0
    C, tau = 3, 0.001
    loss = torch.tensor(0)
    avg = 0
    scores, losses, avg_score = [], [], []
    optim = torch.optim.Adam(player.DQN.parameters(), lr=learning_rate)
    scheduler = torch.optim.lr_scheduler.MultiStepLR(optim, [5000 * 1000, 10000 * 1000, 15000 * 1000, 20000 * 1000, 25000 * 1000, 30000 * 1000], gamma=0.5)
    step = 0

    # Start the user input listener thread
    input_thread = threading.Thread(target=listen_for_input, daemon=True)
    input_thread.start()

    # LOOP
    for epoch in range(start_epoch, epochs):
        if terminate_game:
            print("Game terminated by user.")
            break  # Exit the main loop if "quit" was entered

        action = player.get_Action(env.state.get_state(), epoch)
        # Simulate action in environment
        env.move(action, G=None)
        optim.step()

        # Optional rendering and other features (commented out for now)
        # graphics.render_screen(env)
        # pygame.display.update()
        # clock.tick(FPS)

        # Check if the game ended (if needed) and display a picture if the game is over
        has_split = env.state.second_hand_active
        if env.checkend:
            print(env.state)
            d_cards = env.d_hand_vals
            check_end_status = env.CheckEnd()
            print(check_end_status)
            if check_end_status != 0:
                print(d_cards)
            if check_end_status in [1, 4, 5, 6, 8]:
                win += 1
                if check_end_status == 1 and has_split:
                    win += 1

    print(f"win: {win}\nwin rate: {win / (epoch-1)}\nend balance: {env.state.balance}")

# Run the main game loop
if __name__ == '__main__':
    main()