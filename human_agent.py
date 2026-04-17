import pygame
from graphics import Graphics
from env import Env

class Human_Agent:
    '''
    A class that represents a human agent
    '''

    #get an action and run it
    def get_action(self, event, env:Env, G:Graphics, state = None):
        '''
        get the player's next game action

        return values:
        0 - hit
        1 - double
        2 - split
        3 - stand
        4 - surrender
        5 - bet 0
        6 - bet 1/4
        7 - bet 1/2
        8 - bet 3/4
        9 - bet all in (all of the balance)
        '''
        
        if env.state.round_phase == 'betting':
            if G.bet.container_rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]: #if pressed somewhere on the slider
                G.bet.move_slider(pygame.mouse.get_pos()) #move the slider to press position
                #set the bets (only for the bet to render OK)
                env.state.bet_val = G.bet.get_value()
                env.state.bet2_val = G.bet.get_value()
            if G.lock.is_clicked(event):
                env.state.round_phase = 'playing' #end betting phase
                #return the action and confirm bet value once more.
                return 5 + G.bet.get_knob()
        else:
            #if hit
            if G.hit.is_clicked(event, G):
                return 0

            #if double
            if G.double.is_clicked(event, G):
                return 1

            #if split
            if G.split.is_clicked(event, G):
                return 2

            #if stand
            if G.stand.is_clicked(event, G):
                return 3

            #is surrender
            if G.surrender.is_clicked(event, G):
                return 4