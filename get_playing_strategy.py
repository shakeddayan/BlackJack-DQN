import torch
from human_agent import Human_Agent
from random_agent import Random_Agent
from DQN_Agent_min import DQN_Agent_min
from DQN_Agent import DQN_Agent
from Split_Agent import Split_Agent



def main():
    '''
    will create a table with the playing strategy of a min model and his split agent.
    '''
    WITH_SPLIT = False
    MIN_MODEL_NUM = 14 #the min model number
    SPLIT_MODEL_NUMS = (8, 14) #the split model number, and what min model was it created for.

    min_parametes_path=f'checkpoints/BlackJack-min-run-{MIN_MODEL_NUM}.pth'
    split_parametes_path=f'checkpoints-split/BlackJack-split-run-{SPLIT_MODEL_NUMS[0]} (min model number {SPLIT_MODEL_NUMS[1]}).pth'
    agent = DQN_Agent(min_parametes_path, split_parametes_path, train=False)
    
    
    #HARD HANDS - NO PAIRS
    hard_hands_no_pairs = []
    
    for i in range(5, 20): #the possibilites for player sum(5-19). i = player sum
        this_hand_actions = []
        for j in range (2, 12): #dealer open card possibilities. j = dealer card
            this_hand_actions.append(agent.min_agent.get_Action(torch.Tensor([i / 21, 0, j / 11]), train=False)) #get_state_AI()
        hard_hands_no_pairs.append(this_hand_actions)
    
    #SOFT HANDS - NO PAIRS
    soft_hands_no_pairs = []
    
    for i in range(13, 21): #the possibilites for player sum(13-20). i = player sum
        this_hand_actions = []
        for j in range (2, 12): #dealer open card possibilities. j = dealer card
            this_hand_actions.append(agent.min_agent.get_Action(torch.Tensor([i / 21, 1, j / 11]), train=False)) #get_state_AI()
        soft_hands_no_pairs.append(this_hand_actions)
    
    #PAIRS
    pairs = []
    
    for i in range(2, 12):
        this_hand_actions = []
        for j in range(2,12):
            decision = agent.split_agent.get_Action(torch.Tensor([i / 11, j / 11]), train = False) #get_state_split
            if decision == 1: #if decided to split
                this_hand_actions.append(2)
            else: #choose according to min model.
                this_hand_actions.append(agent.min_agent.get_Action(torch.Tensor([i * 2 / 21, 0 if i != 11 else 1, j / 11]), train=False)) #get_state_AI()
        pairs.append(this_hand_actions)
        
    #BLACKJACKS
    bj = []
    for j in range(2,12):
        bj.append(agent.min_agent.get_Action(torch.Tensor([1, 1, j / 11]), train=False))
    
    # ==========================================
    # --- PRINTING THE RESULTS AS TABLES ---
    # ==========================================

    # def print_row(label, actions):
    #     # Helper to format each row nicely
    #     formatted_actions = "   ".join([str(a).rjust(2) for a in actions])
    #     print(f"{str(label).ljust(10)} | {formatted_actions}")

    # print("\n" + "="*50)
    # print(" HARD HANDS - NO PAIRS ")
    # print("="*50)
    # print("Player Sum | Dlr: 2    3    4    5    6    7    8    9   10   11")
    # print("-" * 55)
    # for idx, actions in enumerate(hard_hands_no_pairs):
    #     print_row(idx + 5, actions)
    
    #write to the output csv file.
    with open(f"startegies/strat_min{MIN_MODEL_NUM}_split{SPLIT_MODEL_NUMS[0]}.csv", "w") as f:
        #write the next table title
        f.write("HARD HANDS - NO PAIRS\n")
        f.write("P_SUM \\ D_HAND,") #the corner of the table
        f.write(",".join(map(str, range(2,12))) + "\n") #the dealer's open card
        f.writelines(map(lambda list, index: str(index) + "," + ",".join(map(str, list)) + "\n", hard_hands_no_pairs, map(str, range(5, 5 + len(hard_hands_no_pairs))))) #fill in the values of the testing
        #a few breaks between tables
        f.write("\n\n\n")

        #write the next table title
        f.write("SOFT HANDS - NO PAIRS\n")
        f.write("P_SUM \\ D_HAND,") #the corner of the table
        f.write(",".join(map(str, range(2,12))) + "\n") #the dealer's open card
        f.writelines(map(lambda list, index: str(index) + "," + ",".join(map(str, list)) + "\n", soft_hands_no_pairs, map(str, range(13, 13 + len(soft_hands_no_pairs))))) #fill in the values of the testing
        #a few breaks between tables
        f.write("\n\n\n")

        #write the next table title
        f.write("PAIRS\n")
        f.write("P_SUM \\ D_HAND,") #the corner of the table
        f.write(",".join(map(str, range(2,12))) + "\n") #the dealer's open card
        f.writelines(map(lambda list, index: str(index) + "," + ",".join(map(str, list)) + "\n", pairs, map(str, range(2, 2 + len(pairs))))) #fill in the values of the testing
        #a few breaks between tables
        f.write("\n\n\n")

        #write the next table title
        f.write("BLACKJACKS\n")
        f.write("P_SUM \\ D_HAND,") #the corner of the table
        f.write(",".join(map(str, range(2,12))) + "\n") #the dealer's open card
        f.write("BlackJack (21):," + ",".join(map(str, bj))+ "\n") #fill in the values of the testing
        #a few breaks between tables
        f.write("\n\n\n")


    # print("\n" + "="*50)
    # print(" SOFT HANDS - NO PAIRS ")
    # print("="*50)
    # print("Player Sum | Dlr: 2    3    4    5    6    7    8    9   10   11")
    # print("-" * 55)
    # for idx, actions in enumerate(soft_hands_no_pairs):
    #     print_row(idx + 13, actions)

    # print("\n" + "="*50)
    # print(" PAIRS ")
    # print("="*50)
    # # Note: the pairs dealer loop goes from 1 to 10
    # print("Pair Card  | Dlr: 2    3    4    5    6    7    8    9   10   11") 
    # print("-" * 60)
    # for idx, actions in enumerate(pairs):
    #     # i starts at 2 and steps by 2 (2, 4, 6, 8, 10)
    #     pair_val = 2 + (idx) 
    #     print_row(pair_val, actions)

    # print("\n" + "="*50)
    # print(" BLACKJACKS ")
    # print("="*50)
    # print("Player Sum | Dlr: 2    3    4    5    6    7    8    9   10   11")
    # print("-" * 55)
    # print_row("BJ (21)", bj)
    # print("\n")


#run the main game loop
if __name__ == '__main__':
    main()