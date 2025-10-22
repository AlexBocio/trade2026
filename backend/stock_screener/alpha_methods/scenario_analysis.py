# scenario_analysis.py - Macro Scenario Analysis
# Simulates macro events and identifies beneficiaries

from typing import Dict, List, Optional
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class ScenarioAnalysis:
    """
    Macro scenario simulation and beneficiary detection.

    Scenarios:
    1. Fed rate cuts (25bp, 50bp, emergency)
    2. Recession (mild, severe)
    3. Inflation spike
    4. Dollar strength/weakness
    5. Energy crisis
    6. Tech boom/bust
    7. Banking crisis
    """

    # Scenario definitions with expected sector impacts
    SCENARIOS = {
        'FED_CUT_25BP': {
            'name': 'Fed Rate Cut 25bp',
            'description': 'Federal Reserve cuts interest rates by 25 basis points',
            'beneficiaries': {
                'XLF': 0.02,   # Financials (moderate positive)
                'XLY': 0.03,   # Consumer Discretionary (positive)
                'XLI': 0.02,   # Industrials (positive)
                'XLRE': 0.04,  # Real Estate (strong positive)
                'XLU': 0.03,   # Utilities (positive)
                'GLD': 0.02,   # Gold (moderate positive)
                'TLT': 0.05    # Long bonds (strong positive)
            }
        },
        'FED_CUT_50BP': {
            'name': 'Fed Rate Cut 50bp (Emergency)',
            'description': 'Federal Reserve emergency rate cut of 50 basis points',
            'beneficiaries': {
                'XLF': 0.04,
                'XLY': 0.05,
                'XLI': 0.04,
                'XLRE': 0.08,
                'XLU': 0.05,
                'GLD': 0.06,
                'TLT': 0.10,
                'XLK': -0.02   # Tech may suffer (recession signal)
            }
        },
        'RECESSION_MILD': {
            'name': 'Mild Recession',
            'description': 'Economic slowdown with 1-2% GDP contraction',
            'beneficiaries': {
                'XLP': 0.03,   # Consumer Staples (defensive)
                'XLV': 0.02,   # Healthcare (defensive)
                'XLU': 0.02,   # Utilities (defensive)
                'GLD': 0.05,   # Gold (flight to safety)
                'TLT': 0.06,   # Bonds (flight to safety)
                'XLY': -0.05,  # Consumer Discretionary (negative)
                'XLI': -0.04,  # Industrials (negative)
                'XLE': -0.03   # Energy (negative)
            }
        },
        'RECESSION_SEVERE': {
            'name': 'Severe Recession',
            'description': 'Deep recession with >3% GDP contraction',
            'beneficiaries': {
                'XLP': 0.05,
                'XLV': 0.03,
                'XLU': 0.03,
                'GLD': 0.10,
                'TLT': 0.12,
                'XLY': -0.10,
                'XLI': -0.08,
                'XLE': -0.06,
                'XLF': -0.08,
                'XLK': -0.06
            }
        },
        'INFLATION_SPIKE': {
            'name': 'Inflation Spike',
            'description': 'CPI increases above 6% year-over-year',
            'beneficiaries': {
                'XLE': 0.08,   # Energy (positive)
                'XLB': 0.05,   # Materials (positive)
                'GLD': 0.06,   # Gold (inflation hedge)
                'XLRE': 0.04,  # Real Estate (moderate positive)
                'TLT': -0.08,  # Bonds (negative)
                'XLU': -0.03,  # Utilities (negative)
                'XLF': -0.04   # Financials (negative)
            }
        },
        'DOLLAR_STRENGTH': {
            'name': 'Strong Dollar',
            'description': 'Dollar index (DXY) rallies >5%',
            'beneficiaries': {
                'UUP': 0.05,   # Dollar bullish fund
                'XLF': 0.03,   # Financials (positive)
                'XLP': 0.02,   # Staples (positive)
                'EEM': -0.06,  # Emerging markets (negative)
                'GLD': -0.04,  # Gold (negative)
                'XLE': -0.03   # Energy (negative)
            }
        },
        'DOLLAR_WEAKNESS': {
            'name': 'Weak Dollar',
            'description': 'Dollar index (DXY) falls >5%',
            'beneficiaries': {
                'EEM': 0.08,   # Emerging markets (positive)
                'GLD': 0.06,   # Gold (positive)
                'XLE': 0.05,   # Energy (positive)
                'XLB': 0.04,   # Materials (positive)
                'UUP': -0.05,  # Dollar fund (negative)
                'XLF': -0.03   # Financials (negative)
            }
        },
        'ENERGY_CRISIS': {
            'name': 'Energy Crisis',
            'description': 'Oil prices spike >20% in 30 days',
            'beneficiaries': {
                'XLE': 0.15,   # Energy (very positive)
                'USO': 0.12,   # Oil ETF (very positive)
                'XLB': 0.04,   # Materials (moderate positive)
                'XLY': -0.06,  # Consumer Discretionary (negative)
                'XLI': -0.05,  # Industrials (negative)
                'XLP': -0.03   # Staples (negative)
            }
        },
        'TECH_BOOM': {
            'name': 'Tech Boom',
            'description': 'Technology sector rally driven by AI/innovation',
            'beneficiaries': {
                'XLK': 0.10,   # Technology (very positive)
                'QQQ': 0.12,   # Nasdaq (very positive)
                'XLC': 0.08,   # Communication Services (positive)
                'XLY': 0.05,   # Consumer Discretionary (positive)
                'XLV': 0.03,   # Healthcare (moderate positive)
                'XLE': -0.02,  # Energy (relative negative)
                'XLU': -0.02   # Utilities (relative negative)
            }
        },
        'BANKING_CRISIS': {
            'name': 'Banking Crisis',
            'description': 'Financial sector stress, bank failures',
            'beneficiaries': {
                'GLD': 0.10,   # Gold (flight to safety)
                'TLT': 0.08,   # Bonds (flight to safety)
                'XLU': 0.04,   # Utilities (defensive)
                'XLP': 0.03,   # Staples (defensive)
                'XLF': -0.15,  # Financials (very negative)
                'XLRE': -0.08, # Real Estate (negative)
                'XLY': -0.06,  # Consumer Discretionary (negative)
                'XLI': -0.05   # Industrials (negative)
            }
        }
    }

    def __init__(self, mock_mode: bool = False):
        self.mock_mode = mock_mode

    def simulate_scenario(self, scenario_name: str, symbols: Optional[List[str]] = None) -> Dict:
        """
        Simulate a macro scenario and identify beneficiaries.

        Args:
            scenario_name: One of the predefined scenarios
            symbols: Optional list of specific symbols to analyze (in addition to sector ETFs)

        Returns:
            {
                'scenario': str,
                'description': str,
                'beneficiaries': List[Dict],
                'detractors': List[Dict],
                'neutral': List[Dict],
                'analysis_date': str
            }
        """
        try:
            if scenario_name not in self.SCENARIOS:
                return {
                    'error': f'Unknown scenario: {scenario_name}',
                    'available_scenarios': list(self.SCENARIOS.keys())
                }

            scenario = self.SCENARIOS[scenario_name]

            if self.mock_mode:
                return self._mock_scenario_result(scenario_name, scenario)

            # Analyze sector ETFs from scenario
            beneficiaries = []
            detractors = []
            neutral = []

            for symbol, expected_impact in scenario['beneficiaries'].items():
                # Get current data
                analysis = self._analyze_symbol(symbol, expected_impact)

                if analysis['expected_impact'] > 0.02:
                    beneficiaries.append(analysis)
                elif analysis['expected_impact'] < -0.02:
                    detractors.append(analysis)
                else:
                    neutral.append(analysis)

            # Analyze additional symbols if provided
            if symbols:
                for symbol in symbols:
                    # Infer expected impact based on sector
                    sector = self._infer_sector(symbol)
                    expected_impact = scenario['beneficiaries'].get(sector, 0.0)

                    analysis = self._analyze_symbol(symbol, expected_impact)

                    if analysis['expected_impact'] > 0.02:
                        beneficiaries.append(analysis)
                    elif analysis['expected_impact'] < -0.02:
                        detractors.append(analysis)
                    else:
                        neutral.append(analysis)

            # Sort by expected impact
            beneficiaries.sort(key=lambda x: x['expected_impact'], reverse=True)
            detractors.sort(key=lambda x: x['expected_impact'])

            return {
                'scenario': scenario_name,
                'scenario_name': scenario['name'],
                'description': scenario['description'],
                'beneficiaries': beneficiaries,
                'detractors': detractors,
                'neutral': neutral,
                'analysis_date': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error simulating scenario {scenario_name}: {e}")
            return {
                'scenario': scenario_name,
                'error': str(e)
            }

    def analyze_all_scenarios(self, symbol: str) -> Dict:
        """
        Analyze how a symbol performs across all scenarios.

        Args:
            symbol: Stock symbol to analyze

        Returns:
            {
                'symbol': str,
                'best_scenarios': List[Dict],
                'worst_scenarios': List[Dict],
                'overall_resilience': float (0-100),
                'interpretation': str
            }
        """
        try:
            if self.mock_mode:
                return self._mock_all_scenarios_result(symbol)

            scenario_results = []

            for scenario_name, scenario in self.SCENARIOS.items():
                sector = self._infer_sector(symbol)
                expected_impact = scenario['beneficiaries'].get(sector, 0.0)

                scenario_results.append({
                    'scenario': scenario_name,
                    'scenario_name': scenario['name'],
                    'expected_impact': expected_impact,
                    'impact_category': self._categorize_impact(expected_impact)
                })

            # Sort scenarios
            scenario_results.sort(key=lambda x: x['expected_impact'], reverse=True)

            best_scenarios = [s for s in scenario_results if s['expected_impact'] > 0.02]
            worst_scenarios = [s for s in scenario_results if s['expected_impact'] < -0.02]

            # Calculate overall resilience (0-100)
            # High resilience = performs well across many scenarios
            positive_count = len(best_scenarios)
            negative_count = len(worst_scenarios)
            total_scenarios = len(self.SCENARIOS)

            resilience = ((positive_count - negative_count) / total_scenarios) * 50 + 50
            resilience = max(0, min(100, resilience))

            interpretation = self._interpret_resilience(symbol, resilience, best_scenarios, worst_scenarios)

            return {
                'symbol': symbol,
                'best_scenarios': best_scenarios[:5],
                'worst_scenarios': worst_scenarios[:5],
                'overall_resilience': round(resilience, 1),
                'interpretation': interpretation,
                'analysis_date': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error analyzing all scenarios for {symbol}: {e}")
            return {
                'symbol': symbol,
                'error': str(e)
            }

    def compare_scenarios(self, scenario1: str, scenario2: str) -> Dict:
        """
        Compare two scenarios side-by-side.

        Args:
            scenario1: First scenario name
            scenario2: Second scenario name

        Returns:
            {
                'scenario1': Dict,
                'scenario2': Dict,
                'winners_in_both': List[str],
                'losers_in_both': List[str],
                'divergent': List[Dict]
            }
        """
        try:
            if scenario1 not in self.SCENARIOS or scenario2 not in self.SCENARIOS:
                return {'error': 'Invalid scenario names'}

            s1_data = self.simulate_scenario(scenario1)
            s2_data = self.simulate_scenario(scenario2)

            s1_beneficiaries = set(b['symbol'] for b in s1_data.get('beneficiaries', []))
            s2_beneficiaries = set(b['symbol'] for b in s2_data.get('beneficiaries', []))

            s1_detractors = set(d['symbol'] for d in s1_data.get('detractors', []))
            s2_detractors = set(d['symbol'] for d in s2_data.get('detractors', []))

            winners_in_both = list(s1_beneficiaries & s2_beneficiaries)
            losers_in_both = list(s1_detractors & s2_detractors)

            # Find divergent symbols
            divergent = []
            all_symbols = s1_beneficiaries | s1_detractors | s2_beneficiaries | s2_detractors

            for symbol in all_symbols:
                in_s1_winners = symbol in s1_beneficiaries
                in_s2_winners = symbol in s2_beneficiaries

                if in_s1_winners != in_s2_winners:
                    divergent.append({
                        'symbol': symbol,
                        f'{scenario1}': 'winner' if in_s1_winners else 'loser',
                        f'{scenario2}': 'winner' if in_s2_winners else 'loser'
                    })

            return {
                'scenario1': {
                    'name': scenario1,
                    'description': self.SCENARIOS[scenario1]['description']
                },
                'scenario2': {
                    'name': scenario2,
                    'description': self.SCENARIOS[scenario2]['description']
                },
                'winners_in_both': winners_in_both,
                'losers_in_both': losers_in_both,
                'divergent': divergent,
                'analysis_date': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error comparing scenarios: {e}")
            return {'error': str(e)}

    def _analyze_symbol(self, symbol: str, expected_impact: float) -> Dict:
        """Analyze a symbol under a scenario."""
        try:
            # Get current price and volatility
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period='1mo')

            if len(hist) < 5:
                current_price = 0
                volatility = 0
            else:
                current_price = float(hist['Close'].iloc[-1])
                returns = hist['Close'].pct_change().dropna()
                volatility = float(returns.std() * np.sqrt(252))

            return {
                'symbol': symbol,
                'expected_impact': expected_impact,
                'impact_category': self._categorize_impact(expected_impact),
                'current_price': current_price,
                'volatility': volatility,
                'confidence': self._calculate_confidence(volatility)
            }

        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            return {
                'symbol': symbol,
                'expected_impact': expected_impact,
                'impact_category': self._categorize_impact(expected_impact),
                'current_price': 0,
                'volatility': 0,
                'confidence': 'low'
            }

    def _infer_sector(self, symbol: str) -> str:
        """Infer sector ETF from individual stock symbol."""
        # Simplified sector mapping
        sector_keywords = {
            'XLK': ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'META', 'AVGO', 'ORCL', 'CSCO', 'CRM', 'ADBE'],
            'XLF': ['JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'BLK', 'SCHW', 'AXP', 'PNC'],
            'XLE': ['XOM', 'CVX', 'COP', 'SLB', 'EOG', 'MPC', 'PSX', 'VLO', 'OXY', 'HAL'],
            'XLV': ['UNH', 'JNJ', 'LLY', 'ABBV', 'PFE', 'MRK', 'TMO', 'ABT', 'DHR', 'BMY'],
            'XLY': ['AMZN', 'TSLA', 'HD', 'MCD', 'NKE', 'SBUX', 'TGT', 'LOW', 'TJX', 'MAR'],
            'XLP': ['PG', 'KO', 'PEP', 'COST', 'WMT', 'PM', 'MO', 'CL', 'MDLZ', 'KMB'],
            'XLI': ['BA', 'HON', 'UNP', 'CAT', 'GE', 'RTX', 'LMT', 'MMM', 'DE', 'UPS'],
            'XLB': ['LIN', 'APD', 'SHW', 'ECL', 'FCX', 'NEM', 'DD', 'DOW', 'ALB', 'NUE']
        }

        for sector, stocks in sector_keywords.items():
            if symbol in stocks:
                return sector

        # Default to technology if unknown
        return 'XLK'

    def _categorize_impact(self, impact: float) -> str:
        """Categorize impact magnitude."""
        if impact > 0.05:
            return 'strong_positive'
        elif impact > 0.02:
            return 'moderate_positive'
        elif impact > -0.02:
            return 'neutral'
        elif impact > -0.05:
            return 'moderate_negative'
        else:
            return 'strong_negative'

    def _calculate_confidence(self, volatility: float) -> str:
        """Calculate confidence level based on volatility."""
        if volatility < 0.2:
            return 'high'
        elif volatility < 0.4:
            return 'medium'
        else:
            return 'low'

    def _interpret_resilience(self, symbol: str, resilience: float, best: List, worst: List) -> str:
        """Generate resilience interpretation."""
        if resilience > 70:
            return f"{symbol} shows high resilience, benefiting from {len(best)} scenarios. Strong defensive characteristics."
        elif resilience > 50:
            return f"{symbol} shows moderate resilience, performing well in {len(best)} scenarios."
        elif resilience > 30:
            return f"{symbol} shows below-average resilience, vulnerable in {len(worst)} scenarios."
        else:
            return f"{symbol} shows low resilience, highly vulnerable across {len(worst)} scenarios. High-risk asset."

    # Mock methods
    def _mock_scenario_result(self, scenario_name: str, scenario: Dict) -> Dict:
        """Generate mock scenario result."""
        beneficiaries = []
        detractors = []

        for symbol, impact in scenario['beneficiaries'].items():
            analysis = {
                'symbol': symbol,
                'expected_impact': impact,
                'impact_category': self._categorize_impact(impact),
                'current_price': np.random.uniform(50, 200),
                'volatility': np.random.uniform(0.15, 0.35),
                'confidence': 'high'
            }

            if impact > 0.02:
                beneficiaries.append(analysis)
            elif impact < -0.02:
                detractors.append(analysis)

        return {
            'scenario': scenario_name,
            'scenario_name': scenario['name'],
            'description': scenario['description'],
            'beneficiaries': beneficiaries,
            'detractors': detractors,
            'neutral': [],
            'analysis_date': datetime.now().isoformat()
        }

    def _mock_all_scenarios_result(self, symbol: str) -> Dict:
        """Generate mock all-scenarios result."""
        scenario_results = []

        for scenario_name, scenario in self.SCENARIOS.items():
            impact = np.random.uniform(-0.08, 0.08)
            scenario_results.append({
                'scenario': scenario_name,
                'scenario_name': scenario['name'],
                'expected_impact': impact,
                'impact_category': self._categorize_impact(impact)
            })

        scenario_results.sort(key=lambda x: x['expected_impact'], reverse=True)

        best_scenarios = scenario_results[:3]
        worst_scenarios = scenario_results[-3:]
        resilience = np.random.uniform(40, 80)

        return {
            'symbol': symbol,
            'best_scenarios': best_scenarios,
            'worst_scenarios': worst_scenarios,
            'overall_resilience': round(resilience, 1),
            'interpretation': self._interpret_resilience(symbol, resilience, best_scenarios, worst_scenarios),
            'analysis_date': datetime.now().isoformat()
        }


# Module-level instance
_scenario_analysis = ScenarioAnalysis()


def simulate_scenario(scenario_name: str, symbols: Optional[List[str]] = None) -> Dict:
    """Simulate a macro scenario."""
    return _scenario_analysis.simulate_scenario(scenario_name, symbols)


def analyze_all_scenarios(symbol: str) -> Dict:
    """Analyze symbol across all scenarios."""
    return _scenario_analysis.analyze_all_scenarios(symbol)


def compare_scenarios(scenario1: str, scenario2: str) -> Dict:
    """Compare two scenarios."""
    return _scenario_analysis.compare_scenarios(scenario1, scenario2)


def list_scenarios() -> List[str]:
    """List all available scenarios."""
    return list(ScenarioAnalysis.SCENARIOS.keys())
