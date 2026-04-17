import torch
import torch.nn as nn
import torch.nn.functional as F
import copy

# Parameters
input_size = 3 # State dimension: [sum, has_ace, dealer_card]
layer1 = 64
# layer2 = 256
# layer3 = 512
# layer3 = 128
layer2 = 64
output_size = 5 # Q(state) -> hit? double? split = 0 stand? surrender?
gamma = 0.99 


class DQN (nn.Module):
    def __init__(self,layer1 = layer1, layer2 = layer2, input_size = input_size, output_size = output_size, device = torch.device('cpu')) -> None:
        super().__init__()
        self.device = device
        self.linear1 = nn.Linear(input_size, layer1)
        self.linear2 = nn.Linear(layer1, layer2)
        # self.linear3 = nn.Linear(layer2, layer3)
        # self.linear4 = nn.Linear(layer3, layer4)
        # self.linear5 = nn.Linear(layer4, layer5)
        self.output = nn.Linear(layer2, output_size)
        self.MSELoss = nn.MSELoss()

    def forward (self, x):
        x = self.linear1(x)
        x = F.leaky_relu(x)
        x = self.linear2(x)
        x = F.leaky_relu(x)
        # x = self.linear3(x)
        # x = F.leaky_relu(x)
        # x = self.linear4(x)
        # x = F.leaky_relu(x)
        # x = self.linear5(x)
        # x = F.leaky_relu(x)
        x = self.output(x)
        return x

    def loss (self, Q_values, rewards, Q_next_Values, dones ):
        Q_new = rewards.to(self.device) + gamma * Q_next_Values * (1- dones.to(self.device))
        return self.MSELoss(Q_values, Q_new)
    
    def load_params(self, path):
        self.load_state_dict(torch.load(path, weights_only=True))

    def save_params(self, path):
        torch.save(self.state_dict(), path)

    def copy (self):
        return copy.deepcopy(self)