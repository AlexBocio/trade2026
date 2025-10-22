# replay_buffer.py - Experience replay for RL agents

import numpy as np
from collections import deque
import random

class ReplayBuffer:
    """
    Experience Replay Buffer for off-policy RL algorithms.
    Stores transitions (state, action, reward, next_state, done).
    """

    def __init__(self, capacity=100000):
        """
        Args:
            capacity: Maximum number of transitions to store
        """
        self.buffer = deque(maxlen=capacity)
        self.capacity = capacity

    def push(self, state, action, reward, next_state, done):
        """Add a transition to the buffer."""
        self.buffer.append((state, action, reward, next_state, done))

    def sample(self, batch_size):
        """
        Sample a random batch of transitions.

        Returns:
            Tuple of (states, actions, rewards, next_states, dones)
        """
        batch = random.sample(self.buffer, batch_size)

        states = np.array([t[0] for t in batch])
        actions = np.array([t[1] for t in batch])
        rewards = np.array([t[2] for t in batch])
        next_states = np.array([t[3] for t in batch])
        dones = np.array([t[4] for t in batch])

        return states, actions, rewards, next_states, dones

    def __len__(self):
        return len(self.buffer)

    def clear(self):
        """Clear the buffer."""
        self.buffer.clear()


class PrioritizedReplayBuffer:
    """
    Prioritized Experience Replay (PER).
    Samples transitions based on their TD error (priority).
    """

    def __init__(self, capacity=100000, alpha=0.6, beta=0.4):
        """
        Args:
            capacity: Maximum buffer size
            alpha: Prioritization exponent (0 = uniform sampling)
            beta: Importance sampling weight (increases to 1)
        """
        self.capacity = capacity
        self.alpha = alpha
        self.beta = beta
        self.buffer = []
        self.priorities = []
        self.position = 0

    def push(self, state, action, reward, next_state, done, td_error=1.0):
        """Add transition with priority."""
        max_priority = max(self.priorities) if self.priorities else 1.0

        if len(self.buffer) < self.capacity:
            self.buffer.append((state, action, reward, next_state, done))
            self.priorities.append(max_priority)
        else:
            self.buffer[self.position] = (state, action, reward, next_state, done)
            self.priorities[self.position] = max_priority

        self.position = (self.position + 1) % self.capacity

    def sample(self, batch_size):
        """Sample batch with prioritization."""
        priorities = np.array(self.priorities)
        probs = priorities ** self.alpha
        probs /= probs.sum()

        indices = np.random.choice(len(self.buffer), batch_size, p=probs)

        # Importance sampling weights
        weights = (len(self.buffer) * probs[indices]) ** (-self.beta)
        weights /= weights.max()

        batch = [self.buffer[i] for i in indices]

        states = np.array([t[0] for t in batch])
        actions = np.array([t[1] for t in batch])
        rewards = np.array([t[2] for t in batch])
        next_states = np.array([t[3] for t in batch])
        dones = np.array([t[4] for t in batch])

        return states, actions, rewards, next_states, dones, weights, indices

    def update_priorities(self, indices, td_errors):
        """Update priorities based on TD errors."""
        for idx, td_error in zip(indices, td_errors):
            self.priorities[idx] = abs(td_error) + 1e-6

    def __len__(self):
        return len(self.buffer)


class OfflineReplayBuffer:
    """
    Replay buffer for offline RL.
    Loads historical trading data and treats it as fixed dataset.
    """

    def __init__(self, historical_data):
        """
        Args:
            historical_data: DataFrame with columns [state, action, reward, next_state, done]
        """
        self.data = historical_data
        self.size = len(historical_data)

    def sample(self, batch_size):
        """Sample from historical data."""
        indices = np.random.choice(self.size, batch_size, replace=False)
        batch = self.data.iloc[indices]

        states = np.array(batch['state'].tolist())
        actions = np.array(batch['action'].tolist())
        rewards = np.array(batch['reward'].tolist())
        next_states = np.array(batch['next_state'].tolist())
        dones = np.array(batch['done'].tolist())

        return states, actions, rewards, next_states, dones

    def __len__(self):
        return self.size
