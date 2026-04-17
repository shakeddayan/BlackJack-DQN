
import torch
import random
import math
from DQN import DQN


epsilon_start, epsilon_final, epsilon_decay = 1, 0.01, 200000


class DQN_Agent_min:
    def __init__(self, parametes_path = None, train = True, env= None, device = torch.device('cpu')):
        self.C0 = 0
        self.C1 = 0
        self.C2 = 0
        self.C3 = 0
        self.C4 = 0
        self.rando = 0
        self.DQN = DQN(device=device)
        if parametes_path:
            self.DQN.load_params(parametes_path)
        self.train = train
        self.setTrainMode()

    def setTrainMode (self):
        if self.train:
            self.DQN.train()
        else:
            self.DQN.eval()

    def get_Action (self, state, epoch = 0, start_epoch = 0, has_split = False, events= None, train = True):
        actions = [0,1,3,4] #no bet & no spilt
        if self.train and train:
            epsilon = self.epsilon_greedy(epoch - start_epoch)
            rnd = random.random()
            if rnd < epsilon:
                self.rando += 1
                randy =  random.choice(actions)
                if randy == 0:
                    self.C0 += 1
                if randy == 1:
                    self.C1 += 1
                if randy == 2:
                    self.C2 += 1
                if randy == 3:
                    self.C3 += 1
                if randy == 4:
                    self.C4 += 1
                return randy
        with torch.no_grad():
            Q_values = self.DQN(state)
            Q_values[2] = -float('inf') # masking - making the split non-playable
            if has_split:
                Q_values[4] = -float('inf') # masking - making the surrender non-playable if splitted, as it is not permitted.
            
            max_index = torch.argmax(Q_values)
        return int(max_index.item())

    def get_Actions_Values (self, states):
        with torch.no_grad():
            Q_values = self.DQN(states)
            max_values, max_indices = torch.max(Q_values,dim=1) # best_values, best_actions
        
        return max_indices.reshape(-1,1), max_values.reshape(-1,1)

    def Q (self, states, actions):
        Q_values = self.DQN(states) # try: Q_values = self.DQN(states).gather(dim=1, actions) ; check if shape of actions is [-1, 1] otherwise dim=0
        rows = torch.arange(Q_values.shape[0]).reshape(-1,1)
        cols = actions.reshape(-1,1)
        return Q_values[rows, cols]

    def epsilon_greedy(self,epoch, start = epsilon_start, final=epsilon_final, decay=epsilon_decay):
        return final + (start - final) * math.exp(-1 * epoch/decay)
        # if epoch < decay:
        #     return start - (start - final) * epoch/decay
        # return final
        
    def loadModel (self, file):
        self.model = torch.load(file)
    
    def save_param (self, path):
        self.DQN.save_params(path)

    def load_params (self, path):
        self.DQN.load_params(path)

    def fix_update (self, dqn, tau=0.001):
        self.DQN.load_state_dict(dqn.state_dict())

    def soft_update (self, dqn, tau=0.001):
        with torch.no_grad():
            for dqn_hat_param, dqn_param in zip(self.DQN.parameters(), dqn.parameters()):
                dqn_hat_param.data.copy_(tau * dqn_param.data + (1.0 - tau) * dqn_hat_param.data)


    def __call__(self, events= None, state=None):
        return self.get_Action(state)
