from card import Card
import random

class Deck:
    '''
    A class that represents a deck of playing cards.

    Attributes:
    cards - a list of card objects
    '''
    
    def __init__(self):
        '''
        initialize a new Deck with all the cards (no Joker of course)
        '''
        #Define the suits and values
        suits = ['hearts', 'diamonds', 'clubs', 'spades']
        values = [2, 3, 4, 5, 6, 7, 8, 9, 10, 'jack', 'queen', 'king', 'ace']
        #Create the deck as a list of Card objects
        self.cards = [Card(value, suit) for suit in suits for value in values]
        random.shuffle(self.cards) #shuffle the deck
    
    def get_card(self) -> Card:
        '''
        get a random card from the deck
        the deck is shuffled, get a card and remove it from the deck.
        '''
        # card = random.choice(self.cards) #choose a random card
        # self.cards.remove(card) #remove it from the deck so won't appear twice
        # return card
        return self.cards.pop() if self.cards else None
    
    def get_specific(self, value) -> Card:
        '''
        get a specific card value from the deck
        '''
        tens = ['jack', 'queen', 'king']
        for card in self.cards:
            if card.value == value or (card.value in tens and value == 10) or (card.value == 'ace' and (value == 11 or value == 1)):
                self.cards.remove(card)
                return card
        return None