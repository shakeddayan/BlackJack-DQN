from Split_Agent import Split_Agent
import torch

'''
get_specific card
create env.splitstart() which will start with a splittable hand no matter what.
(make sure what the split rules are before changing them.)
create a trainer which will get a split state, will decide if to split and let a trained min model for getting through the rest of the game.
give a reward and train only the split agent, you can try to train together later.
'''

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
    # torch.set_num_threads(1)
    
    global terminate_game
    
    # --- WandB Configuration ---
    # Define hyperparameters for tracking
    RUN_NUM = 11
    FOR_MIN_MODEL_NUM = 14
    RUN_NAME = f"BlackJack-split-run-{RUN_NUM} (min model number {FOR_MIN_MODEL_NUM})" #the run name
    RESUME_TRAINING = False #is resuming another already saved run?
    PATH_TO_LOAD = "checkpoints-split/BlackJack-split-run-3 (min model number 9).pth" #path to load
    WANDB_RESUME_ID = "ycbqnzoj"
    EPOCH_START = 0 #starting epoch
    
    config = {
        "learning_rate": 0.0005,
        "epoches": EPOCH_START + 3000000, #make sure if resuming this is the old + new together
        "batch_size": 64,
        "train_batch_freq": 10,
        "calc_win_from": 10000, # Log frequency
        "buffer_size": 50000,
        "gamma": 0.99, 
        "start_balance": 10000,
        "epsilon_decay": 500000,
        "min_model_num": FOR_MIN_MODEL_NUM
    }
    
    # Initialize WandB project or resume
    if RESUME_TRAINING and WANDB_RESUME_ID:
        # Resume existing run
        wandb.init(project="BlackJack-split", id=WANDB_RESUME_ID, resume="must", config=config)
    else:
        # Start new run
        wandb.init(project="BlackJack-split", config=config, name=RUN_NAME)
    
    # RUN VARIABLES
    win = 0 
    balance = config["start_balance"]
    env = Env(balance=balance)
    env.start(force_split=True)

    # Initialize player
    player = DQN_Agent_min(parametes_path=f'checkpoints/BlackJack-min-run-{config["min_model_num"]}.pth', train=False)
    splitter = Split_Agent()
    
    # Try to load the .pth file.
    if RESUME_TRAINING:
        print(f"Loading model from: {PATH_TO_LOAD}")
        try:
            # Load weights
            splitter.DQN.load_state_dict(torch.load(PATH_TO_LOAD, weights_only=True))
            print("Model loaded successfully.")
        except FileNotFoundError:
            print("Error: File not found. Starting from scratch.")
            

    # Training variables (loaded from config)
    learning_rate = config["learning_rate"]
    epoches = config["epoches"]
    start_epoch = EPOCH_START if RESUME_TRAINING else 0
    batch_size = config["batch_size"]
    train_batch = config["train_batch_freq"]
    calc_win_from = config["calc_win_from"] 
    
    # Counters & diagnostics
    splits = 0
    overall = 0
    totalR = 0

    # Metrics for continuous logging
    running_loss = 0
    loss_count = 0
    running_reward = 0
    current_win_count = 0 

    # Optimizer
    optim = torch.optim.Adam(splitter.DQN.parameters(), lr=learning_rate)

    # Replay buffer
    buffer = ReplayBuffer(config["buffer_size"])

    # Start the user input listener thread
    # input_thread = threading.Thread(target=listen_for_input, daemon=True)
    # input_thread.start()

    # LOOP
    for epoch in range(start_epoch, epoches):
        if terminate_game:
            print("Game terminated by user.")
            break 
        # print('epoch start - line 131')
        done = False
        episode_reward = 0 
        save_state = False
        # moves_made = 0
        # action = None
        
        while not done:
            # print('turn start - line 137')
            env.checkend = False
            # moves_made += 1
            # if moves_made > 50:
                # print(f'CRITICAL: Infinite loop detected! Phase: {env.state.round_phase}, Action: {action}')
                # print(env.state)
                # print('d_hand_vals: ', env.d_hand_vals)
                # break
            
            # S
            curr_state = env.state.get_state_split() #the state of the current playing hand.
            # print('got state - line 142')
            
            # A
            action = None
            split_legal = env.is_action_legal(2)
            if split_legal: #if can split.
                save_state = True #save to buffer later.
                saved_split_state = curr_state #save the state.
                # make a decision: 1-split, 0-do something else.
                decision = splitter.get_Action(curr_state, epoch=epoch, start_epoch=start_epoch)
                #save the decision for the buffer.
                saved_decision = decision
                
                if decision == 1: #if decided to split
                    action = 2 # action is split
                
            if action != 2: #else use min model selection if can't/didn't split (action will be None).
                min_state = env.state.get_state_AI() #needs a different format
                action = player.get_Action(min_state,has_split=env.splitted, epoch=epoch, start_epoch=start_epoch,train=False) if env.state.round_phase == 'playing' else 5 if epoch < epoches - 50000 else 6 
            # print('got action - line 161')
            # S'
            

            # R
            reward = 0
            check_end_status = 0

            #update counters
            # if action == 1:
            #     has_doubled = True
            
            #put the values into variables for simplicty and readability.
            pair_val = env.state.p_hand_vals[1] #take the second card, in case of aces the first will be 1.
            d_card = env.state.d_card #get the dealer open card.
            
            if action == 2:
                splits += 1
                overall += 1
                
                #run 11 - added more conditions to target cases with small pair_val and high d_card.
                if pair_val == 11 or pair_val == 8:
                    reward += 3
                elif pair_val == 10 or pair_val == 5:
                    reward -= 5
                elif pair_val in [6, 7] and d_card >= 8:
                    reward -= 5
                elif pair_val == 9 and d_card in [7, 10, 11]:
                    reward -= 5
                elif pair_val == 2 and d_card in [8,9]:
                    reward -= 5
                #new - run 11
                elif pair_val in [2, 3] and d_card >= 8:
                    reward -= 5
                elif pair_val == 4 and d_card not in [5, 6]:
                    reward -= 5
                elif pair_val == 4 and d_card in [5, 6]:
                    reward += 5
            else:
                if pair_val == 5 or pair_val == 10:
                    reward += 2
                elif pair_val == 8 or pair_val == 11:
                    reward -= 5
                elif pair_val == 9 and d_card == 2:
                    reward -= 5
                elif pair_val in [6,7] and d_card >= 8:
                    reward += 2
                elif pair_val == 9 and d_card in [7, 10, 11]:
                    reward += 2
                elif pair_val == 2 and d_card in [8, 9]:
                    reward += 2
                    #new - run 11
                elif pair_val in [2, 3] and d_card >= 8:
                    reward += 2
                elif pair_val == 4 and d_card not in [5, 6]:
                    reward += 2
                elif pair_val == 4 and d_card in [5, 6]:
                    reward -= 5

            env.move(action, G=None)
            # print('env moved - line 177')

            # Check if the game ended
            has_BJ = env.PCheckBJ()
            
            if env.checkend:
                # print('starting checkend - line 183')
                check_end_status = env.CheckEnd(force_split=True)
                # print('after checkend - line 185')
                
                if check_end_status == 0: #not finished.
                    # print('not finished (continue) - line 188')
                    continue
                
                #if here, the game is done
                # print('game is done - line 192')
                done = True 
                
                # Calculate reward
                reward += endgame_reward(check_end_status)
                # print('reward calculated - line 197')
                
                # Count wins logic
                if check_end_status in [1, 4, 5, 6, 8]: 
                    win += 1
                    # print('adding win to counter - line 202')
                    current_win_count += 1 
                    if check_end_status == 1 and env.splitted:
                        win += 1
                        current_win_count += 1
                
                
            
            if action == 5 or action == 6:
                # print('skipping betting - line 211')
                continue
            

            # Update totals
            totalR += reward
            episode_reward += reward 
            
            
        if save_state: #save to buffer the decision and game reward.
            # print('saving to buffer - line 221')
            buffer.push_split(saved_split_state, torch.tensor([saved_decision]), torch.tensor([reward], dtype=torch.float32))
            
        
        # Accumulate reward for logging
        running_reward += episode_reward

        # --- TRAINING BLOCK ---
        # print('starting training - line 229')
        if len(buffer) > batch_size and epoch % train_batch == 0:
            # print('training - line 232')
            states, actions, rewards= buffer.sample_split(batch_size)
            
            Q_values = splitter.DQN(states)
            Q_current = Q_values.gather(1, actions.long())
            rewards = rewards.view(-1, 1)

            # every state is terminal, split only once. done = true always 
            # so the bellman equation is Q(s,a) = R
            # hence why there is no second network.
            #
            # with torch.no_grad():
            #     Q_next = splitter_hat.DQN(next_states)
            #     max_next_Q = torch.max(Q_next, dim=1, keepdim=True)[0]
            #     Q_target = rewards + (0.99 * max_next_Q * (1 - dones))
            
            loss = torch.nn.MSELoss()(Q_current, rewards)
            
            # Track loss
            running_loss += loss.item()
            loss_count += 1
            
            loss.backward()
            optim.step()
            optim.zero_grad()
            

        # --- WANDB LOGGING & PRINTING ---
        if epoch > 0 and epoch % calc_win_from == 0:
            # print('logging to wandb - line 259')
            # Calculate averages
            avg_loss = running_loss / loss_count if loss_count > 0 else 0
            avg_reward = running_reward / calc_win_from
            win_rate = (current_win_count / calc_win_from) * 100
            epsilon = splitter.epsilon_greedy(epoch - start_epoch) 
            
            # Console output
            # print('checkpoint - line 267')
            print(f"epoch: {epoch} | win rate: {win_rate:.2f}% | loss: {avg_loss:.4f} | epsilon: {epsilon:.3f}")
            
            # Log to WandB
            wandb.log({
                "epoch": epoch,
                "win_rate": win_rate,
                "loss": avg_loss,
                "avg_reward": avg_reward,
                "epsilon": epsilon,
                "balance": env.state.balance,
                "splits_taken": splits
            })
            
            # Reset counters
            current_win_count = 0
            running_loss = 0
            loss_count = 0
            running_reward = 0
            win = 0 


    # --- END OF TRAINING ---
    print(f"end balance: {env.state.balance}")
    
    # Save model artifact
    # torch.save(player.DQN.state_dict(), "checkpoints/" + RUN_NAME + ".pth")
    # wandb.save(RUN_NAME + ".pth")
    full_path = "checkpoints-split/" + RUN_NAME + ".pth"
    torch.save(splitter.DQN.state_dict(), full_path)
    wandb.save(full_path)
    
    ####### TEST PHASE ######
    print("\n--- STARTING TEST PHASE ---")
    test_epoches = 100000
    test_win = 0
    extra_hands = 0 #how many hands were created by a split, to not cheat the win rate.
    env.state.balance = 0 #prevent integer overflow.
    
    env.start(force_split=True)
    splitter.train = False
    splitter.setTrainMode()
    
    for epoch in range(test_epoches):
        if terminate_game:
            break
        
        #restart a new game.
        env.start(force_split=True) #added here because on surrender the game would just get stuck on a terminal losing state. will take effect from run 10+.
        
        done = False
        while not done:
            curr_state = env.state.get_state_split()
            
            if env.state.round_phase == 'playing':
                action = None
                split_legal = env.is_action_legal(2)
                if split_legal: #if can split.
                    # make a decision: 1-split, 0-do something else.
                    decision = splitter.get_Action(curr_state, epoch=epoch, train=False)
                    if decision == 1:
                        action = 2
                        extra_hands += 1
                
                if action != 2:
                    min_state = env.state.get_state_AI() #needs a different format
                    action = player.get_Action(min_state, epoch, train=False)
            else:
                action = 6 
            
            env.move(action, G=None, force_split=True)

            if action == 5 or action == 6:
                continue
            if action == 4: 
                done = True
                continue
            
            has_split = env.state.second_hand_active 
            
            if env.checkend:
                check_end_status = env.CheckEnd(force_split=True)
                done = True
                if check_end_status in [1, 4, 5, 6, 8]:
                    test_win += 1
                    if check_end_status == 1 and has_split:
                        test_win += 1
                
    final_test_rate = (test_win / (test_epoches + extra_hands)) * 100
    print(f"Test Win Rate: {final_test_rate}%")
    
    # Log final test result
    wandb.log({"test_win_rate": final_test_rate})
    wandb.finish() 


def endgame_reward (check_end_status):
    reward = 0
    match check_end_status:
        case 0: #didn't end
            reward += 0
        case 1: #won both\main hands
            reward += 2
        case 2: #lost both\main hands
            reward -= 2
        case 3,4,5: #draw both\main hands or win one hand and lose the other
            reward += 0
        case 6,8: #win on one hand and draw on the other
            reward += 1
        case 7,9: #lose one hand and draw on the other
            reward -= 1
    
    return reward 


if __name__ == '__main__':
    main()