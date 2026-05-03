from env import Env
from random_agent import Random_Agent
from DQN_Agent import DQN_Agent
import matplotlib.pyplot as plt


def main():
    print("\n--- STARTING TEST PHASE ---")

    min_parametes_path = 'checkpoints/BlackJack-min-run-14.pth'
    split_parametes_path='checkpoints-split/BlackJack-split-run-11 (min model number 14).pth'
    agent = DQN_Agent(min_parametes_path, split_parametes_path, train=False)
    # agent = Random_Agent()
    # agent = DQN_Agent()
    env = Env(balance=10000)

    test_epoches = 100000
    test_win = 0
    extra_hands = 0 #how many hands were created by a split, to not cheat the win rate.
    balance_checkpoints = [10000]
    epoch_checkpoints = [0]
    
    env.start()
    
    for epoch in range(test_epoches):
        steps_count = 0 #will help catch problems and infinite loops
        done = False
        while not done:
            
            # debugging infinite loops
            steps_count += 1
            if steps_count > 100:
                print("infinite loop. printing state\n", str(env.state))
                env.start()
                break
            
            #choose action
            action = agent.get_Action(env=env, epoch=epoch, train=False)
            if action == 2:
                extra_hands += 1
            
            env.move(action, G=None)

            if action >= 5: #on betting
                continue
            if action == 4: 
                done = True
                continue
            
            has_split = env.state.second_hand_active 
            
            if env.checkend: #check if game ended
                check_end_status = env.CheckEnd()
                if check_end_status == 0:
                    continue
                
                done = True
                
                if epoch % 500 == 0: #uppate balance graph
                    balance_checkpoints.append(env.state.balance)
                    epoch_checkpoints.append(epoch)
                
                if check_end_status in [1, 4, 5, 6, 8]: #update win counters
                    test_win += 1
                    if check_end_status == 1 and has_split:
                        test_win += 1
                
    #print the results
    final_test_rate = (test_win / (test_epoches + extra_hands)) * 100
    print(f"Test Win Rate: {final_test_rate}%")
    print(f"Test Balance: {env.state.balance}")
    plot_simulation_results(epoch_checkpoints, balance_checkpoints)


def plot_simulation_results(episodes, balances):
    '''
    create a graph for the balance over time(epoches)
    '''
    
    plt.figure(figsize=(12, 6))
    plt.plot(episodes, balances, label='AI Bankroll', color='blue', linewidth=1.5)
    
    # Added the baseline comparison in 10,000 in red
    plt.axhline(y=10000, color='red', linestyle='--', label='Starting Capital')
    
    # The graph details
    plt.title('Blackjack AI Performance - 100,000 Hands', fontsize=14)
    plt.xlabel('Number of Hands', fontsize=12)
    plt.ylabel('Balance ($)', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    # The endpoint
    plt.annotate(f'Final: ${balances[-1]}', 
                 xy=(episodes[-1], balances[-1]), 
                 xytext=(episodes[-1]-10000, balances[-1]+1000),
                 arrowprops=dict(facecolor='black', shrink=0.05))
    
    plt.show()

if __name__ == '__main__':
    main()