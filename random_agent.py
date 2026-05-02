import random
from env import Env


class Random_Agent:
    '''
    A class that represents a Random agent
    '''

    #get an action and run it
    def get_Action(self, env:Env = None, epoch=None, train=False):
        
        if env.state.round_phase == 'betting': #betting phase
            return random.randint(5, 16)
        else: #playing phase
            return random.randint(0, 4)