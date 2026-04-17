class Card:
    '''
    A class that represents a card in a deck.
    
    Attributes:
    value - the value of the card
    suit - the suit of the card
    img - path to an image of the card
    '''

    def __init__(self, value, suit):
        '''
        initialize a new card object
        '''
        self.value = value
        self.suit = suit
        #referencing the correct picture in the img folder using the card value and suit
        self.img = f'img\\PNG-cards-1.3\\{value}_of_{suit}{"" if isinstance(value, int) or value == "ace" else "2"}.png'