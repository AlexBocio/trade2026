# environment.py - Trading environment for RL

import numpy as np
import pandas as pd
import sys
import os

# Add parent directory to path to import shared module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.data_fetcher import fetch_prices

class TradingEnvironment:
    """
    Trading environment for RL agents.
    State: [prices, indicators, position, cash, portfolio_value]
    Actions: [hold, buy, sell]
    """

    def __init__(self, ticker, initial_balance=10000, commission=0.001):
        self.ticker = ticker
        self.initial_balance = initial_balance
        self.commission = commission

        # Load data
        self.data = self._load_data()
        self.max_steps = len(self.data) - 1

        # Trading state
        self.reset()

    def _load_data(self):
        """Load and preprocess market data."""
        df = fetch_prices(self.ticker, period='2y', progress=False)

        # Convert Series to DataFrame if needed
        if isinstance(df, pd.Series):
            df = df.to_frame(name='Close')

        # Ensure we have Close column
        if 'Close' not in df.columns and len(df.columns) == 1:
            df = df.rename(columns={df.columns[0]: 'Close'})

        # Calculate indicators
        df['returns'] = df['Close'].pct_change()
        df['sma_20'] = df['Close'].rolling(20).mean()
        df['sma_50'] = df['Close'].rolling(50).mean()
        df['rsi'] = self._calculate_rsi(df['Close'])

        df = df.dropna()

        return df

    def _calculate_rsi(self, prices, period=14):
        """Calculate RSI indicator."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def reset(self):
        """Reset environment to initial state."""
        self.current_step = 0
        self.cash = self.initial_balance
        self.shares = 0
        self.portfolio_value = self.initial_balance
        self.trades = []

        return self._get_state()

    def _get_state(self):
        """Get current state representation."""
        row = self.data.iloc[self.current_step]

        state = np.array([
            row['Close'] / 1000,  # Normalize price
            row['returns'],
            row['sma_20'] / row['Close'],  # Ratio
            row['sma_50'] / row['Close'],
            row['rsi'] / 100,
            self.shares / 100,  # Normalize position
            self.cash / self.initial_balance,
            self.portfolio_value / self.initial_balance
        ])

        return state

    def step(self, action):
        """
        Execute action and return next state, reward, done.

        Actions:
            0: Hold
            1: Buy (25% of cash)
            2: Sell (all shares)
        """
        current_price = self.data.iloc[self.current_step]['Close']

        # Execute action
        if action == 1:  # Buy
            max_shares = int((self.cash * 0.25) / current_price)
            if max_shares > 0:
                cost = max_shares * current_price * (1 + self.commission)
                if cost <= self.cash:
                    self.cash -= cost
                    self.shares += max_shares
                    self.trades.append(('BUY', max_shares, current_price))

        elif action == 2:  # Sell
            if self.shares > 0:
                proceeds = self.shares * current_price * (1 - self.commission)
                self.cash += proceeds
                self.trades.append(('SELL', self.shares, current_price))
                self.shares = 0

        # Move to next step
        self.current_step += 1
        done = self.current_step >= self.max_steps

        # Calculate new portfolio value
        if not done:
            next_price = self.data.iloc[self.current_step]['Close']
            new_portfolio_value = self.cash + self.shares * next_price
        else:
            # Final liquidation
            new_portfolio_value = self.cash + self.shares * current_price * (1 - self.commission)

        # Reward = change in portfolio value
        reward = (new_portfolio_value - self.portfolio_value) / self.initial_balance
        self.portfolio_value = new_portfolio_value

        next_state = self._get_state() if not done else None

        info = {
            'portfolio_value': self.portfolio_value,
            'cash': self.cash,
            'shares': self.shares,
            'total_return': (self.portfolio_value - self.initial_balance) / self.initial_balance
        }

        return next_state, reward, done, info

    @property
    def state_dim(self):
        return 8

    @property
    def action_dim(self):
        return 3


class MultiAssetTradingEnvironment:
    """
    Multi-asset trading environment.
    Manages portfolio across multiple stocks.
    """

    def __init__(self, tickers, initial_balance=10000, commission=0.001):
        self.tickers = tickers
        self.initial_balance = initial_balance
        self.commission = commission

        # Load data for all tickers
        self.data = self._load_data()
        self.max_steps = len(self.data) - 1

        self.reset()

    def _load_data(self):
        """Load data for all tickers."""
        data = {}
        for ticker in self.tickers:
            df = fetch_prices(ticker, period='2y', progress=False)

            # Convert Series to DataFrame if needed
            if isinstance(df, pd.Series):
                df = df.to_frame(name='Close')

            # Ensure we have Close column
            if 'Close' not in df.columns and len(df.columns) == 1:
                df = df.rename(columns={df.columns[0]: 'Close'})

            df['returns'] = df['Close'].pct_change()
            df = df.dropna()
            data[ticker] = df

        return data

    def reset(self):
        """Reset to initial state."""
        self.current_step = 0
        self.cash = self.initial_balance
        self.holdings = {ticker: 0 for ticker in self.tickers}
        self.portfolio_value = self.initial_balance

        return self._get_state()

    def _get_state(self):
        """Get state for all assets."""
        state = []

        for ticker in self.tickers:
            df = self.data[ticker]
            if self.current_step < len(df):
                row = df.iloc[self.current_step]
                state.extend([
                    row['Close'] / 1000,
                    row['returns'],
                    self.holdings[ticker] / 100
                ])
            else:
                state.extend([0, 0, 0])

        state.extend([
            self.cash / self.initial_balance,
            self.portfolio_value / self.initial_balance
        ])

        return np.array(state)

    def step(self, actions):
        """
        Execute actions for all assets.

        Args:
            actions: Dict of {ticker: action} where action in [0, 1, 2]
        """
        # Execute all actions
        for ticker, action in actions.items():
            if ticker not in self.data:
                continue

            df = self.data[ticker]
            if self.current_step >= len(df):
                continue

            current_price = df.iloc[self.current_step]['Close']

            if action == 1:  # Buy
                max_shares = int((self.cash * 0.1) / current_price)  # 10% per asset
                if max_shares > 0:
                    cost = max_shares * current_price * (1 + self.commission)
                    if cost <= self.cash:
                        self.cash -= cost
                        self.holdings[ticker] += max_shares

            elif action == 2:  # Sell
                if self.holdings[ticker] > 0:
                    proceeds = self.holdings[ticker] * current_price * (1 - self.commission)
                    self.cash += proceeds
                    self.holdings[ticker] = 0

        # Move to next step
        self.current_step += 1
        done = self.current_step >= self.max_steps

        # Calculate portfolio value
        portfolio_value = self.cash
        for ticker in self.tickers:
            if ticker in self.data:
                df = self.data[ticker]
                if self.current_step < len(df):
                    current_price = df.iloc[self.current_step]['Close']
                    portfolio_value += self.holdings[ticker] * current_price

        # Reward
        reward = (portfolio_value - self.portfolio_value) / self.initial_balance
        self.portfolio_value = portfolio_value

        next_state = self._get_state() if not done else None

        info = {
            'portfolio_value': portfolio_value,
            'cash': self.cash,
            'holdings': self.holdings.copy(),
            'total_return': (portfolio_value - self.initial_balance) / self.initial_balance
        }

        return next_state, reward, done, info

    @property
    def state_dim(self):
        return len(self.tickers) * 3 + 2

    @property
    def action_dim(self):
        return 3  # Per asset
