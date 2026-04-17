import torch
from DQN import DQN
import random
import math


epsilon_start, epsilon_final, epsilon_decay = 1, 0.01, 500000

class Split_Agent:
    def __init__(self, parametes_path = None, train = True, device = torch.device('cpu')):
        self.DQN = DQN(layer1=16, layer2=32, input_size=2, output_size=2, device=device)
        if parametes_path:
            self.DQN.load_params(parametes_path)
        self.train = train
    
    def setTrainMode (self):
        if self.train:
            self.DQN.train()
        else:
            self.DQN.eval()

    def get_Action (self, state, epoch = 0, start_epoch = 0, events= None, train = True):
        actions = [0,1] #no bet & no spilt
        if self.train and train:
            epsilon = self.epsilon_greedy(epoch - start_epoch)
            rnd = random.random()
            if rnd < epsilon:
                return random.choice(actions)
        with torch.no_grad():
            Q_values = self.DQN(state)
            
        max_index = torch.argmax(Q_values)
        return int(max_index.item())
    
    def epsilon_greedy(self,epoch, start = epsilon_start, final=epsilon_final, decay=epsilon_decay):
        return final + (start - final) * math.exp(-1 * epoch/decay)
    
    def save_param (self, path):
        self.DQN.save_params(path)
    
    def __call__(self, events=None, state=None):
        return self.get_Action(state)