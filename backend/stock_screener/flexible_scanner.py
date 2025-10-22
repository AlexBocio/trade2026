# flexible_scanner.py - Flexible Custom Scanner Engine
# Allows user-configurable criteria, weights, and ranking methods

from typing import Dict, List, Optional
import numpy as np
import pandas as pd
from scipy import stats
import logging
from criteria_library import CriteriaLibrary, RankingMethod, get_library

logger = logging.getLogger(__name__)


class FlexibleScanner:
    """
    Flexible scanner with customizable criteria and ranking.

    Features:
    - Toggle criteria on/off
    - Custom weights per criterion
    - Multiple ranking methods
    - Hierarchy alignment filtering
    - Divergence-based filtering
    """

    def __init__(self):
        self.library = get_library()

    def scan(self,
             stocks: List[Dict],
             enabled_criteria: List[str] = None,
             custom_weights: Dict[str, float] = None,
             ranking_method: str = 'composite_score',
             min_hierarchy_alignment: float = None,
             filter_divergent: bool = False) -> List[Dict]:
        """
        Scan stocks with custom criteria and ranking.

        Args:
            stocks: List of stock dicts with factors/regime/hierarchy data
            enabled_criteria: List of criterion IDs to use (None = default)
            custom_weights: Dict of criterion_id -> weight overrides
            ranking_method: 'composite_score', 'percentile_rank', 'z_score', 'pareto_optimal'
            min_hierarchy_alignment: Minimum hierarchy alignment score (0-100)
            filter_divergent: Remove stocks divergent from hierarchy

        Returns:
            Ranked list of stocks with scores
        """
        if not stocks:
            return []

        # Determine enabled criteria
        if enabled_criteria is None:
            enabled_criteria = [c.id for c in self.library.get_enabled_default()]

        # Apply hierarchy filters if specified
        if min_hierarchy_alignment is not None or filter_divergent:
            stocks = self._apply_hierarchy_filters(
                stocks, min_hierarchy_alignment, filter_divergent
            )

        # Calculate criterion scores for each stock
        scored_stocks = []
        for stock in stocks:
            stock_scores = self.library.calculate_all_scores(stock, enabled_criteria)
            stock['criterion_scores'] = stock_scores
            scored_stocks.append(stock)

        # Get weights (custom or default)
        weights = self._get_weights(enabled_criteria, custom_weights)

        # Apply ranking method
        if ranking_method == 'composite_score':
            ranked = self._rank_composite_score(scored_stocks, weights)
        elif ranking_method == 'percentile_rank':
            ranked = self._rank_percentile(scored_stocks, weights)
        elif ranking_method == 'z_score':
            ranked = self._rank_z_score(scored_stocks, weights)
        elif ranking_method == 'pareto_optimal':
            ranked = self._rank_pareto_optimal(scored_stocks, weights)
        else:
            # Default to composite
            ranked = self._rank_composite_score(scored_stocks, weights)

        return ranked

    def _get_weights(self, enabled_criteria: List[str],
                    custom_weights: Dict[str, float] = None) -> Dict[str, float]:
        """Get weights for criteria (custom overrides default)."""
        weights = {}
        for criterion_id in enabled_criteria:
            criterion = self.library.get_criterion(criterion_id)
            if criterion:
                # Use custom weight if provided, else default
                weights[criterion_id] = (
                    custom_weights.get(criterion_id, criterion.default_weight)
                    if custom_weights else criterion.default_weight
                )
        return weights

    def _apply_hierarchy_filters(self, stocks: List[Dict],
                                 min_alignment: float = None,
                                 filter_divergent: bool = False) -> List[Dict]:
        """Apply hierarchy-based filters."""
        filtered = []
        for stock in stocks:
            hierarchy = stock.get('hierarchy', {})

            # Check minimum alignment
            if min_alignment is not None:
                alignment = hierarchy.get('overall_alignment', 0)
                if alignment < min_alignment:
                    continue

            # Check divergence
            if filter_divergent:
                alignment_status = hierarchy.get('hierarchy_alignment', 'UNKNOWN')
                if alignment_status == 'DIVERGENT':
                    continue

            filtered.append(stock)

        return filtered

    def _rank_composite_score(self, stocks: List[Dict],
                              weights: Dict[str, float]) -> List[Dict]:
        """
        Rank by weighted composite score.

        Normalizes each criterion, applies weights, sums.
        """
        # Collect all scores by criterion
        all_scores = {crit: [] for crit in weights.keys()}
        for stock in stocks:
            for crit in weights.keys():
                score = stock['criterion_scores'].get(crit, 0)
                all_scores[crit].append(score)

        # Normalize each criterion to [0, 1]
        normalized = {crit: [] for crit in weights.keys()}
        for crit in weights.keys():
            scores = all_scores[crit]
            criterion = self.library.get_criterion(crit)

            if not scores or all(s == scores[0] for s in scores):
                # All same, no normalization needed
                normalized[crit] = [0.5] * len(stocks)
                continue

            min_score = min(scores)
            max_score = max(scores)

            for score in scores:
                if max_score == min_score:
                    norm = 0.5
                else:
                    norm = (score - min_score) / (max_score - min_score)

                # Invert if ideal direction is 'lower'
                if criterion and criterion.ideal_direction == 'lower':
                    norm = 1.0 - norm

                normalized[crit].append(norm)

        # Calculate composite scores
        for i, stock in enumerate(stocks):
            composite = 0.0
            total_weight = sum(weights.values())

            for crit, weight in weights.items():
                composite += normalized[crit][i] * weight

            stock['composite_score'] = composite / total_weight if total_weight > 0 else 0
            stock['rank_method'] = 'composite_score'

        # Sort by composite score (descending)
        stocks.sort(key=lambda x: x['composite_score'], reverse=True)

        # Add rank
        for i, stock in enumerate(stocks):
            stock['rank'] = i + 1

        return stocks

    def _rank_percentile(self, stocks: List[Dict],
                        weights: Dict[str, float]) -> List[Dict]:
        """
        Rank by percentile scores.

        Converts each score to percentile, then weighted average.
        """
        # Collect all scores by criterion
        all_scores = {crit: [] for crit in weights.keys()}
        for stock in stocks:
            for crit in weights.keys():
                score = stock['criterion_scores'].get(crit, 0)
                all_scores[crit].append(score)

        # Calculate percentiles
        percentiles = {crit: [] for crit in weights.keys()}
        for crit in weights.keys():
            scores = np.array(all_scores[crit])
            criterion = self.library.get_criterion(crit)

            for score in scores:
                # Calculate percentile
                if criterion and criterion.ideal_direction == 'lower':
                    # For "lower is better", invert
                    pct = 100 - stats.percentileofscore(scores, score)
                else:
                    pct = stats.percentileofscore(scores, score)

                percentiles[crit].append(pct)

        # Calculate weighted percentile scores
        for i, stock in enumerate(stocks):
            weighted_pct = 0.0
            total_weight = sum(weights.values())

            for crit, weight in weights.items():
                weighted_pct += percentiles[crit][i] * weight

            stock['percentile_score'] = weighted_pct / total_weight if total_weight > 0 else 0
            stock['rank_method'] = 'percentile_rank'

        # Sort by percentile score (descending)
        stocks.sort(key=lambda x: x['percentile_score'], reverse=True)

        # Add rank
        for i, stock in enumerate(stocks):
            stock['rank'] = i + 1

        return stocks

    def _rank_z_score(self, stocks: List[Dict],
                     weights: Dict[str, float]) -> List[Dict]:
        """
        Rank by standardized (z-score) composite.

        Standardizes each criterion, applies weights, sums.
        """
        # Collect all scores by criterion
        all_scores = {crit: [] for crit in weights.keys()}
        for stock in stocks:
            for crit in weights.keys():
                score = stock['criterion_scores'].get(crit, 0)
                all_scores[crit].append(score)

        # Calculate z-scores
        z_scores = {crit: [] for crit in weights.keys()}
        for crit in weights.keys():
            scores = np.array(all_scores[crit])
            criterion = self.library.get_criterion(crit)

            mean = np.mean(scores)
            std = np.std(scores)

            for score in scores:
                if std == 0:
                    z = 0
                else:
                    z = (score - mean) / std

                # Invert if ideal direction is 'lower'
                if criterion and criterion.ideal_direction == 'lower':
                    z = -z

                z_scores[crit].append(z)

        # Calculate weighted z-score composite
        for i, stock in enumerate(stocks):
            weighted_z = 0.0
            total_weight = sum(weights.values())

            for crit, weight in weights.items():
                weighted_z += z_scores[crit][i] * weight

            stock['z_score'] = weighted_z / total_weight if total_weight > 0 else 0
            stock['rank_method'] = 'z_score'

        # Sort by z-score (descending)
        stocks.sort(key=lambda x: x['z_score'], reverse=True)

        # Add rank
        for i, stock in enumerate(stocks):
            stock['rank'] = i + 1

        return stocks

    def _rank_pareto_optimal(self, stocks: List[Dict],
                            weights: Dict[str, float]) -> List[Dict]:
        """
        Rank by Pareto optimality.

        Finds Pareto frontier, then ranks by dominated count.
        """
        # Normalize criteria first
        all_scores = {crit: [] for crit in weights.keys()}
        for stock in stocks:
            for crit in weights.keys():
                score = stock['criterion_scores'].get(crit, 0)
                all_scores[crit].append(score)

        # Normalize to [0, 1]
        normalized = {crit: [] for crit in weights.keys()}
        for crit in weights.keys():
            scores = all_scores[crit]
            criterion = self.library.get_criterion(crit)

            if not scores or all(s == scores[0] for s in scores):
                normalized[crit] = [0.5] * len(stocks)
                continue

            min_score = min(scores)
            max_score = max(scores)

            for score in scores:
                if max_score == min_score:
                    norm = 0.5
                else:
                    norm = (score - min_score) / (max_score - min_score)

                if criterion and criterion.ideal_direction == 'lower':
                    norm = 1.0 - norm

                normalized[crit].append(norm)

        # Build score vectors
        score_vectors = []
        for i in range(len(stocks)):
            vec = [normalized[crit][i] for crit in weights.keys()]
            score_vectors.append(vec)

        # Calculate domination count for each stock
        for i, stock in enumerate(stocks):
            dominated_by_count = 0
            dominates_count = 0

            for j in range(len(stocks)):
                if i == j:
                    continue

                # Check if j dominates i
                if self._dominates(score_vectors[j], score_vectors[i]):
                    dominated_by_count += 1

                # Check if i dominates j
                if self._dominates(score_vectors[i], score_vectors[j]):
                    dominates_count += 1

            stock['dominated_by_count'] = dominated_by_count
            stock['dominates_count'] = dominates_count
            stock['pareto_score'] = dominates_count - dominated_by_count
            stock['rank_method'] = 'pareto_optimal'

        # Sort by pareto score (higher is better)
        stocks.sort(key=lambda x: x['pareto_score'], reverse=True)

        # Add rank
        for i, stock in enumerate(stocks):
            stock['rank'] = i + 1

        return stocks

    def _dominates(self, vec1: List[float], vec2: List[float]) -> bool:
        """Check if vec1 Pareto-dominates vec2."""
        if len(vec1) != len(vec2):
            return False

        at_least_one_better = False
        for v1, v2 in zip(vec1, vec2):
            if v1 < v2:
                return False  # vec1 is worse in this dimension
            if v1 > v2:
                at_least_one_better = True

        return at_least_one_better


# Module-level instance
_scanner = FlexibleScanner()


def scan_stocks(stocks: List[Dict],
                enabled_criteria: List[str] = None,
                custom_weights: Dict[str, float] = None,
                ranking_method: str = 'composite_score',
                min_hierarchy_alignment: float = None,
                filter_divergent: bool = False) -> List[Dict]:
    """Convenience function for flexible scanning."""
    return _scanner.scan(
        stocks, enabled_criteria, custom_weights,
        ranking_method, min_hierarchy_alignment, filter_divergent
    )
