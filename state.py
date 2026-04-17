import numpy as np
import torch

class State:
    '''
    A class that represents a state.

    Attributes:
    balance - the player's balance
    bet_val - holds the bet value for the main hand
    bet2_val - holds the bet value for the second hand (if exists)
    p_hand_vals - a list of the player's main hand values
    p2_hand_vals - a list of the player's secondary hand values
    d_hand_vals - a list of the dealer's hand values (when sending to AI will send only the first val)
    second_hand_active - is the player currently playing on the main or secondary hand
    '''
    
    def __init__(self, balance:int):
        '''
        initialize a state object. holds the round's information
        '''

        self.balance = balance
        self.bet_val = 0
        self.bet2_val = 0
        self.p_hand_vals = np.zeros(11, dtype=np.int32)
        self.d_card = 0
        self.p2_hand_vals = np.zeros(11, dtype=np.int32)
        self.second_hand_active = False
        self.round_phase = 'betting'

    def get_state(self): #(28,1) - [round phase, balance, first bet, second bet, dealer card, which hand is active, ---main hand---, ---secondary hand---]
        # add round phase as 0 or 1
        phase = 1 if self.round_phase == 'playing' else 0
        st = [phase, self.balance, self.bet_val, self.bet2_val, self.d_card, self.second_hand_active] #add all single digit data

        #add the main hand (11 values)
        for num in self.p_hand_vals:
            st.append(num)
        
        #add secondary hand(11 values)
        for num in self.p2_hand_vals:
            st.append(num)
        
        return torch.Tensor(st)
    
    def get_state_AI(self):
        if self.second_hand_active:
            st = [self.get_p2_sum() / 21, 1 if 11 in self.p2_hand_vals else 0, self.d_card/11]
        else:
            st = [self.get_p_sum() / 21, 1 if 11 in self.p_hand_vals else 0, self.d_card/11] #the divisions are for normalization.
        return torch.Tensor(st)
    
    def get_state_split(self):
        if self.second_hand_active:
            st = [self.p2_hand_vals[1] / 11, self.d_card/11]
        else:
            st = [self.p_hand_vals[1] / 11, self.d_card/11]
        return torch.Tensor(st)
    

    def __str__(self):
        return f''' BALANCE:{self.balance}
            BET1: {self.bet_val}
            BET2: {self.bet2_val}

            hand 1: {self.p_hand_vals} 
            hand 2: {self.p2_hand_vals} ACTIVE: {self.second_hand_active}

            dealer: {self.d_card}
        '''

    def get_bet(self, val):
        '''
        sets both bets to a given value
        '''
        self.bet_val = val
        self.bet2_val = val
    
    def get_p_sum(self):
        '''
        Gets the sum of the player's main / first hand.
        Automatically handles aces being 11 or 1.
        '''

        # First, convert all aces (if they were 1s) to 11
        for i in range(len(self.p_hand_vals)):
            if self.p_hand_vals[i] == 1:
                self.p_hand_vals[i] = 11

        total = np.sum(self.p_hand_vals)

        # While the total is >21 and there's still an 11 (ace), convert one 11 to 1
        while total > 21 and 11 in self.p_hand_vals:
            # Find the first 11 and convert it to 1
            for i in range(len(self.p_hand_vals)):
                if self.p_hand_vals[i] == 11:
                    self.p_hand_vals[i] = 1
                    break
            total = np.sum(self.p_hand_vals)

        return total
    
    def get_p2_sum(self):
        '''
        gets the sum of the player's secondary hand
        Automatically handles aces being 11 or 1.
        '''

        # First, convert all aces (if they were 1s) to 11
        for i in range(len(self.p2_hand_vals)):
            if self.p2_hand_vals[i] == 1:
                self.p2_hand_vals[i] = 11

        total = np.sum(self.p2_hand_vals)

        # While the total is >21 and there's still an 11 (ace), convert one 11 to 1
        while total > 21 and 11 in self.p2_hand_vals:
            # Find the first 11 and convert it to 1
            for i in range(len(self.p_hand_vals)):
                if self.p2_hand_vals[i] == 11:
                    self.p2_hand_vals[i] = 1
                    break
            total = np.sum(self.p2_hand_vals)

        return total
    