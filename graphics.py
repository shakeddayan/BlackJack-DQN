import pygame
import math
from screenObjects.button import Circle_Button, Rectangle_Button
from card import Card
from screenObjects.slider import Slider

pygame.init()

class Graphics:
    '''
    A class that represents the graphics module.

    Attributes:
    screen: main screen
    table_surf: green main table
    wood_surf: wood secondary surface
    shadow_surface: wood shadow
    hit: hit button
    double: double button
    split: split button
    stand: stand button
    surrender: surrender button
    lock: lock bet button
    p_hand: a list of graphic objects that represents the player's main hand
    p2_hand: a list of graphic objects that represents the player's secondary hand
    d_hand: a list of graphic objects that represents the dealer's hand
    p_turn: player's main hand turn counter
    p2_turn: player's second hand turn counter
    d_turn: dealer's hand turn counter
    '''
        
    def __init__(self, balance:int):
        '''
        initialize a new Graphics object.
        '''

        # CONSTANTS
        #the game screen
        self.SCREEN_HEIGHT = 1020
        self.SCREEN_WIDTH = 1920

        #deck
        self.DECK_HEIGHT = self.SCREEN_HEIGHT / 3
        self.DECK_WIDTH = 5*self.DECK_HEIGHT / 6  # original ratio is 500 * 600
        self.DECK_X = 5 * self.SCREEN_WIDTH / 6
        self.DECK_Y = 40

        #cards
        self.CARD_HEIGHT = 3 * self.DECK_HEIGHT / 4
        self.CARD_WIDTH = 5 * self.CARD_HEIGHT / 7.26 #original ratio is 500 * 726

        #card placements
        self.HAND_CARD_OFFSETS = 30
        self.PLAYER_X = self.SCREEN_WIDTH / 2 - self.CARD_WIDTH / 2
        self.PLAYER_X_SPLITTED = self.SCREEN_WIDTH / 3 - self.CARD_WIDTH / 2
        self.PLAYER2_X = 2 * self.SCREEN_WIDTH / 3 - self.CARD_WIDTH / 2
        self.PLAYER_Y = 3 *self.SCREEN_HEIGHT / 5 - self.CARD_HEIGHT / 2 - 20
        self.DEALER_X = self.SCREEN_WIDTH / 2 - self.CARD_WIDTH / 2 + 50
        self.DEALER_Y = self.SCREEN_HEIGHT / 4 - self.CARD_HEIGHT / 2 - 40

        #chips placement
        self.CHIP_HEIGHT = 125
        self.CHIP_WIDTH = 466 * self.CHIP_HEIGHT / 580 #ORIGINAL RATIO: 466 * 580
        self.CHIPS_OFFSET_X = 75
        self.CHIPS_OFFSET_STACK = 5
        self.CHIPS_START_X = 10
        self.CHIPS_START_Y = self.SCREEN_HEIGHT - 1.5 * self.CHIPS_OFFSET_X
        self.RED_CHIPS_X = self.CHIPS_START_X
        self.BLUE_CHIPS_X = self.RED_CHIPS_X + self.CHIPS_OFFSET_X
        self.GREEN_CHIPS_X = self.BLUE_CHIPS_X + self.CHIPS_OFFSET_X
        self.YELLOW_CHIPS_X = self.RED_CHIPS_X
        self.PINK_CHIPS_X = self.BLUE_CHIPS_X
        self.BLACK_CHIPS_X = self.GREEN_CHIPS_X

        self.RED_CHIPS_Y = self.CHIPS_START_Y
        self.BLUE_CHIPS_Y = self.RED_CHIPS_Y
        self.GREEN_CHIPS_Y = self.BLUE_CHIPS_Y
        self.YELLOW_CHIPS_Y = self.RED_CHIPS_Y - self.CHIPS_OFFSET_X
        self.PINK_CHIPS_Y = self.BLUE_CHIPS_Y - self.CHIPS_OFFSET_X
        self.BLACK_CHIPS_Y = self.GREEN_CHIPS_Y - self.CHIPS_OFFSET_X

        #bet slider
        self.BET_POS = (425, self.SCREEN_HEIGHT - 50)
        self.BET_DIM = (300,20)
        
        #colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.LIGHT_GREEN = (0, 240, 0)
        self.DARK_GREEN = (0, 100, 0)
        self.ORANGE = (237, 160, 36)
        self.LIGHT_BLUE = (27, 180, 222)
        self.LIGHT_PINK = (212, 76, 191)
        self.PINK = (255, 20, 192)
        self.PASTEL_RED = (199, 34, 83)
        self.RED = (201, 10, 36)
        self.YELLOW = (227, 227, 39)
        self.GRAY = (107, 107, 107)
        self.LIGHT_GRAY = (199, 199, 199)
        self.GOLD = (255, 215, 0)

        #endgame picture location
        self.ENDGAME_LOCATION = (self.SCREEN_WIDTH / 2 - 300, self.SCREEN_HEIGHT / 2 - 200)
        self.ENDGAME_LOCATION1 = (self.ENDGAME_LOCATION[0] / 2, self.ENDGAME_LOCATION[1])
        self.ENDGAME_LOCATION2 = (3 * self.ENDGAME_LOCATION[0] / 2, self.ENDGAME_LOCATION[1])

        #money font
        self.MONEY_FONT = pygame.font.Font("fonts\\jqkas-wild-font\\JqkasWild-w1YD6.ttf", 50)

        #GRAPHIC OBJECTS
        #surfaces
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT)) #initialize screen
        pygame.display.set_caption('BlackJack') #title
        self.table_surf = self.create_gradient_surface(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, self.DARK_GREEN, self.LIGHT_GREEN) #background
        self.wood_surf = pygame.transform.scale(pygame.image.load('img/wood.png'), (self.SCREEN_WIDTH, 200)) #wood surface
        self.shadow_surface = pygame.Surface((self.SCREEN_WIDTH, 200), pygame.SRCALPHA)
        self.shadow_surface.fill((50, 50, 50, 100))  # (R, self, B, A) with alpha for transparency

        #buttons
        self.hit = Circle_Button('HIT', 'img/moves/hit.png', color= self.ORANGE, pos=(self.SCREEN_WIDTH - 880, self.wood_surf.get_height() / 2), G=self) #the hit button
        self.double = Circle_Button('DOUBLE ', 'img/moves/double.png', color= self.LIGHT_BLUE, pos = (self.SCREEN_WIDTH - 690, self.wood_surf.get_height() / 2), G=self) #the double button
        self.split = Circle_Button('SPLIT ', 'img/moves/split.png', color = self.YELLOW, pos= (self.SCREEN_WIDTH - 500, self.wood_surf.get_height() / 2), G=self) #the split button
        self.stand = Circle_Button('STAND ', 'img/moves/stand.png', color = self.RED, pos= (self.SCREEN_WIDTH - 310, self.wood_surf.get_height() / 2), G=self) #the stand button
        self.surrender = Circle_Button('SURRENDER', 'img/moves/surrender.png', color= self.BLACK, pos= (self.SCREEN_WIDTH - 120, self.wood_surf.get_height() / 2), G=self) #the surrender button
        self.lock = Rectangle_Button(text='lock bet', img='img/moves/lock.webp', pos=(self.BET_POS[0] + (self.BET_DIM[0] // 2) + 10, self.BET_POS[1] - self.BET_DIM[1]), dimentions= ((self.BET_DIM[0] - 100) / 2 + 20, 2 * self.BET_DIM[1]), G=self) #the lock bet button

        #slider
        self.bet = Slider(self.BET_POS, self.BET_DIM, 0, 0, balance) #a slider holding the bet.
        
        #CHANGING VALUES
        self.p_hand = [] #player's main hand card graphics
        self.p2_hand = [] #player's second hand card graphics
        self.d_hand = [] #dealer's hand card graphics
        self.p_turn: int = 1 #player's main hand turn counter
        self.p2_turn: int = 1 #player's second hand turn counter
        self.d_turn: int = 1 #dealer's hand turn counter

    #GRAPHICS FUNCTIONS
    def render_screen(self, env):
        '''
        render the screen and all objects that appear visually
        '''
        
        #print the table again
        self.screen.blit(self.table_surf, (0, 0)) #reload screen
        self.screen.blit(self.shadow_surface, (0, self.SCREEN_HEIGHT - 205)) #reload wood shadow
        self.screen.blit(self.wood_surf, (0, self.SCREEN_HEIGHT - 200)) #reload wood
        self.load_deck(self.screen) #reload deck

        #draw all cards in player's hand
        self.draw_cards(self.screen, env)

        #update balance
        balance_txt = self.MONEY_FONT.render(f' Balance : {env.state.balance}$ ', True, self.BLACK, self.WHITE,) #render font
        balance_text_rect = balance_txt.get_rect() #create rectangle
        self.screen.blit(balance_txt, (10, 10),  balance_text_rect) # update balance

        #draw bet slider
        self.bet.max = env.state.balance
        #choose the active hand's bet
        self.bet.set_value(env.state.bet_val if not env.state.second_hand_active else env.state.bet2_val)
        self.bet.render(self, env.state.bet_val if not env.state.second_hand_active else env.state.bet2_val)

        #load the chips
        self.load_chips(self.screen, self.bet.get_value())

        #reload buttons
        self.hit(env, self)
        self.double.lock_double(env, self)
        self.double(env, self)
        self.split.lock_split(env, self)
        self.split(env, self)
        self.stand(env, self)
        self.surrender(env, self)
        self.lock(env, self)

    def create_gradient_surface(self, width, height, color_start, color_end):
        '''
        creates a gradient background with the given colors.
        '''

        # Create a new surface
        gradient_surface = pygame.Surface((width, height))
        
        # Draw the gradient onto the surface
        for y in range(height):
            # Interpolate the color for each row
            ratio = y / height
            r = int(color_start[0] + (color_end[0] - color_start[0]) * ratio)
            g = int(color_start[1] + (color_end[1] - color_start[1]) * ratio)
            b = int(color_start[2] + (color_end[2] - color_start[2]) * ratio)
            
            color = pygame.Color(r, g, b)
            pygame.draw.line(gradient_surface, color, (0, y), (width, y))
        
        return gradient_surface

    def load_deck(self, screen):
        '''
        renders the deck on the screen
        '''

        card_back_img = pygame.transform.scale(pygame.image.load('img\\cardBack.webp'), (self.DECK_WIDTH, self.DECK_HEIGHT))
        OFFSET = 5
        screen.blit(card_back_img, (self.DECK_X, self.DECK_Y))
        screen.blit(card_back_img, (self.DECK_X - OFFSET, self.DECK_Y))
        screen.blit(card_back_img, (self.DECK_X - 2*OFFSET, self.DECK_Y))

    def load_card(self, card:Card, hand_to_add, env):
        '''
        loads a card into any hand graphically, and adds the value to the corresponding value list
        '''

        card_img = pygame.transform.scale(pygame.image.load(card.img), (self.CARD_WIDTH, self.CARD_HEIGHT))
        card_pos = ((self.PLAYER_X if not env.splitted else self.PLAYER_X_SPLITTED) + self.p_turn * self.HAND_CARD_OFFSETS - self.CARD_WIDTH / 2 ,self.PLAYER_Y) if hand_to_add == 'player' else (self.DEALER_X + self.d_turn * self.HAND_CARD_OFFSETS - self.CARD_WIDTH / 2, self.DEALER_Y) if hand_to_add == 'dealer' else (self.PLAYER2_X + self.p2_turn * self.HAND_CARD_OFFSETS - self.CARD_WIDTH / 2 ,self.PLAYER_Y)
        hand = self.p_hand if hand_to_add =='player' else self.d_hand if hand_to_add == 'dealer' else self.p2_hand
        hand_vals = env.state.p_hand_vals if hand_to_add =='player' else env.d_hand_vals if hand_to_add == 'dealer' else env.state.p2_hand_vals
        # hand_vals.append(card.value if isinstance(card.value, int) else (10 if card.value != 'ace' else 11))
        env.append_hand(card.value if isinstance(card.value, int) else (10 if card.value != 'ace' else 11), hand_vals)
        
        #calculate printing positions for each card in the hand
        for i in range(len(hand)):
            hand[i] = (hand[i][0], (hand[i][1][0] - self.HAND_CARD_OFFSETS, hand[i][1][1]))
        hand.append((card_img, card_pos))
        return (card_img, card_pos)

    def load_chips(self, screen, bet):
        '''
        loads the chips dynamically according to the given argument
        '''
        BLACK = 100000
        PINK = 10000
        YELLOW = 1000
        GREEN = 100
        BLUE = 10
        RED = 1
        SHADOW = pygame.transform.scale(pygame.image.load('img\\chips\\shadow.png'), (self.CHIP_WIDTH, self.CHIP_HEIGHT))
        #black
        if bet / BLACK >= 1:
            path = 'img\\chips\\black.png'
            #add shadow to stack
            screen.blit(SHADOW, (self.BLACK_CHIPS_X, self.BLACK_CHIPS_Y + 1.5 * self.CHIPS_OFFSET_STACK))
            for i in range(math.floor(bet // BLACK)):
                screen.blit(pygame.transform.scale(pygame.image.load(path), (self.CHIP_WIDTH, self.CHIP_HEIGHT)), (self.BLACK_CHIPS_X, self.BLACK_CHIPS_Y - i * self.CHIPS_OFFSET_STACK))
            bet %= BLACK
        
        #pink
        if bet / PINK >= 1:
            path = 'img\\chips\\pink.png'
            #add shadow to stack
            screen.blit(SHADOW, (self.PINK_CHIPS_X, self.PINK_CHIPS_Y + 1.5 * self.CHIPS_OFFSET_STACK))
            for i in range(math.floor(bet // PINK)):
                screen.blit(pygame.transform.scale(pygame.image.load(path), (self.CHIP_WIDTH, self.CHIP_HEIGHT)), (self.PINK_CHIPS_X, self.PINK_CHIPS_Y - i * self.CHIPS_OFFSET_STACK))
            bet %= PINK
        
        #yellow
        if bet / YELLOW >= 1:
            path = 'img\\chips\\yellow.png'
            #add shadow to stack
            screen.blit(SHADOW, (self.YELLOW_CHIPS_X, self.YELLOW_CHIPS_Y + 1.5 * self.CHIPS_OFFSET_STACK))
            for i in range(math.floor(bet // YELLOW)):
                screen.blit(pygame.transform.scale(pygame.image.load(path), (self.CHIP_WIDTH, self.CHIP_HEIGHT)), (self.YELLOW_CHIPS_X, self.YELLOW_CHIPS_Y - i * self.CHIPS_OFFSET_STACK))
            bet %= YELLOW
        
        #green
        if bet / GREEN >= 1:
            path = 'img\\chips\\green.png'
            #add shadow to stack
            screen.blit(SHADOW, (self.GREEN_CHIPS_X, self.GREEN_CHIPS_Y + 1.5 * self.CHIPS_OFFSET_STACK))
            for i in range(math.floor(bet // GREEN)):
                screen.blit(pygame.transform.scale(pygame.image.load(path), (self.CHIP_WIDTH, self.CHIP_HEIGHT)), (self.GREEN_CHIPS_X, self.GREEN_CHIPS_Y - i * self.CHIPS_OFFSET_STACK))
            bet %= GREEN
        
        #blue
        if bet / BLUE >= 1:
            path = 'img\\chips\\blue.png'
            #add shadow to stack
            screen.blit(SHADOW, (self.BLUE_CHIPS_X, self.BLUE_CHIPS_Y + 1.5 * self.CHIPS_OFFSET_STACK))
            for i in range(math.floor(bet // BLUE)):
                screen.blit(pygame.transform.scale(pygame.image.load(path), (self.CHIP_WIDTH, self.CHIP_HEIGHT)), (self.BLUE_CHIPS_X, self.BLUE_CHIPS_Y - i * self.CHIPS_OFFSET_STACK))
            bet %= BLUE
        
        #red
        if bet / RED >= 1:
            path = 'img\\chips\\red.png'
            #add shadow to stack
            screen.blit(SHADOW, (self.RED_CHIPS_X, self.RED_CHIPS_Y + 1.5 * self.CHIPS_OFFSET_STACK))
            for i in range(math.floor(bet // RED)):
                screen.blit(pygame.transform.scale(pygame.image.load(path), (self.CHIP_WIDTH, self.CHIP_HEIGHT)), (self.RED_CHIPS_X, self.RED_CHIPS_Y - i * self.CHIPS_OFFSET_STACK))
        
    def draw_cards(self, screen:pygame.Surface, env):
        '''
        draw all playing hands - main, secondary (split), and dealer
        will draw the sum labels too
        '''

        #don't show cards in betting phase
        if env.state.round_phase == 'playing':
                
                #print main hand
                for card_img, card_pos in self.p_hand:
                    screen.blit(card_img, card_pos)
                
                #update player sum
                p_sum_txt = self.MONEY_FONT.render(f" {'you'  if not env.splitted else 'hand 1'}: {env.state.get_p_sum()} ", True, self.BLACK, self.WHITE if env.state.second_hand_active else self.YELLOW) #render font
                p_sum_text_rect = p_sum_txt.get_rect() #create rectangle
                #screen.blit(p_sum_txt, (SCREEN_WIDTH / 10, PLAYER_Y + CARD_HEIGHT / 2),  p_sum_text_rect) # update sum
                screen.blit(p_sum_txt, (self.PLAYER_X if not env.splitted else self.PLAYER_X_SPLITTED - p_sum_text_rect.width / 2, self.PLAYER_Y + 10 * self.CARD_HEIGHT / 9),  p_sum_text_rect) # update sum

                #print split hand
                if env.splitted:
                    for card_img, card_pos in self.p2_hand:
                        screen.blit(card_img, card_pos)
                
                    #update player sum
                    p2_sum_txt = self.MONEY_FONT.render(f' hand 2: {env.state.get_p2_sum()} ', True, self.BLACK, self.WHITE if not env.state.second_hand_active else self.YELLOW) #render font
                    p2_sum_text_rect = p2_sum_txt.get_rect() #create rectangle
                    screen.blit(p2_sum_txt, (self.PLAYER2_X - p_sum_text_rect.width / 2, self.PLAYER_Y + 10 * self.CARD_HEIGHT / 9),  p2_sum_text_rect) # update sum

        
                # Draw the cards in the dealer's hand
                if env.Dplayed:
                    for card_img, card_pos in self.d_hand:
                        screen.blit(card_img, card_pos)
                        pygame.display.update()
                        pygame.time.delay(1000)
                    
                    #show dealer sum
                    d_sum_txt = self.MONEY_FONT.render(f' dealer: {env.get_d_sum()} ', True, self.BLACK, self.WHITE) #render font
                    d_sum_text_rect = d_sum_txt.get_rect() #create rectangle
                    screen.blit(d_sum_txt, (self.SCREEN_WIDTH / 10, self.DEALER_Y + self.CARD_HEIGHT / 2),  d_sum_text_rect) # update sum
                else:
                    card_img = pygame.transform.scale(pygame.image.load('img\\cardBack_noshadow.png'), (1.5* self.CARD_WIDTH, 1.45* self.CARD_HEIGHT))
                    card_pos = self.d_hand[0][1]
                    card_pos = card_pos[0] - 0.55 * self.CARD_WIDTH, card_pos[1] - 0.21 * self.CARD_HEIGHT
                    screen.blit(card_img, card_pos)
                    card_img,card_pos = self.d_hand[0][0], self.d_hand[0][1]
                    screen.blit(card_img, card_pos)

    def end_pic(self, screen:pygame.Surface, env, force_split = False):
        '''
        load the correct end-game picture according to the result
        reminder for end-game results:
            non - split: will display one picture
            0 - game doesn't end
            1 - player won (if split, it means he won both games)
            2 - dealer won (if split, it means he won both games)
            3 - draw (if split, it means draw in both games)
            only split return values: will display 2 pictures
            4 - player won main hand, dealer won second hand
            5 - dealer won main hand, player won second hand
            6 - draw on main hand, player won second hand
            7 - draw on main hand, dealer won second hand
            8 - player won main hand, draw on the second hand
            9 - dealer won main hand, draw on the second hand 
        '''
        
        if env.checkend:
                check_end_status = env.CheckEnd(self, force_split= force_split)
                match check_end_status:
                    case 1: #player won (if split, it means he won both games)
                        screen.blit(pygame.image.load("img/endgame/youwin.webp"), self.ENDGAME_LOCATION)
                    case 2: #dealer won (if split, it means he won both games)
                        screen.blit(pygame.image.load("img/endgame/youlose.png"), self.ENDGAME_LOCATION)
                    case 3: #draw (if split, it means draw in both games)
                        screen.blit(pygame.image.load("img/endgame/draw.png"), self.ENDGAME_LOCATION)
                    case 4: #player won main hand, dealer won second hand
                        screen.blit(pygame.image.load("img/endgame/youwin.webp"), self.ENDGAME_LOCATION1)
                        screen.blit(pygame.image.load("img/endgame/youlose.png"), self.ENDGAME_LOCATION2)
                    case 5: #dealer won main hand, player won second hand
                        screen.blit(pygame.image.load("img/endgame/youlose.png"), self.ENDGAME_LOCATION1)
                        screen.blit(pygame.image.load("img/endgame/youwin.webp"), self.ENDGAME_LOCATION2)
                    case 6: #draw on main hand, player won second hand
                        screen.blit(pygame.image.load("img/endgame/draw.png"), self.ENDGAME_LOCATION1)
                        screen.blit(pygame.image.load("img/endgame/youwin.webp"), self.ENDGAME_LOCATION2)
                    case 7: #draw on main hand, dealer won second hand
                        screen.blit(pygame.image.load("img/endgame/draw.png"), self.ENDGAME_LOCATION1)
                        screen.blit(pygame.image.load("img/endgame/youlose.png"), self.ENDGAME_LOCATION2)
                    case 8: #player won main hand, draw on the second hand
                        screen.blit(pygame.image.load("img/endgame/youwin.webp"), self.ENDGAME_LOCATION1)
                        screen.blit(pygame.image.load("img/endgame/draw.png"), self.ENDGAME_LOCATION2)
                    case 9: #dealer won main hand, draw on the second hand 
                        screen.blit(pygame.image.load("img/endgame/youlose.png"), self.ENDGAME_LOCATION1)
                        screen.blit(pygame.image.load("img/endgame/draw.png"), self.ENDGAME_LOCATION2)
                
                if check_end_status != 0: #if displays a picture, wait a bit
                    pygame.display.update()
                    pygame.time.delay(3000)
                env.checkend = False #turn off checkend