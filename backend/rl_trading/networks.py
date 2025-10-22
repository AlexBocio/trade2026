# networks.py - Neural network architectures for RL

import torch
import torch.nn as nn
import torch.nn.functional as F

class QNetwork(nn.Module):
    """
    Q-Network for DQN.
    Maps state -> Q-values for each action.
    """

    def __init__(self, state_dim, action_dim, hidden_dims=[256, 256]):
        super(QNetwork, self).__init__()

        layers = []
        input_dim = state_dim

        for hidden_dim in hidden_dims:
            layers.append(nn.Linear(input_dim, hidden_dim))
            layers.append(nn.ReLU())
            input_dim = hidden_dim

        layers.append(nn.Linear(input_dim, action_dim))

        self.network = nn.Sequential(*layers)

    def forward(self, state):
        return self.network(state)


class ActorNetwork(nn.Module):
    """
    Actor Network for policy gradient methods (PPO, SAC).
    Maps state -> action probabilities or continuous action.
    """

    def __init__(self, state_dim, action_dim, hidden_dims=[256, 256], continuous=False):
        super(ActorNetwork, self).__init__()

        self.continuous = continuous

        layers = []
        input_dim = state_dim

        for hidden_dim in hidden_dims:
            layers.append(nn.Linear(input_dim, hidden_dim))
            layers.append(nn.ReLU())
            input_dim = hidden_dim

        self.shared = nn.Sequential(*layers)

        if continuous:
            # Output mean and log_std for continuous actions
            self.mean = nn.Linear(input_dim, action_dim)
            self.log_std = nn.Linear(input_dim, action_dim)
        else:
            # Output action probabilities for discrete actions
            self.action_head = nn.Linear(input_dim, action_dim)

    def forward(self, state):
        shared = self.shared(state)

        if self.continuous:
            mean = self.mean(shared)
            log_std = self.log_std(shared)
            log_std = torch.clamp(log_std, min=-20, max=2)
            return mean, log_std
        else:
            action_probs = F.softmax(self.action_head(shared), dim=-1)
            return action_probs


class CriticNetwork(nn.Module):
    """
    Critic Network for actor-critic methods.
    Maps state -> value estimate.
    """

    def __init__(self, state_dim, hidden_dims=[256, 256]):
        super(CriticNetwork, self).__init__()

        layers = []
        input_dim = state_dim

        for hidden_dim in hidden_dims:
            layers.append(nn.Linear(input_dim, hidden_dim))
            layers.append(nn.ReLU())
            input_dim = hidden_dim

        layers.append(nn.Linear(input_dim, 1))

        self.network = nn.Sequential(*layers)

    def forward(self, state):
        return self.network(state)


class DuelingQNetwork(nn.Module):
    """
    Dueling Q-Network architecture.
    Separates value and advantage streams.
    """

    def __init__(self, state_dim, action_dim, hidden_dims=[256, 256]):
        super(DuelingQNetwork, self).__init__()

        # Shared feature extractor
        layers = []
        input_dim = state_dim

        for hidden_dim in hidden_dims[:-1]:
            layers.append(nn.Linear(input_dim, hidden_dim))
            layers.append(nn.ReLU())
            input_dim = hidden_dim

        self.features = nn.Sequential(*layers)

        # Value stream
        self.value_stream = nn.Sequential(
            nn.Linear(input_dim, hidden_dims[-1]),
            nn.ReLU(),
            nn.Linear(hidden_dims[-1], 1)
        )

        # Advantage stream
        self.advantage_stream = nn.Sequential(
            nn.Linear(input_dim, hidden_dims[-1]),
            nn.ReLU(),
            nn.Linear(hidden_dims[-1], action_dim)
        )

    def forward(self, state):
        features = self.features(state)
        value = self.value_stream(features)
        advantages = self.advantage_stream(features)

        # Combine value and advantages
        q_values = value + (advantages - advantages.mean(dim=-1, keepdim=True))

        return q_values
