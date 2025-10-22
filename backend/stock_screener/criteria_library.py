# criteria_library.py - Flexible Screening Criteria Library
# Provides toggleable criteria with custom weights for stock screening

from typing import Dict, List, Callable, Any
import pandas as pd
import numpy as np
from dataclasses import dataclass
from enum import Enum


class CriteriaCategory(Enum):
    """Categories of screening criteria."""
    VALUATION = "valuation"
    GROWTH = "growth"
    MOMENTUM = "momentum"
    QUALITY = "quality"
    TECHNICAL = "technical"
    REGIME = "regime"
    HIERARCHY = "hierarchy"


class RankingMethod(Enum):
    """Methods for ranking stocks."""
    COMPOSITE_SCORE = "composite_score"  # Weighted sum
    PERCENTILE_RANK = "percentile_rank"  # Rank by percentile
    Z_SCORE = "z_score"  # Standardized scores
    PARETO_OPTIMAL = "pareto_optimal"  # Multi-objective optimization


@dataclass
class Criterion:
    """Single screening criterion."""
    id: str
    name: str
    category: CriteriaCategory
    description: str
    calc_function: Callable[[Dict], float]
    ideal_direction: str  # 'higher' or 'lower'
    default_weight: float = 1.0
    enabled_by_default: bool = True


class CriteriaLibrary:
    """
    Library of all available screening criteria.

    Provides:
    - Toggleable criteria (enable/disable)
    - Custom weights
    - Multiple ranking methods
    - Integration with PROMPT 1 & 2 data
    """

    def __init__(self):
        self.criteria = self._build_criteria_library()

    def _build_criteria_library(self) -> Dict[str, Criterion]:
        """Build the complete criteria library."""
        criteria = {}

        # VALUATION CRITERIA
        criteria['pe_ratio'] = Criterion(
            id='pe_ratio',
            name='P/E Ratio',
            category=CriteriaCategory.VALUATION,
            description='Price-to-Earnings ratio (lower is better)',
            calc_function=lambda stock: stock.get('factors', {}).get('pe_ratio', 20),
            ideal_direction='lower',
            default_weight=1.0
        )

        criteria['pb_ratio'] = Criterion(
            id='pb_ratio',
            name='P/B Ratio',
            category=CriteriaCategory.VALUATION,
            description='Price-to-Book ratio (lower is better)',
            calc_function=lambda stock: stock.get('factors', {}).get('pb_ratio', 3),
            ideal_direction='lower',
            default_weight=0.8
        )

        criteria['ps_ratio'] = Criterion(
            id='ps_ratio',
            name='P/S Ratio',
            category=CriteriaCategory.VALUATION,
            description='Price-to-Sales ratio (lower is better)',
            calc_function=lambda stock: stock.get('factors', {}).get('ps_ratio', 2),
            ideal_direction='lower',
            default_weight=0.7
        )

        # GROWTH CRITERIA
        criteria['revenue_growth'] = Criterion(
            id='revenue_growth',
            name='Revenue Growth',
            category=CriteriaCategory.GROWTH,
            description='Year-over-year revenue growth %',
            calc_function=lambda stock: stock.get('factors', {}).get('revenue_growth_yoy', 0),
            ideal_direction='higher',
            default_weight=1.2
        )

        criteria['earnings_growth'] = Criterion(
            id='earnings_growth',
            name='Earnings Growth',
            category=CriteriaCategory.GROWTH,
            description='Year-over-year earnings growth %',
            calc_function=lambda stock: stock.get('factors', {}).get('earnings_growth_yoy', 0),
            ideal_direction='higher',
            default_weight=1.5
        )

        # MOMENTUM CRITERIA
        criteria['momentum_20d'] = Criterion(
            id='momentum_20d',
            name='20-Day Momentum',
            category=CriteriaCategory.MOMENTUM,
            description='20-day price momentum %',
            calc_function=lambda stock: stock.get('factors', {}).get('momentum_20d', 0),
            ideal_direction='higher',
            default_weight=1.3
        )

        criteria['momentum_60d'] = Criterion(
            id='momentum_60d',
            name='60-Day Momentum',
            category=CriteriaCategory.MOMENTUM,
            description='60-day price momentum %',
            calc_function=lambda stock: stock.get('factors', {}).get('momentum_60d', 0),
            ideal_direction='higher',
            default_weight=1.0
        )

        criteria['rsi'] = Criterion(
            id='rsi',
            name='RSI',
            category=CriteriaCategory.MOMENTUM,
            description='Relative Strength Index (50-70 ideal)',
            calc_function=lambda stock: abs(stock.get('factors', {}).get('rsi', 50) - 60),
            ideal_direction='lower',  # Distance from 60
            default_weight=0.8
        )

        # QUALITY CRITERIA
        criteria['roe'] = Criterion(
            id='roe',
            name='Return on Equity',
            category=CriteriaCategory.QUALITY,
            description='Return on Equity %',
            calc_function=lambda stock: stock.get('factors', {}).get('roe', 0),
            ideal_direction='higher',
            default_weight=1.0
        )

        criteria['debt_to_equity'] = Criterion(
            id='debt_to_equity',
            name='Debt-to-Equity',
            category=CriteriaCategory.QUALITY,
            description='Debt-to-Equity ratio (lower is better)',
            calc_function=lambda stock: stock.get('factors', {}).get('debt_to_equity', 1),
            ideal_direction='lower',
            default_weight=0.7
        )

        # TECHNICAL CRITERIA
        criteria['volume_trend'] = Criterion(
            id='volume_trend',
            name='Volume Trend',
            category=CriteriaCategory.TECHNICAL,
            description='Volume vs 20-day average',
            calc_function=lambda stock: stock.get('factors', {}).get('volume_ratio', 1) - 1,
            ideal_direction='higher',
            default_weight=0.9
        )

        criteria['volatility'] = Criterion(
            id='volatility',
            name='Volatility',
            category=CriteriaCategory.TECHNICAL,
            description='20-day realized volatility (lower for stability)',
            calc_function=lambda stock: stock.get('factors', {}).get('volatility_20d', 0.3),
            ideal_direction='lower',
            default_weight=0.5,
            enabled_by_default=False
        )

        # REGIME CRITERIA (from PROMPT 1)
        criteria['regime_confidence'] = Criterion(
            id='regime_confidence',
            name='Regime Confidence',
            category=CriteriaCategory.REGIME,
            description='Confidence in regime detection',
            calc_function=lambda stock: stock.get('regime', {}).get('confidence', 0),
            ideal_direction='higher',
            default_weight=1.5
        )

        criteria['trend_strength'] = Criterion(
            id='trend_strength',
            name='Trend Strength',
            category=CriteriaCategory.REGIME,
            description='Strength of current trend (0-10)',
            calc_function=lambda stock: stock.get('regime', {}).get('characteristics', {}).get('trend_strength', 0),
            ideal_direction='higher',
            default_weight=1.2
        )

        # HIERARCHY CRITERIA (from PROMPT 2)
        criteria['hierarchy_alignment'] = Criterion(
            id='hierarchy_alignment',
            name='Hierarchy Alignment',
            category=CriteriaCategory.HIERARCHY,
            description='Alignment with market hierarchy (0-100)',
            calc_function=lambda stock: stock.get('hierarchy', {}).get('overall_alignment', 50),
            ideal_direction='higher',
            default_weight=2.0
        )

        criteria['market_alignment'] = Criterion(
            id='market_alignment',
            name='Market Alignment',
            category=CriteriaCategory.HIERARCHY,
            description='Alignment with market indices',
            calc_function=lambda stock: stock.get('hierarchy', {}).get('market_alignment', 50),
            ideal_direction='higher',
            default_weight=1.5
        )

        criteria['sector_alignment'] = Criterion(
            id='sector_alignment',
            name='Sector Alignment',
            category=CriteriaCategory.HIERARCHY,
            description='Alignment with sector',
            calc_function=lambda stock: stock.get('hierarchy', {}).get('sector_alignment', 50),
            ideal_direction='higher',
            default_weight=1.3
        )

        return criteria

    def get_criterion(self, criterion_id: str) -> Criterion:
        """Get a specific criterion by ID."""
        return self.criteria.get(criterion_id)

    def get_by_category(self, category: CriteriaCategory) -> List[Criterion]:
        """Get all criteria in a category."""
        return [c for c in self.criteria.values() if c.category == category]

    def get_enabled_default(self) -> List[Criterion]:
        """Get criteria enabled by default."""
        return [c for c in self.criteria.values() if c.enabled_by_default]

    def list_all(self) -> List[Dict]:
        """List all criteria with metadata."""
        return [
            {
                'id': c.id,
                'name': c.name,
                'category': c.category.value,
                'description': c.description,
                'ideal_direction': c.ideal_direction,
                'default_weight': c.default_weight,
                'enabled_by_default': c.enabled_by_default
            }
            for c in self.criteria.values()
        ]

    def calculate_score(self, stock: Dict, criterion_id: str) -> float:
        """Calculate score for a stock on a specific criterion."""
        criterion = self.criteria.get(criterion_id)
        if not criterion:
            return 0.0

        try:
            return criterion.calc_function(stock)
        except Exception as e:
            return 0.0

    def calculate_all_scores(self, stock: Dict, enabled_criteria: List[str] = None) -> Dict[str, float]:
        """Calculate scores for all enabled criteria."""
        if enabled_criteria is None:
            enabled_criteria = [c.id for c in self.get_enabled_default()]

        scores = {}
        for criterion_id in enabled_criteria:
            if criterion_id in self.criteria:
                scores[criterion_id] = self.calculate_score(stock, criterion_id)

        return scores


# Module-level instance
_library = CriteriaLibrary()


def get_library() -> CriteriaLibrary:
    """Get the criteria library instance."""
    return _library


def list_criteria() -> List[Dict]:
    """List all available criteria."""
    return _library.list_all()


def get_criteria_by_category(category: str) -> List[Dict]:
    """Get criteria by category."""
    try:
        cat = CriteriaCategory(category)
        criteria = _library.get_by_category(cat)
        return [
            {
                'id': c.id,
                'name': c.name,
                'description': c.description,
                'default_weight': c.default_weight
            }
            for c in criteria
        ]
    except ValueError:
        return []
