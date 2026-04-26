import pygame
# from screenObjects.slider import Slider
# from screenObjects.button import Circle_Button, Rectangle_Button
from graphics import Graphics
from state import State
from deck import Deck
from card import Card
import numpy as np

class Env:
    '''
    A class that represents the environment - manages the game.

    Attributes:
        screen - the main screen surface (used this atribute in DOUBLE function to display the new bet for a moment)
        Deck - the deck of cards
        Pplays - if this is the player's turn to play
        Dplayed - the dealer finished his turn
        round_phase - the phase of the game: betting / playing
        checkend - if need to check end in the main loop
        state - the state of the game and round information.
    '''

    #initialization and managment
    def __init__(self, G:Graphics = None, balance:int = 0):
        '''
        initialize a new Env object, and set everything to the default.
        '''

        self.deck = Deck() #the deck to take cards from
        self.Pplays = True #if the player still plays
        self.Dplayed = False #if the dealer played already
        self.checkend = False #if need to check end in the main loop.
        self.state = State(balance) # holds the game state.
        self.state.round_phase = 'betting' #will hold the round phase: betting / playing, and will help lock buttons accordingly
        self.d_hand_vals = np.zeros(11, dtype=np.int32)
        self.splitted = False
        self.state.get_bet(G.bet.get_value() if G != None else 0) #store the bet value in the state
    
    # def render_graphics(self, G:Graphics):
    #     #draw bet slider
    #     G.bet.max = self.state.balance
    #     #choose the active hand's bet
    #     G.bet.set_value(self.state.bet_val if not self.state.second_hand_active else self.state.bet2_val)
    #     G.bet.render(G)

    def start(self, G:Graphics = None, force_split = False):
        '''
        zero the game without affecting the balance, so can play another round.
        '''

        self.state.p_hand_vals = np.zeros(11, dtype=np.int32) #empty the list of card values 
        self.state.p2_hand_vals = np.zeros(11, dtype=np.int32) #empty the list of card values 
        self.d_hand_vals = np.zeros(11, dtype=np.int32) #empty the list of card values
        self.state.second_hand_active = False #play main hand
        self.splitted = False #make sure splitted mode is off
        self.deck = Deck() #remake the deck with all cards
        self.Pplays = True #make it the players turn
        self.Dplayed = False #the dealer hasn't played yet
        self.state.round_phase = 'betting' #set the game state to betting
        self.state.get_bet(0) #store the bet value in the state       G.bet.get_value() if G != None else

        if G != None:
            G.p_hand = [] #empty the list of graphic cards to print out
            G.p2_hand = [] #empty the list of graphic cards to print out
            G.d_hand = [] #empty the list of graphic cards to print out
            G.p_turn = 1 #how many turns have gone through, will help display the cards graphically
            G.p2_turn = 1 #how many turns have gone through, will help display the cards graphically
            G.d_turn = 1 #how many turns have gone through, will help display the cards graphically
            G.bet.set_value(0) #zero the bet

        #load beginning state: two cards for the player and two for the dealer
        cardTMP = self.deck.get_card()
        self.add_card(cardTMP, 'player', G)
        # if G != None:
        #     G.load_card(cardTMP, 'player', self)
        #     G.p_turn += 1
        # else:
        #     self.append_hand(cardTMP.value if isinstance(cardTMP.value, int) else (10 if cardTMP.value != 'ace' else 11), self.state.p_hand_vals)

        if force_split:
            cardTMP = self.deck.get_specific(cardTMP.value)
        else:
            cardTMP = self.deck.get_card()
        self.add_card(cardTMP, 'player', G)
        # if G != None:
        #     G.load_card(cardTMP, 'player', self)
        #     G.p_turn += 1
        # else:
        #     self.append_hand(cardTMP.value if isinstance(cardTMP.value, int) else (10 if cardTMP.value != 'ace' else 11), self.state.p_hand_vals)
        
        cardTMP = self.deck.get_card()
        self.add_card(cardTMP, 'dealer', G)
        # if G != None:
        #     G.load_card(cardTMP, 'dealer', self)
        #     G.d_turn += 1
        # else:
        #     self.append_hand(cardTMP.value if isinstance(cardTMP.value, int) else (10 if cardTMP.value != 'ace' else 11), self.d_hand_vals)
        self.state.d_card = cardTMP.value if isinstance(cardTMP.value, int) else 10 if cardTMP.value != 'ace' else 11
        
        cardTMP = self.deck.get_card()
        self.add_card(cardTMP, 'dealer', G)
        # if G != None:
        #     G.load_card(cardTMP, 'dealer', self)
        #     G.d_turn += 1
        # else:
        #     self.append_hand(cardTMP.value if isinstance(cardTMP.value, int) else (10 if cardTMP.value != 'ace' else 11), self.d_hand_vals)
    
    def append_hand(self, value:int, hand:np.ndarray):
        for i in range(len(hand)):
            if hand[i] == 0:
                hand[i] = value
                return
            
    def add_card(self, card:Card, hand_to_add, G:Graphics = None):
        if G != None:
            G.load_card(card, hand_to_add, self)
            if hand_to_add =='player':
                G.p_turn = G.p_turn + 1 
            elif hand_to_add == 'dealer':
                G.d_turn = G.d_turn + 1 
            else:
                G.p2_turn = G.p2_turn + 1
        else:
            hand_vals = self.state.p_hand_vals if hand_to_add =='player' else self.d_hand_vals if hand_to_add == 'dealer' else self.state.p2_hand_vals
            self.append_hand(card.value if isinstance(card.value, int) else (10 if card.value != 'ace' else 11), hand_vals)
    
    def pop_hand(self, hand:np.ndarray):
        for i in range(len(hand)):
            if hand[i] == 0:
                value = hand[i -1]
                hand[i - 1] = 0
                return value

    def get_d_sum(self):
        '''
        gets the sum of the player's secondary hand
        Automatically handles aces being 11 or 1.
        '''

        # First, convert all aces (if they were 1s) to 11
        for i in range(len(self.d_hand_vals)):
            if self.d_hand_vals[i] == 1:
                self.d_hand_vals[i] = 11

        total = np.sum(self.d_hand_vals)

        # While the total is >21 and there's still an 11 (ace), convert one 11 to 1
        while total > 21 and 11 in self.d_hand_vals:
            # Find the first 11 and convert it to 1
            for i in range(len(self.d_hand_vals)):
                if self.d_hand_vals[i] == 11:
                    self.d_hand_vals[i] = 1
                    break
            total = np.sum(self.d_hand_vals)

        return total
    
    #PLAYING FUNCTIONS
    def HIT(self, G:Graphics):
        '''
        the player hits - takes a card
        '''

        #add a card from the deck to the active hand
        card = self.deck.get_card()
        if not self.state.second_hand_active:
            self.add_card(card, 'player', G)
            # G.load_card(card, 'player', self)
            # G.p_turn += 1
        else:
            self.add_card(card, 'player2', G)
            # G.load_card(card, 'player2', self)
            # G.p2_turn += 1
            
        #check for bust
        if ((self.splitted and not self.state.second_hand_active) or not self.splitted) and self.PCheckBust(): #if playing on main hand and busted
            if self.splitted: #move to next hand or end the game
                self.state.second_hand_active = True
            else:
                #dealer play
                self.Pplays = False
                self.Dplay(G)
                self.Dplayed = True

        elif self.state.second_hand_active and self.P2CheckBust(): #if playing on second hand and busted
            self.Pplays = False
            self.Dplay(G)
            self.Dplayed = True

        self.checkend = True
    
    def DOUBLE(self, G:Graphics): 
        '''
        double - double the bet, hit a last card and stop playing(stand)
        only legal when the bets don't exceed the balance
        '''

        # Double the bet
        if not self.state.second_hand_active:
            self.state.bet_val = min(self.state.bet_val * 2, self.state.balance)
            if G != None:
                G.bet.set_value(min(self.state.bet_val, G.bet.max))  # Ensure it doesn't exceed the max value
        else:
            self.state.bet2_val = min(self.state.bet2_val * 2, self.state.balance)
            if G != None:
                G.bet.set_value(min(self.state.bet2_val, G.bet.max))  # Ensure it doesn't exceed the max value
        
        #make the bet change visible in case of a split
        if G != None:
            G.bet.render(G, self.state.bet2_val if self.state.second_hand_active else self.state.bet_val)
            pygame.display.update()
            pygame.time.wait(500)
        # Save the current state of second_hand_active before hitting
        was_second_hand_active = self.state.second_hand_active

        # Perform a hit
        self.HIT(G)

        # If we're in split mode, first hand, and not already on second hand after HIT,
        # then proceed with STAND. Otherwise, we've already switched to second hand due to bust.
        if not self.splitted or self.state.second_hand_active == was_second_hand_active:
            self.STAND(G)

    def SPLIT(self, G:Graphics):
        '''
        split the hand into 2 hands - only if you have 2 cards in the hand, and they have the same value.
        '''
        
        self.splitted = True #set splitted mode

        #move the second card to the second hand:graphically
        if G != None:
            card_pic = G.p_hand.pop()[0]
            G.p2_hand.append((card_pic ,(G.PLAYER2_X + G.p2_turn * G.HAND_CARD_OFFSETS - G.CARD_WIDTH / 2 ,G.PLAYER_Y)))
            G.p2_turn += 1
            G.p_turn -= 1

        #move the value
        self.append_hand(self.pop_hand(self.state.p_hand_vals), self.state.p2_hand_vals)

        #change main deck position
        if G != None:
            G.p_hand[0] =(G.p_hand[0][0], (G.PLAYER_X_SPLITTED + G.HAND_CARD_OFFSETS - G.CARD_WIDTH / 2, G.PLAYER_Y))
        
        #add another card to each hand
            #main hand:
        cardTMP = self.deck.get_card()
        self.add_card(cardTMP, 'player', G)
            #secondary hand:
        cardTMP = self.deck.get_card()
        self.add_card(cardTMP, 'player2', G)
        
    
        #make bets match
        self.state.get_bet(self.state.bet_val)

    def STAND(self, G:Graphics): 
        '''
        stand - stop playing, and let the dealer play (or move to second hand if splitted).
        '''
        #if it is supposed to be the dealer's turn
        if (self.splitted and self.state.second_hand_active) or not self.splitted:
            self.Pplays = False
            self.Dplay(G)
            self.Dplayed = True
            self.checkend = True
        else: #if needs to move to the second hand
            self.state.second_hand_active = True
            self.checkend = True
    
    def SURRENDER(self, G:Graphics, force_split = False): 

        '''
        surrender- end the game immediatly, and lose half of the bet
        legal only if not splitted
        '''

        self.state.balance -= int(0.5 * self.state.bet_val)
        if G != None:
            G.bet.set_value(0)
        self.start(G, force_split=force_split)

    def BET(self, G:Graphics = None, bet_action = 5):
        '''
        bet money on the coming game (according to the slider)
        '''
        if not self.splitted or (self.splitted and not self.state.second_hand_active):
            # self.state.bet_val =  int(self.state.balance * ((bet_action - 5)/10 if bet_action != 16 else 0.01)) #G.bet.get_value() if G != None else
            self.state.bet_val =  int(self.state.balance * (bet_action - 5)/10 if bet_action != 16 else 10) #G.bet.get_value() if G != None else
            if G != None:
                G.bet.set_value(self.state.bet_val)
        else:
            # self.state.bet2_val = int(self.state.balance * ((bet_action - 5)/10 if bet_action != 16 else 0.01)) #G.bet.get_value() if G != None else 
            self.state.bet2_val = int(self.state.balance * (bet_action - 5)/10 if bet_action != 16 else 10) #G.bet.get_value() if G != None else 
            if G != None:
                G.bet.set_value(self.state.bet2_val)
        self.state.round_phase = 'playing'
    
    #make a move
    def move(self, action:int, G:Graphics, force_split = False):
        '''
        perform a given action if it is legal
        '''
        if self.is_action_legal(action):
            match action:
                case 0:
                    self.HIT(G)
                case 1:
                    self.DOUBLE(G)
                case 2:
                    self.SPLIT(G)
                case 3:
                    self.STAND(G)
                case 4:
                    self.SURRENDER(G, force_split)
                case 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16:
                    self.BET(G, action)

    #check legal functions
    def is_action_legal(self, action: int):
        '''
        return if the given action is legal in this state.
        '''
        if action is None:
            return False
        match action:
            case 0 | 3:
                return self.state.round_phase == 'playing'
            case 1:
                if self.state.round_phase == 'playing': #if playing, not legal in betting phase
                    if self.splitted: #if splitted
                        if not self.state.second_hand_active: #if doubling the first hand
                            return self.state.bet_val * 2 + self.state.bet2_val <= self.state.balance #return if the bets are not exceeding the balance
                        else: #if doubling the second hand
                            return self.state.bet_val + self.state.bet2_val * 2 <= self.state.balance #return if the bets are not exceeding the balance
                    else: #not splitted
                        return self.state.bet_val * 2 <= self.state.balance #check if the bet does not exceed the balance
                else:
                    return False #if not playing
            case 2:
                card_amount = 0
                for i in range(len(self.state.p_hand_vals)):
                    if(self.state.p_hand_vals[i] != 0):
                        card_amount += 1
                return self.state.round_phase == 'playing' and (not self.splitted) and card_amount == 2 and (self.state.p_hand_vals[0] == self.state.p_hand_vals[1] or self.state.p_hand_vals[0] == 1 and self.state.p_hand_vals[1] == 11) and self.state.bet_val * 2 <= self.state.balance
            case 4:
                return not self.splitted
            case 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16:
                return self.state.round_phase == 'betting'

    def get_legal_actions(self):
        '''
        gets a numpy array that shows which actions are legal in the current state. (0 = not legal, 1 = legal)
        '''

        actions = np.zeros(17, dtype=np.int32)
        for i in range(len(actions)):
            if self.is_action_legal(i):
                actions[i] = 1
        return actions

    #end game checks
    def PCheckBust(self):
        '''
        checks if the player's main hand busted
        '''
        return self.state.get_p_sum() > 21
    
    def P2CheckBust(self):
        '''
        checks if the player's secondary hand busted
        '''
        return self.state.get_p2_sum() > 21
    
    def DCheckBust(self) -> bool:
        '''
        checks if the dealer busted
        '''
        return self.get_d_sum() > 21
    
    def PCheckBJ(self):
        '''
        checks if the player's main hand has a BlackJack
        '''
        
        card_amount = 0
        for i in range(len(self.state.p_hand_vals)):
            if self.state.p_hand_vals[i] != 0:
                card_amount += 1
        return self.state.get_p_sum() == 21 and card_amount == 2
    
    def P2CheckBJ(self):
        '''
        checks if the player's second hand has a BlackJack
        '''
        
        card_amount = 0
        for i in range(len(self.state.p2_hand_vals)):
            if self.state.p2_hand_vals[i] != 0:
                card_amount += 1
        return self.state.get_p2_sum() == 21 and card_amount == 2
    
    def DCheckBJ(self):
        '''
        checks if the dealer has a BlackJack
        '''

        card_amount = 0
        for i in range(len(self.d_hand_vals)):
            if self.d_hand_vals[i] != 0:
                card_amount += 1
        
        return self.get_d_sum() == 21 and card_amount == 2

    def Dplay(self, G:Graphics = None):
        '''
        make the dealer play.
        the dealer is automatic - hits until he has a total sum of 17, then stops.
        '''

        while self.get_d_sum() < 17 and not self.DCheckBust():
            card = self.deck.get_card()
            self.add_card(card, 'dealer', G)
        self.Dplayed = True
        
    def check_hand_result(self, is_main_hand = True) -> int:
        '''
        checks if a hand won or lost.
        return values:
        0 - still not finished playing the hand
        1 - hand won
        2 - hand lost
        3 - draw
        '''
        checkBust = self.PCheckBust if is_main_hand else self.P2CheckBust #choose pointer to the correct check bust
        checkBJ = self.PCheckBJ if is_main_hand else self.P2CheckBJ #choose pointer to the correct check BJ
        get_sum = self.state.get_p_sum if is_main_hand else self.state.get_p2_sum

        # print('check bust: ', checkBust)
        if checkBust(): #player busts
            # print('hooray')
            return 2
        
        if not self.Dplayed: #dealer didnt make a move
            return 0
        
        if self.DCheckBust(): #dealer busted
            return 1
        
        #handle win / lose by sum
        p_sum = get_sum()
        d_sum = self.get_d_sum()

        if p_sum > d_sum: #player won by sum
            return 1
        
        if d_sum > p_sum: #dealer won by sum
            return 2
        
        #handle draw / win by BlackJack
        pBJ = checkBJ()
        dBJ = self.DCheckBJ()
        if (pBJ and dBJ) or (not pBJ and not dBJ): #if draw (push) - no one / both have BlackJack and the same sum
            return 3
        
        return 1 if pBJ else 2 #if someone has a BJ, he is the winner

    def update_end_game(self, is_main_hand:bool, result :int):
        '''
        updates the balance according to the game results
        '''

        checkBJ = self.PCheckBJ if is_main_hand else self.P2CheckBJ #choose pointer to the correct check bust
        bet = self.state.bet_val if is_main_hand else self.state.bet2_val
        pBJ = checkBJ()
        match result:
            case 1:
                self.state.balance += int(bet * (1 if not pBJ else 1.5))
            case 2:
                self.state.balance -= min(bet, self.state.balance)

    def CheckEnd(self, G: Graphics = None, force_split = False):
        '''
        checks for game end.
        return values:
        0 - game doesn't end
        1 - player won (if split, it means he won both games)
        2 - dealer won (if split, it means he won both games)
        3 - draw (if split, it means draw in both games)
        only split return values:
        4 - player won main hand, dealer won second hand
        5 - dealer won main hand, player won second hand
        6 - draw on main hand, player won second hand
        7 - draw on main hand, dealer won second hand
        8 - player won main hand, draw on the second hand
        9 - dealer won main hand, draw on the second hand
        '''

        main_hand_result = self.check_hand_result(True) #the first hand results

        #if not finished game on main hand
        if main_hand_result == 0:
            return 0

        #if split exists and the second hand hasn't been activated yet
        if self.splitted and not self.state.second_hand_active:
            self.state.second_hand_active = True #activate second hand
            if G != None:
                G.bet.set_value(self.state.bet2_val) #set the bet slider to second bet
            return 0 #wait for second hand to be played

        #the second hand results, if exists. if didnt exist will be 4 so wont confuse with any known return code.
        second_hand_result = self.check_hand_result(False) if self.splitted else 4

        #if not finished game on second hand
        if self.splitted and second_hand_result == 0:
            return 0

        #if dealer hasn't played yet, make the dealer play before evaluating result
        if not self.Dplayed:
            self.Dplay(G) #dealer plays until at least 17 or busts
            #recalculate the results after dealer finished
            main_hand_result = self.check_hand_result(True)
            second_hand_result = self.check_hand_result(False) if self.splitted else 4

        # Combine results into return codes
        result_map = {
            (1, 4): 1,   # player won both hands
            (2, 4): 2,   # dealer won both hands
            (3, 4): 3,   # draw on both hands
            (1, 1): 1,   # player won both hands
            (2, 2): 2,   # dealer won both hands
            (3, 3): 3,   # draw on both hands
            (1, 2): 4,   # player won main, dealer won second
            (2, 1): 5,   # dealer won main, player won second
            (3, 1): 6,   # draw main, player won second
            (3, 2): 7,   # draw main, dealer won second
            (1, 3): 8,   # player won main, draw second
            (2, 3): 9    # dealer won main, draw second
        }

        combined_result = result_map.get((main_hand_result, second_hand_result), 0) #the result from the dictionary

        self.update_end_game(True, main_hand_result) #update balance for the main hand
        if self.splitted:
            self.update_end_game(False, second_hand_result) #update balance for second hand if exists

        self.start(G, force_split) #reset environment for new round

        return combined_result #return the appropriate result code