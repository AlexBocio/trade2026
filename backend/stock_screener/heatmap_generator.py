# heatmap_generator.py - Generate Heatmap Data for Multi-Timeframe Visualization
# Creates dual-axis heatmap showing long/short opportunities across timeframes

import numpy as np
import pandas as pd
from typing import Dict, List
import yfinance as yf
import logging

logger = logging.getLogger(__name__)


class HeatmapGenerator:
    """
    Generate heatmap data structure for multi-timeframe visualization.
    """

    # Define timeframe order (for X-axis)
    TIMEFRAME_ORDER = [
        # Short side (left to right: far to near zero)
        '-6mo', '-5mo', '-4mo', '-3mo', '-2mo', '-1mo',
        '-5w', '-4w', '-3w', '-2w', '-1w',
        '-5d', '-4d', '-3d', '-2d', '-1d',
        '-4h', '-1h',
        # Zero point
        '0',
        # Long side (left to right: near to far zero)
        '+1h', '+4h',
        '+1d', '+2d', '+3d', '+4d', '+5d',
        '+1w', '+2w', '+3w', '+4w', '+5w',
        '+1mo', '+2mo', '+3mo', '+4mo', '+5mo', '+6mo'
    ]

    def generate_heatmap_data(self,
                             screener_results: List[Dict],
                             predictions_by_ticker: Dict[str, Dict],
                             price_cache: Dict[str, float] = None) -> Dict:
        """
        Generate heatmap data structure from predictions.

        Args:
            screener_results: List of top stocks from screener
            predictions_by_ticker: {
                'AAPL': {
                    '1h': {'predicted_return': 0.01, 'confidence': 0.8, ...},
                    '1d': {'predicted_return': -0.02, 'confidence': 0.85, ...},
                    ...
                },
                ...
            }
            price_cache: Optional dict of current prices

        Returns:
            {
                'tickers': ['AAPL', 'MSFT', ...],
                'timeframes': ['-6mo', ..., '0', ..., '+6mo'],
                'matrix': [...],
                'confidence_matrix': [...],
                'strength_matrix': [...],
                'cell_data': {...}
            }
        """
        logger.info(f"Generating heatmap for {len(screener_results)} stocks")

        tickers = [stock['ticker'] for stock in screener_results]
        n_tickers = len(tickers)
        n_timeframes = len(self.TIMEFRAME_ORDER)

        # Initialize matrices
        matrix = np.zeros((n_tickers, n_timeframes))
        confidence_matrix = np.zeros((n_tickers, n_timeframes))
        strength_matrix = np.zeros((n_tickers, n_timeframes))  # 0=none, 1=weak, 2=moderate, 3=strong

        cell_data = {}

        # Fill matrices
        for i, ticker in enumerate(tickers):
            cell_data[ticker] = {}

            if ticker not in predictions_by_ticker:
                logger.warning(f"No predictions for {ticker}")
                continue

            predictions = predictions_by_ticker[ticker]

            for horizon_key, pred in predictions.items():
                # Determine timeframe label
                predicted_return = pred['predicted_return']
                direction = pred['direction']

                if direction == 'neutral':
                    timeframe_label = '0'
                elif direction == 'long':
                    timeframe_label = f'+{horizon_key}'
                else:  # short
                    timeframe_label = f'-{horizon_key}'

                # Find column index
                if timeframe_label in self.TIMEFRAME_ORDER:
                    j = self.TIMEFRAME_ORDER.index(timeframe_label)

                    # Fill matrix
                    matrix[i, j] = predicted_return
                    confidence_matrix[i, j] = pred['confidence']

                    # Strength encoding
                    strength_map = {'none': 0, 'weak': 1, 'moderate': 2, 'strong': 3}
                    strength_matrix[i, j] = strength_map.get(pred['strength'], 0)

                    # Get current price
                    current_price = price_cache.get(ticker, 100.0) if price_cache else 100.0

                    # Store cell data
                    cell_data[ticker][timeframe_label] = {
                        **pred,
                        'trade_setup': self._generate_trade_setup(
                            ticker,
                            horizon_key,
                            pred,
                            current_price
                        )
                    }

        logger.info(f"Heatmap generated: {n_tickers} tickers × {n_timeframes} timeframes")

        return {
            'tickers': tickers,
            'timeframes': self.TIMEFRAME_ORDER,
            'matrix': matrix.tolist(),
            'confidence_matrix': confidence_matrix.tolist(),
            'strength_matrix': strength_matrix.tolist(),
            'cell_data': cell_data,
            'metadata': {
                'n_tickers': n_tickers,
                'n_timeframes': n_timeframes,
                'max_return': float(np.max(np.abs(matrix))) if matrix.size > 0 else 0.0,
                'min_return': float(np.min(np.abs(matrix))) if matrix.size > 0 else 0.0,
                'avg_confidence': float(np.mean(confidence_matrix)) if confidence_matrix.size > 0 else 0.0,
                'timestamp': pd.Timestamp.now().isoformat()
            }
        }

    def _generate_trade_setup(self,
                             ticker: str,
                             horizon: str,
                             prediction: Dict,
                             current_price: float) -> Dict:
        """
        Generate actionable trade setup for a specific prediction.

        Returns:
            {
                'action': 'BUY' | 'SELL',
                'entry_price': Current price,
                'target_price': Expected price at horizon,
                'stop_loss': Suggested stop loss,
                'position_size': % of portfolio,
                'hold_period': Human-readable time,
                'risk_reward': Ratio,
                'confidence_adjusted_size': Position size × confidence
            }
        """
        predicted_return = prediction['predicted_return']
        confidence = prediction['confidence']
        direction = prediction['direction']

        # Calculate targets
        target_price = current_price * (1 + predicted_return)

        # Stop loss: 50% of expected move (opposite direction)
        if direction == 'long':
            stop_loss = current_price * (1 - abs(predicted_return) * 0.5)
        else:
            stop_loss = current_price * (1 + abs(predicted_return) * 0.5)

        # Risk/reward
        risk = abs(current_price - stop_loss)
        reward = abs(target_price - current_price)
        risk_reward = reward / risk if risk > 0 else 0

        # Position sizing (Kelly criterion simplified)
        base_position_size = min(abs(predicted_return) * 10, 10.0)  # Max 10% per position
        confidence_adjusted_size = base_position_size * confidence

        return {
            'action': 'BUY' if direction == 'long' else 'SELL',
            'entry_price': float(current_price),
            'target_price': float(target_price),
            'stop_loss': float(stop_loss),
            'position_size_pct': float(base_position_size),
            'confidence_adjusted_size_pct': float(confidence_adjusted_size),
            'hold_period': horizon,
            'risk_reward_ratio': float(risk_reward),
            'expected_return_pct': float(predicted_return * 100),
            'confidence': float(confidence)
        }

    def get_best_opportunities(self,
                              heatmap_data: Dict,
                              min_confidence: float = 0.7,
                              min_return: float = 0.02,
                              max_results: int = 10) -> List[Dict]:
        """
        Extract best trading opportunities from heatmap.

        Args:
            heatmap_data: Generated heatmap data
            min_confidence: Minimum confidence threshold
            min_return: Minimum expected return (absolute)
            max_results: Maximum number of opportunities to return

        Returns:
            List of best opportunities sorted by expected return × confidence
        """
        opportunities = []

        cell_data = heatmap_data['cell_data']

        for ticker, timeframes in cell_data.items():
            for timeframe, data in timeframes.items():
                if timeframe == '0':
                    continue

                predicted_return = data['predicted_return']
                confidence = data['confidence']

                # Filter by thresholds
                if confidence < min_confidence:
                    continue

                if abs(predicted_return) < min_return:
                    continue

                # Calculate score
                score = abs(predicted_return) * confidence

                opportunities.append({
                    'ticker': ticker,
                    'timeframe': timeframe,
                    'predicted_return': predicted_return,
                    'confidence': confidence,
                    'score': score,
                    'trade_setup': data['trade_setup'],
                    'direction': data['direction'],
                    'strength': data['strength']
                })

        # Sort by score descending
        opportunities.sort(key=lambda x: x['score'], reverse=True)

        return opportunities[:max_results]

    def get_ticker_summary(self,
                          heatmap_data: Dict,
                          ticker: str) -> Dict:
        """
        Get summary of predictions for a specific ticker.

        Returns:
            {
                'ticker': 'AAPL',
                'best_long_timeframe': '+1w',
                'best_long_return': 0.035,
                'best_short_timeframe': '-1d',
                'best_short_return': -0.025,
                'avg_confidence': 0.78,
                'recommendation': 'LONG'
            }
        """
        cell_data = heatmap_data['cell_data'].get(ticker, {})

        if not cell_data:
            return {
                'ticker': ticker,
                'error': 'No predictions available'
            }

        long_opportunities = []
        short_opportunities = []
        confidences = []

        for timeframe, data in cell_data.items():
            if timeframe == '0':
                continue

            predicted_return = data['predicted_return']
            confidence = data['confidence']
            confidences.append(confidence)

            if predicted_return > 0:
                long_opportunities.append((timeframe, predicted_return, confidence))
            elif predicted_return < 0:
                short_opportunities.append((timeframe, abs(predicted_return), confidence))

        # Find best opportunities
        best_long = max(long_opportunities, key=lambda x: x[1] * x[2]) if long_opportunities else None
        best_short = max(short_opportunities, key=lambda x: x[1] * x[2]) if short_opportunities else None

        # Overall recommendation
        long_score = sum(ret * conf for _, ret, conf in long_opportunities) if long_opportunities else 0
        short_score = sum(ret * conf for _, ret, conf in short_opportunities) if short_opportunities else 0

        if long_score > short_score:
            recommendation = 'LONG'
        elif short_score > long_score:
            recommendation = 'SHORT'
        else:
            recommendation = 'NEUTRAL'

        return {
            'ticker': ticker,
            'best_long_timeframe': best_long[0] if best_long else None,
            'best_long_return': float(best_long[1]) if best_long else 0.0,
            'best_short_timeframe': best_short[0] if best_short else None,
            'best_short_return': float(best_short[1]) if best_short else 0.0,
            'avg_confidence': float(np.mean(confidences)) if confidences else 0.0,
            'recommendation': recommendation,
            'long_score': float(long_score),
            'short_score': float(short_score)
        }
