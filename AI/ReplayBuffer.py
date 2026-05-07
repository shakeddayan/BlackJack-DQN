from collections import deque
import random
import torch
import numpy as np

capacity = 500000

class ReplayBuffer: # a class meant to represent the replay buffer. will be used for both models (min and split).
    def __init__(self, capacity= capacity, path = None) -> None:
        '''
        create a new replay buffer or load an existing one.
        '''
        if path:
            self.buffer = torch.load(path).buffer
        else:
            self.buffer = deque(maxlen=capacity)

    def push (self, state , action, reward, next_state, done): #add a new (s,a,r,s') group to the buffer for the min model
        self.buffer.append((state, action, reward, next_state, done))
    
    def push_split (self, state , action, reward): # add a new (s,a,r) group for split model - all states are terminal for the model.
        self.buffer.append((state, action, reward))
    
    def sample (self, batch_size): #get a random batch_size sized sample from the buffer for min model
        if (batch_size > self.__len__()):
            batch_size = self.__len__()
        state_tensors, action_tensor, reward_tensors, next_state_tensors, dones_tensor = zip(*random.sample(self.buffer, batch_size))
        states = torch.vstack(state_tensors)
        actions= torch.vstack(action_tensor)
        rewards = torch.vstack(reward_tensors)
        next_states = torch.vstack(next_state_tensors)
        dones = torch.vstack(dones_tensor)
        return states, actions, rewards, next_states, dones
    
    def sample_split (self, batch_size): #get a random batch_size sized sample from the buffer for split model
        if (batch_size > self.__len__()):
            batch_size = self.__len__()
        state_tensors, action_tensor, reward_tensors = zip(*random.sample(self.buffer, batch_size))
        states = torch.vstack(state_tensors)
        actions= torch.vstack(action_tensor)
        rewards = torch.vstack(reward_tensors)
        return states, actions, rewards

    def __len__(self): #get the len of the buffer
        return len(self.buffer)