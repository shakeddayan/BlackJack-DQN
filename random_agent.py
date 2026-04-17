import random
from env import Env


class Random_Agent:
    '''
    A class that represents a Random agent
    '''

    #get an action and run it
    def get_Action(self, event = None, env:Env = None, graphics = None, epoch = None, train = None):
        
        if env.state.round_phase == 'betting':
            # env.state.round_phase == 'playing'
            return random.randint(5, 16)
        else:
            return random.randint(0, 4)