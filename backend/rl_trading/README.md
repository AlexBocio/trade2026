# Trade2025 Reinforcement Learning Trading System

Deep Reinforcement Learning framework for algorithmic trading with DQN and PPO agents.

## Features

### RL Algorithms
- **DQN (Deep Q-Network)** - Off-policy Q-learning with experience replay
- **PPO (Proximal Policy Optimization)** - On-policy actor-critic method
- **Experience Replay** - Standard and prioritized replay buffers
- **Target Networks** - Stabilized training for Q-learning
- **GAE (Generalized Advantage Estimation)** - Better advantage estimates for PPO

### Trading Environment
- Single-asset and multi-asset environments
- Technical indicators (SMA, RSI)
- Realistic transaction costs
- Portfolio tracking (cash, shares, portfolio value)
- Comprehensive state representation

### Neural Networks
- Q-Network for value-based methods
- Actor-Critic networks for policy gradient
- Dueling Q-Network architecture
- Flexible hidden layer configuration

## Quick Start

### 1. Setup Environment

```powershell
# Navigate to project
cd C:\trade2025\backend\rl_trading

# Create virtual environment
python -m venv venv

# Activate
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Server

```powershell
python app.py
```

Server runs on: **http://localhost:5002**

### 3. Train an Agent

```powershell
# Train DQN agent
curl -X POST http://localhost:5002/api/rl/train-dqn `
  -H "Content-Type: application/json" `
  -d '{
    "ticker": "AAPL",
    "episodes": 100,
    "agent_id": "aapl_dqn"
  }'
```

## API Endpoints

### Training

**POST /api/rl/train-dqn**
Train a DQN agent
```json
{
  "ticker": "AAPL",
  "episodes": 100,
  "agent_id": "my_dqn_agent"
}
```

**POST /api/rl/train-ppo**
Train a PPO agent
```json
{
  "ticker": "MSFT",
  "episodes": 100,
  "agent_id": "my_ppo_agent"
}
```

### Inference

**POST /api/rl/backtest**
Backtest a trained agent
```json
{
  "agent_id": "my_dqn_agent",
  "ticker": "AAPL",
  "agent_type": "dqn"
}
```

**POST /api/rl/get-action**
Get action recommendation
```json
{
  "agent_id": "my_dqn_agent",
  "state": [0.15, 0.02, 1.05, 1.1, 0.45, 0.5, 0.8, 1.05]
}
```

**GET /api/rl/list-agents**
List all trained agents

## Example Usage

### Python

```python
import requests

# Train DQN agent
response = requests.post('http://localhost:5002/api/rl/train-dqn', json={
    'ticker': 'AAPL',
    'episodes': 100,
    'agent_id': 'aapl_dqn_v1'
})

result = response.json()
print(f"Training complete: {result['agent_id']}")
print(f"Final reward: {result['final_reward']:.4f}")

# Backtest the agent
backtest = requests.post('http://localhost:5002/api/rl/backtest', json={
    'agent_id': 'aapl_dqn_v1',
    'ticker': 'AAPL',
    'agent_type': 'dqn'
})

bt_result = backtest.json()
print(f"Total return: {bt_result['total_return']:.2f}%")
print(f"Number of trades: {bt_result['num_trades']}")
```

### JavaScript/React

```javascript
const trainAgent = async () => {
  const response = await fetch('http://localhost:5002/api/rl/train-dqn', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      ticker: 'AAPL',
      episodes: 100,
      agent_id: 'aapl_dqn'
    })
  });

  const result = await response.json();
  console.log('Agent trained:', result);
  return result;
};

const getTradeSignal = async (agentId, state) => {
  const response = await fetch('http://localhost:5002/api/rl/get-action', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      agent_id: agentId,
      state: state
    })
  });

  const result = await response.json();
  return result.action; // 'BUY', 'SELL', or 'HOLD'
};
```

## Architecture

```
backend/rl_trading/
├── app.py              # Flask API server
├── agents.py           # DQN and PPO agents
├── environment.py      # Trading environments
├── networks.py         # Neural network architectures
├── replay_buffer.py    # Experience replay buffers
├── requirements.txt    # Dependencies
├── README.md          # This file
├── models/            # Saved agent models (created automatically)
└── venv/             # Virtual environment
```

## How It Works

### DQN Agent

1. **Observation**: Agent observes market state (prices, indicators, portfolio)
2. **Action Selection**: Epsilon-greedy policy (explore vs exploit)
3. **Experience Storage**: Store (state, action, reward, next_state) in replay buffer
4. **Training**: Sample random batches and minimize TD error
5. **Target Network**: Periodically update target Q-network for stability

### PPO Agent

1. **Rollout Collection**: Collect trajectories using current policy
2. **Advantage Estimation**: Compute GAE for better gradient estimates
3. **Policy Update**: Optimize clipped surrogate objective
4. **Value Update**: Train critic to predict state values
5. **Multiple Epochs**: Reuse data for multiple gradient steps

### Trading Environment

- **State**: [price, returns, SMA ratios, RSI, position, cash, portfolio value]
- **Actions**: 0=HOLD, 1=BUY (25% of cash), 2=SELL (all shares)
- **Rewards**: Change in portfolio value (normalized)
- **Episode**: Completes when reaching end of historical data

## Training Tips

### For DQN:
- Start with `epsilon=1.0` and decay to `0.01`
- Use replay buffer size of 100k+
- Update target network every 1000 steps
- Train for at least 100 episodes

### For PPO:
- Use GAE lambda around 0.95
- Clip epsilon around 0.2
- Train for 10 epochs per episode
- Learning rate around 3e-4

### General:
- Use at least 2 years of historical data
- Start with simple state representation
- Monitor training rewards over time
- Test on unseen data (different time periods)

## Model Persistence

Trained agents are automatically saved to `models/` directory:
- `models/my_agent.pth` - Model weights and optimizer state
- Load agents by `agent_id` via API
- Models include all training state (epsilon, step count, etc.)

## Performance Benchmarks

**Training Time** (100 episodes, single stock):
- DQN: ~5-10 minutes (CPU)
- PPO: ~3-7 minutes (CPU)

**Inference Speed**:
- Action selection: <1ms
- Backtest (500 steps): ~100ms

## Integration with Frontend

```javascript
// services/rlTrading.js
export const rlTradingAPI = {
  baseURL: 'http://localhost:5002/api/rl',

  async trainDQN(ticker, episodes = 100, agentId) {
    const response = await fetch(`${this.baseURL}/train-dqn`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ticker, episodes, agent_id: agentId })
    });
    return response.json();
  },

  async backtest(agentId, ticker, agentType = 'dqn') {
    const response = await fetch(`${this.baseURL}/backtest`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ agent_id: agentId, ticker, agent_type: agentType })
    });
    return response.json();
  },

  async getAction(agentId, state) {
    const response = await fetch(`${this.baseURL}/get-action`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ agent_id: agentId, state })
    });
    return response.json();
  },

  async listAgents() {
    const response = await fetch(`${this.baseURL}/list-agents`);
    return response.json();
  }
};
```

## Troubleshooting

### Torch Installation Issues
```powershell
pip install torch torchvision torchaudio
```

### Port Already in Use
Edit `app.py` line 234:
```python
app.run(host='0.0.0.0', port=5003, debug=True)  # Change to 5003
```

### Training Not Converging
- Increase number of episodes (200-500)
- Adjust learning rate (try 1e-3 or 3e-5)
- Normalize rewards
- Use longer historical data period

## Advanced Features

### Custom Environments
```python
from environment import TradingEnvironment

class MyCustomEnv(TradingEnvironment):
    def _get_state(self):
        # Custom state representation
        pass

    def step(self, action):
        # Custom reward function
        pass
```

### Hyperparameter Tuning
```python
# In agents.py
agent = DQNAgent(
    state_dim=8,
    action_dim=3,
    lr=1e-4,           # Learning rate
    gamma=0.99,        # Discount factor
    epsilon_start=1.0, # Initial exploration
    epsilon_end=0.01,  # Final exploration
    epsilon_decay=0.995 # Decay rate
)
```

## References

- [DQN Paper](https://arxiv.org/abs/1312.5602) - Mnih et al., 2013
- [PPO Paper](https://arxiv.org/abs/1707.06347) - Schulman et al., 2017
- [Stable-Baselines3](https://stable-baselines3.readthedocs.io/) - RL implementations

## Support

- Documentation: See this README
- API Reference: http://localhost:5002/ (when server is running)
- Issues: Create GitHub issue

---

**Ready to train intelligent trading agents!** 🤖📈
