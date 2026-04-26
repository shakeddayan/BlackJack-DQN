import torch
import threading
from env import Env
from DQN_Agent_min import DQN_Agent_min
from ReplayBuffer import ReplayBuffer
import winsound
import time
import wandb 

# Global flag to terminate the game loop
terminate_game = False

def listen_for_input():
    '''
    will be used to listen for user input during the training.
    on user entering 'q' then '\n' (enter) the game will terminate.
    '''
    global terminate_game
    while not terminate_game:
        user_input = input()  # Wait for user input
        if user_input.lower() == 'q':
            terminate_game = True
            print("\nTerminating game...")

def main():
    '''
    The main game loop - for the DQN agent.
    This is a non-graphic version of the game, used for training and diagnostics.
    '''
    
    global terminate_game 
    
    # --- WandB Configuration ---
    # Define hyperparameters for tracking
    RUN_NUM = 14
    RUN_NAME = f"BlackJack-min-run-{RUN_NUM}" #the run name
    RESUME_TRAINING = False #is resuming another already saved run?
    PATH_TO_LOAD = "checkpoints/BlackJack-min-run-9.pth" #path to load
    WANDB_RESUME_ID = "v19a50is"
    EPOCH_START = 0 #starting epoch
    
    config = {
        "learning_rate": 0.0005,
        "epoches": EPOCH_START + 1000000, #make sure if resuming this is the old + new together
        "batch_size": 128,
        "train_batch_freq": 10,
        "update_frequency": 1000,
        "calc_win_from": 10000, # Log frequency
        "buffer_size": 100000,
        "gamma": 0.95, 
        "start_balance": 1000000,
        "epsilon_decay": 200000
    }
    
    # Initialize WandB project or resume
    if RESUME_TRAINING and WANDB_RESUME_ID:
        # Resume existing run
        wandb.init(project="BlackJack-min", id=WANDB_RESUME_ID, resume="must", config=config)
    else:
        # Start new run
        wandb.init(project="BlackJack-min", config=config, name=RUN_NAME)
    
    # RUN VARIABLES
    win = 0 
    balance = config["start_balance"]
    env = Env(balance=balance)
    env.start()

    # Initialize player
    player = DQN_Agent_min() 
    player_hat = DQN_Agent_min() 
    
    # Try to load the .pth file.
    if RESUME_TRAINING:
        print(f"Loading model from: {PATH_TO_LOAD}")
        try:
            # Load weights
            player.DQN.load_state_dict(torch.load(PATH_TO_LOAD))
            print("Model loaded successfully.")
        except FileNotFoundError:
            print("Error: File not found. Starting from scratch.")
            
    player_hat.DQN = player.DQN.copy() 

    # Training variables (loaded from config)
    learning_rate = config["learning_rate"]
    epoches = config["epoches"]
    start_epoch = EPOCH_START if RESUME_TRAINING else 0
    batch_size = config["batch_size"]
    train_batch = config["train_batch_freq"]
    update_frequency = config["update_frequency"]
    calc_win_from = config["calc_win_from"] 
    
    # Counters & diagnostics
    surrenders = 0
    hits = 0
    doubles = 0
    splits = 0
    stands = 0
    overall = 0
    totalR = 0

    # Metrics for continuous logging
    running_loss = 0
    loss_count = 0
    running_reward = 0
    current_win_count = 0 

    # Optimizer
    optim = torch.optim.Adam(player.DQN.parameters(), lr=learning_rate)

    # Replay buffer
    buffer = ReplayBuffer(config["buffer_size"])

    # Start the user input listener thread
    input_thread = threading.Thread(target=listen_for_input, daemon=True)
    input_thread.start()

    # LOOP
    for epoch in range(start_epoch, epoches):
        if terminate_game:
            print("Game terminated by user.")
            break 
        
        done = False
        has_doubled = False
        episode_reward = 0 
        
        while not done:
            
            # S
            curr_state = env.state.get_state_AI() 
            
            # A
            action = player.get_Action(curr_state, epoch,start_epoch= start_epoch) if env.state.round_phase == 'playing' else 5 if epoch < epoches - 50000 else 6 
            
            p_sum = env.state.get_p_sum() #save these for the reward in case of a state override (for example, surrender)
            d_card_val = env.state.d_card
            
            # S'
            env.move(action, G=None)
            if action == 5 or action == 6:
                continue
            new_state = env.state.get_state_AI() 

            # R
            reward = 0
            check_end_status = 0

            #update counters & give reward for actions on specific circumstances.
            # Handle Hit reward
            if action == 0:
                hits += 1
                overall+=1
                if p_sum < 12:
                    reward += 0.15
                if p_sum == 12 and d_card_val <= 3: #new
                    reward += 0.5
                if p_sum >= 12 and p_sum <= 16 and d_card_val >= 7:
                    reward += 1# old - 0.3
                if p_sum >= 17 and 11 not in env.state.p_hand_vals: #punish on hard 17+
                    reward -= 1.5
                elif p_sum >= 19 and 11 in env.state.p_hand_vals: #punish on soft 19+
                    reward -= 1
                
            # Handle Double reward
            if action == 1:
                doubles += 1
                overall += 1
                has_doubled = True
                if p_sum < 12:
                    reward += 0.1
                if p_sum == 11 or (p_sum == 10 and d_card_val < 10):
                    reward += 1.5 #was 0.3
                elif p_sum >= 17 and 11 not in env.state.p_hand_vals: #punish on hard 17+
                    reward -= 1.5
                elif p_sum in [17, 18] and 11 in env.state.p_hand_vals: #punish on hard 17+
                    reward += 1 #was 0.3
                elif p_sum>= 19 and 11 in env.state.p_hand_vals: #punish on soft 19+
                    reward -= 1
                if 13 <= p_sum <= 18 and 3 <= d_card_val <= 6 and 11 in env.state.p_hand_vals:
                    reward += 0.2
                if 13 <= p_sum <= 15 and 2 <= d_card_val <= 3 and 11 in env.state.p_hand_vals: #new
                    reward -= 0.2
                
            # Handle Split - won't happen (masked, this is Split_Agent job)
            if action == 2:
                splits += 1
                overall += 1
                
            # Handle Stand reward
            if action == 3:
                stands += 1
                overall += 1
                if p_sum < 12 or (p_sum < 18 and 11 in env.state.p_hand_vals):
                    reward -= 2
                if p_sum == 18 and 11 in env.state.p_hand_vals and (d_card_val >= 9 or d_card_val <= 6): #added the <= 6
                    reward -= 2 
                if p_sum >= 12 and p_sum <= 16 and d_card_val >= 7:
                    reward -= 1.5
            
            # Handle Surrender reward
            if action == 4:
                reward -= 0.5
                done = True
                surrenders += 1
                overall += 1
                
                if p_sum >= 17:
                    reward -= 0.25
                elif p_sum == 16:
                    reward += 0.1
                elif p_sum in [15,16] and d_card_val >= 9:
                    reward += 1.2
                elif p_sum <= 15: 
                    reward -= 2
                    if p_sum == 14:
                        reward -= 2


            # Check if the game ended
            has_split = env.state.second_hand_active
            has_BJ = env.PCheckBJ()
            
            if env.checkend:
                check_end_status = env.CheckEnd()
                done = True 
                
                # Count wins logic
                if check_end_status in [1, 4, 5, 6, 8]: 
                    win += 1
                    current_win_count += 1 
                    if check_end_status == 1 and has_split:
                        win += 1
                        current_win_count += 1
                
                # Calculate reward
                reward += endgame_reward(has_BJ, check_end_status, action, env.state.get_p_sum(), has_split, has_doubled)
            

            # Update totals
            totalR += reward
            episode_reward += reward 
            
            buffer.push(curr_state, torch.tensor([action]), torch.tensor([reward], dtype=torch.float32), new_state, torch.tensor([1 if done else 0]))
            
            curr_state = new_state
        
        # Accumulate reward for logging
        running_reward += episode_reward

        # --- TRAINING BLOCK ---
        if len(buffer) > batch_size and epoch % train_batch == 0:
            states, actions, rewards, next_states, dones= buffer.sample(batch_size)
            
            Q_values = player.DQN(states)
            Q_current = Q_values.gather(1, actions.long())

            with torch.no_grad():
                Q_next = player_hat.DQN(next_states)
                max_next_Q = torch.max(Q_next, dim=1, keepdim=True)[0]
                Q_target = rewards + (0.99 * max_next_Q * (1 - dones))
            
            loss = player.DQN.MSELoss(Q_current, Q_target)
            
            # Track loss
            running_loss += loss.item()
            loss_count += 1
            
            loss.backward()
            optim.step()
            optim.zero_grad()
            
        if epoch % update_frequency == 0:
            player_hat.DQN = player.DQN.copy()

        # --- WANDB LOGGING & PRINTING ---
        if epoch > 0 and epoch % calc_win_from == 0:
            # Calculate averages
            avg_loss = running_loss / loss_count if loss_count > 0 else 0
            avg_reward = running_reward / calc_win_from
            win_rate = (current_win_count / calc_win_from) * 100
            epsilon = player.epsilon_greedy(epoch - start_epoch) 
            
            # Console output
            print(f"epoch: {epoch} | win rate: {win_rate:.2f}% | loss: {avg_loss:.4f} | epsilon: {epsilon:.3f}")
            
            # Log to WandB
            wandb.log({
                "epoch": epoch,
                "win_rate": win_rate,
                "loss": avg_loss,
                "avg_reward": avg_reward,
                "epsilon": epsilon,
                "balance": env.state.balance,
                "action_stats/hits": hits,
                "action_stats/stands": stands,
                "action_stats/doubles": doubles,
                "action_stats/surrenders": surrenders
            })
            
            # Reset counters
            current_win_count = 0
            running_loss = 0
            loss_count = 0
            running_reward = 0
            win = 0 


    # --- END OF TRAINING ---
    print(f"end balance: {env.state.balance}")
    print("PERCENTAGES")
    if overall > 0:
        print(f'hit: {100*(hits - player.C0)/overall}%')
        print(f'stand: {100*(stands - player.C3)/overall}%')
    
    # Save model artifact
    # torch.save(player.DQN.state_dict(), "checkpoints/" + RUN_NAME + ".pth")
    # wandb.save(RUN_NAME + ".pth")
    full_path = "checkpoints/" + RUN_NAME + ".pth"
    torch.save(player.DQN.state_dict(), full_path)
    wandb.save(full_path)
    
    ####### TEST PHASE ######
    print("\n--- STARTING TEST PHASE ---")
    test_epoches = 100000
    test_win = 0
    test_hits = 0
    test_stands = 0
    
    env.start()
    player.train = False
    player.setTrainMode()
    
    for epoch in range(test_epoches):
        if terminate_game:
            break
            
        done = False
        while not done:
            curr_state = env.state.get_state_AI()
            
            if env.state.round_phase == 'playing':
                action = player.get_Action(curr_state, epoch, train=False)
                if action == 0: test_hits += 1
                if action == 3: test_stands += 1
            else:
                action = 6 
            
            env.move(action, G=None)

            if action == 5 or action == 6:
                continue
            if action == 4: 
                done = True
                continue
            
            has_split = env.state.second_hand_active 
            
            if env.checkend:
                check_end_status = env.CheckEnd()
                done = True
                if check_end_status in [1, 4, 5, 6, 8]:
                    test_win += 1
                    if check_end_status == 1 and has_split:
                        test_win += 1
                
    final_test_rate = (test_win / test_epoches) * 100
    print(f"Test Win Rate: {final_test_rate}%")
    
    # Log final test result
    wandb.log({"test_win_rate": final_test_rate})
    wandb.finish() 

    total_moves = test_hits + test_stands
    if total_moves > 0:
        print(f"Test Hit Ratio: {test_hits / total_moves:.2%}")
    else:
        print("No moves made playing phases.")


def endgame_reward (has_BJ, check_end_status, last_action = 0, p_sum = 0, has_split = False, has_doubled = False):
    reward = 0
    match check_end_status:
        case 0:
            reward += 0
        case 1:
            reward += 1
            if has_split or has_doubled:
                reward += 1
            if has_BJ:
                reward += 0.5
        case 2:
            reward -= 1
            if has_split or has_doubled:
                reward -= 1
            # if last_action == 3 and p_sum < 17:
            #     reward -= 0.25
    return reward 


if __name__ == '__main__':
    main()