
import torch
import random
import math
from DQN import DQN
from DQN_Agent_min import DQN_Agent_min
from Split_Agent import Split_Agent
from env import Env


epsilon_start, epsilon_final, epsiln_decay = 1, 0.01, 5000


class DQN_Agent:
    def __init__(self, min_parametes_path = None, split_parameters_path = None, train = False, env= None, device = torch.device('cpu')):
        self.min_agent = DQN_Agent_min(min_parametes_path, train= train, device= device)
        self.split_agent = Split_Agent(split_parameters_path, train= train, device=device)

    def get_Action (self, env:Env, epoch = 0, events= None, train = False):
        action = None
        if train == False: #handle train == true later if needed.
            if env.state.round_phase == 'playing':
                split_legal = env.is_action_legal(2)
                if split_legal: #if can split.
                    # make a decision: 1-split, 0-do something else.
                    decision = self.split_agent.get_Action(env.state.get_state_split(), epoch=epoch, train=False)
                    if decision == 1:
                        action = 2
                
                if action != 2:
                    min_state = env.state.get_state_AI() #needs a different format
                    action = self.min_agent.get_Action(min_state, has_split=env.splitted, train=False)
            else:
                action = 16 #always bet 2%
        return action