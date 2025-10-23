# app.py - RL Trading API

from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
import numpy as np
from agents import DQNAgent, PPOAgent
from environment import TradingEnvironment
import os
from tqdm import tqdm

app = Flask(__name__)
CORS(app)

# Global storage for trained agents
agents = {}
environments = {}

@app.route('/api/rl/train-dqn', methods=['POST'])
def train_dqn():
    """
    Train DQN agent on ticker.

    Body:
    {
        "ticker": "AAPL",
        "episodes": 100,
        "agent_id": "my_dqn_agent"
    }
    """
    try:
        data = request.json
        ticker = data['ticker']
        episodes = data.get('episodes', 100)
        agent_id = data.get('agent_id', 'default_dqn')

        # Create environment
        env = TradingEnvironment(ticker)
        environments[agent_id] = env

        # Create agent
        agent = DQNAgent(
            state_dim=env.state_dim,
            action_dim=env.action_dim
        )

        # Training loop
        training_rewards = []

        print(f"Training DQN agent '{agent_id}' on {ticker} for {episodes} episodes...")

        for episode in tqdm(range(episodes)):
            state = env.reset()
            episode_reward = 0
            done = False

            while not done:
                action = agent.select_action(state, training=True)
                next_state, reward, done, info = env.step(action)

                agent.replay_buffer.push(state, action, reward, next_state, done)
                loss = agent.train_step()

                state = next_state
                episode_reward += reward

            training_rewards.append(episode_reward)

            if episode % 10 == 0:
                print(f"Episode {episode}, Reward: {episode_reward:.4f}, Epsilon: {agent.epsilon:.3f}")

        # Save agent
        agents[agent_id] = agent
        model_path = f"models/{agent_id}.pth"
        os.makedirs("models", exist_ok=True)
        agent.save(model_path)

        return jsonify({
            'agent_id': agent_id,
            'episodes_trained': episodes,
            'final_reward': float(training_rewards[-1]),
            'avg_reward': float(np.mean(training_rewards[-10:])),
            'model_path': model_path,
            'training_rewards': training_rewards
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/rl/train-ppo', methods=['POST'])
def train_ppo():
    """
    Train PPO agent on ticker.

    Body:
    {
        "ticker": "AAPL",
        "episodes": 100,
        "agent_id": "my_ppo_agent"
    }
    """
    try:
        data = request.json
        ticker = data['ticker']
        episodes = data.get('episodes', 100)
        agent_id = data.get('agent_id', 'default_ppo')

        # Create environment
        env = TradingEnvironment(ticker)
        environments[agent_id] = env

        # Create agent
        agent = PPOAgent(
            state_dim=env.state_dim,
            action_dim=env.action_dim,
            continuous=False
        )

        # Training loop
        training_rewards = []

        print(f"Training PPO agent '{agent_id}' on {ticker} for {episodes} episodes...")

        for episode in tqdm(range(episodes)):
            state = env.reset()
            episode_reward = 0
            done = False

            while not done:
                action = agent.select_action(state)
                next_state, reward, done, info = env.step(action)

                agent.store_transition(reward, done)

                state = next_state
                episode_reward += reward

            # Train at end of episode
            actor_loss, critic_loss = agent.train_step(state)

            training_rewards.append(episode_reward)

            if episode % 10 == 0:
                print(f"Episode {episode}, Reward: {episode_reward:.4f}")

        # Save agent
        agents[agent_id] = agent
        model_path = f"models/{agent_id}.pth"
        os.makedirs("models", exist_ok=True)
        agent.save(model_path)

        return jsonify({
            'agent_id': agent_id,
            'episodes_trained': episodes,
            'final_reward': float(training_rewards[-1]),
            'avg_reward': float(np.mean(training_rewards[-10:])),
            'model_path': model_path,
            'training_rewards': training_rewards
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/rl/backtest', methods=['POST'])
def backtest_agent():
    """
    Backtest trained agent.

    Body:
    {
        "agent_id": "my_dqn_agent",
        "ticker": "AAPL",
        "agent_type": "dqn"
    }
    """
    try:
        data = request.json
        agent_id = data['agent_id']
        ticker = data.get('ticker')
        agent_type = data.get('agent_type', 'dqn')

        if agent_id not in agents:
            # Try to load from disk
            model_path = f"models/{agent_id}.pth"
            if not os.path.exists(model_path):
                return jsonify({'error': 'Agent not found'}), 404

            # Need to recreate environment to get state/action dims
            env = TradingEnvironment(ticker or 'AAPL')

            if agent_type == 'dqn':
                agent = DQNAgent(env.state_dim, env.action_dim)
            else:
                agent = PPOAgent(env.state_dim, env.action_dim)

            agent.load(model_path)
            agents[agent_id] = agent

        agent = agents[agent_id]

        # Create test environment
        env = TradingEnvironment(ticker or 'AAPL')

        # Run backtest
        state = env.reset()
        done = False
        trades = []
        portfolio_values = [env.initial_balance]

        while not done:
            action = agent.select_action(state, training=False)
            state, reward, done, info = env.step(action)

            portfolio_values.append(info['portfolio_value'])
            if len(env.trades) > len(trades):
                trades.append(env.trades[-1])

        final_return = (env.portfolio_value - env.initial_balance) / env.initial_balance

        return jsonify({
            'agent_id': agent_id,
            'ticker': ticker,
            'initial_balance': env.initial_balance,
            'final_value': env.portfolio_value,
            'total_return': final_return * 100,
            'num_trades': len(trades),
            'trades': trades,
            'portfolio_curve': portfolio_values
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/rl/get-action', methods=['POST'])
def get_action():
    """
    Get action recommendation from trained agent.

    Body:
    {
        "agent_id": "my_dqn_agent",
        "state": [...]  // Current market state
    }
    """
    try:
        data = request.json
        agent_id = data['agent_id']
        state = np.array(data['state'])

        if agent_id not in agents:
            return jsonify({'error': 'Agent not found'}), 404

        agent = agents[agent_id]
        action = agent.select_action(state, training=False)

        action_map = {0: 'HOLD', 1: 'BUY', 2: 'SELL'}

        return jsonify({
            'action': action_map[action],
            'action_id': int(action)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/rl/list-agents', methods=['GET'])
def list_agents():
    """List all trained agents."""
    try:
        # Get from memory
        agent_list = list(agents.keys())

        # Get from disk
        if os.path.exists('models'):
            saved_models = [f.replace('.pth', '') for f in os.listdir('models') if f.endswith('.pth')]
            agent_list = list(set(agent_list + saved_models))

        return jsonify({
            'agents': agent_list,
            'count': len(agent_list)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/health', methods=['GET'])
def health():
    import os
    return jsonify({
        'status': 'healthy',
        'service': 'rl-trading',
        'port': int(os.environ.get('SERVICE_PORT', 5000))
    })


@app.route('/', methods=['GET'])
def root():
    """Root endpoint with API information."""
    return jsonify({
        'service': 'Trade2025 RL Trading',
        'version': '1.0.0',
        'endpoints': {
            'training': {
                'train_dqn': '/api/rl/train-dqn',
                'train_ppo': '/api/rl/train-ppo'
            },
            'inference': {
                'backtest': '/api/rl/backtest',
                'get_action': '/api/rl/get-action',
                'list_agents': '/api/rl/list-agents'
            },
            'system': {
                'health': '/health'
            }
        }
    })


if __name__ == '__main__':
    import os
    port = int(os.environ.get('SERVICE_PORT', 5000))

    print("[START] Trade2026 RL Trading System")
    print(f"[INFO] Server running on http://localhost:{port}")
    print(f"[INFO] API endpoints available at http://localhost:{port}/")
    app.run(host='0.0.0.0', port=port, debug=True)
