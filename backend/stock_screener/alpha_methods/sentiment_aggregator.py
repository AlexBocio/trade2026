# sentiment_aggregator.py - Multi-Source Sentiment Aggregation
# Collects sentiment from news, social media, analyst ratings, and short interest

from typing import Dict, List, Optional
import numpy as np
from datetime import datetime, timedelta
import logging
import requests
import os
import yfinance as yf

logger = logging.getLogger(__name__)


class SentimentAggregator:
    """
    Aggregates sentiment from multiple sources.

    Sources:
    1. News Sentiment - Financial news articles (NewsAPI, Yahoo Finance)
    2. Social Sentiment - Reddit WallStreetBets, StockTwits
    3. Analyst Ratings - Upgrades, downgrades, target prices
    4. Short Interest - Short ratio, days to cover
    5. FinBERT NLP - Deep learning sentiment analysis
    """

    def __init__(self, mock_mode: bool = False):
        self.mock_mode = mock_mode
        self.newsapi_key = os.getenv('NEWSAPI_KEY', None)
        self.stocktwits_key = os.getenv('STOCKTWITS_API_KEY', None)

        # Try to initialize FinBERT model (optional)
        self.finbert_model = None
        self.finbert_tokenizer = None
        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            import torch
            self.finbert_tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
            self.finbert_model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
            self.torch = torch
            logger.info("FinBERT model loaded successfully")
        except Exception as e:
            logger.warning(f"FinBERT model not available: {e}")

    def aggregate_sentiment(self, symbol: str, lookback_days: int = 7) -> Dict:
        """
        Aggregate sentiment from all sources.

        Args:
            symbol: Stock symbol
            lookback_days: Days of history to analyze

        Returns:
            {
                'symbol': str,
                'aggregate_sentiment': str ('bullish', 'bearish', 'neutral'),
                'aggregate_score': float (-100 to 100),
                'news_sentiment': float (-100 to 100),
                'social_sentiment': float (-100 to 100),
                'analyst_sentiment': float (-100 to 100),
                'short_interest_sentiment': float (-100 to 100),
                'confidence': float (0-100),
                'sentiment_details': Dict,
                'analysis_date': str
            }
        """
        try:
            # Collect sentiment from each source
            news_data = self._get_news_sentiment(symbol, lookback_days)
            social_data = self._get_social_sentiment(symbol, lookback_days)
            analyst_data = self._get_analyst_sentiment(symbol)
            short_data = self._get_short_interest_sentiment(symbol)

            # Calculate weighted aggregate score
            aggregate_score = self._calculate_aggregate_score(
                news_data['score'],
                social_data['score'],
                analyst_data['score'],
                short_data['score']
            )

            # Determine aggregate sentiment
            if aggregate_score >= 30:
                aggregate_sentiment = 'bullish'
            elif aggregate_score <= -30:
                aggregate_sentiment = 'bearish'
            else:
                aggregate_sentiment = 'neutral'

            # Calculate confidence
            confidence = self._calculate_confidence(
                news_data, social_data, analyst_data, short_data
            )

            return {
                'symbol': symbol,
                'aggregate_sentiment': aggregate_sentiment,
                'aggregate_score': aggregate_score,
                'news_sentiment': news_data['score'],
                'social_sentiment': social_data['score'],
                'analyst_sentiment': analyst_data['score'],
                'short_interest_sentiment': short_data['score'],
                'confidence': confidence,
                'sentiment_details': {
                    'news': news_data['details'],
                    'social': social_data['details'],
                    'analyst': analyst_data['details'],
                    'short_interest': short_data['details']
                },
                'analysis_date': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error aggregating sentiment for {symbol}: {e}")
            return self._default_result(symbol)

    def _get_news_sentiment(self, symbol: str, lookback_days: int) -> Dict:
        """
        Get news sentiment from financial news sources.

        Returns score from -100 (very bearish) to 100 (very bullish)
        """
        try:
            if self.mock_mode:
                return self._mock_news_sentiment(symbol)

            # Try to fetch from Yahoo Finance news
            ticker = yf.Ticker(symbol)
            news = ticker.news

            if not news or len(news) == 0:
                return {'score': 0.0, 'details': {'available': False, 'article_count': 0}}

            # Analyze sentiment using FinBERT if available
            sentiments = []
            for article in news[:10]:  # Analyze up to 10 most recent articles
                title = article.get('title', '')
                if title and self.finbert_model:
                    sentiment_score = self._analyze_text_with_finbert(title)
                    sentiments.append(sentiment_score)

            if not sentiments:
                # Fallback to simple keyword analysis
                sentiments = self._simple_news_analysis(news[:10])

            avg_sentiment = np.mean(sentiments) if sentiments else 0.0

            return {
                'score': float(np.clip(avg_sentiment, -100, 100)),
                'details': {
                    'available': True,
                    'article_count': len(news),
                    'analyzed_count': len(sentiments),
                    'avg_sentiment': float(avg_sentiment)
                }
            }

        except Exception as e:
            logger.error(f"Error fetching news sentiment for {symbol}: {e}")
            return {'score': 0.0, 'details': {'available': False, 'error': str(e)}}

    def _analyze_text_with_finbert(self, text: str) -> float:
        """
        Analyze text sentiment using FinBERT model.

        Returns score from -100 to 100.
        """
        try:
            inputs = self.finbert_tokenizer(text, return_tensors="pt",
                                           padding=True, truncation=True, max_length=512)
            outputs = self.finbert_model(**inputs)
            probs = self.torch.nn.functional.softmax(outputs.logits, dim=-1)

            # FinBERT labels: [positive, negative, neutral]
            pos_prob = probs[0][0].item()
            neg_prob = probs[0][1].item()
            neu_prob = probs[0][2].item()

            # Convert to -100 to 100 scale
            sentiment_score = (pos_prob - neg_prob) * 100

            return float(sentiment_score)

        except Exception as e:
            logger.error(f"Error analyzing text with FinBERT: {e}")
            return 0.0

    def _simple_news_analysis(self, articles: List[Dict]) -> List[float]:
        """
        Simple keyword-based sentiment analysis as fallback.
        """
        bullish_keywords = ['surge', 'soar', 'rally', 'gain', 'upgrade', 'beat', 'strong',
                           'growth', 'profit', 'bullish', 'breakthrough', 'positive']
        bearish_keywords = ['fall', 'drop', 'plunge', 'decline', 'downgrade', 'miss',
                           'weak', 'loss', 'bearish', 'concern', 'negative', 'risk']

        sentiments = []
        for article in articles:
            title = article.get('title', '').lower()

            bullish_count = sum(1 for kw in bullish_keywords if kw in title)
            bearish_count = sum(1 for kw in bearish_keywords if kw in title)

            if bullish_count > bearish_count:
                sentiments.append(50.0)
            elif bearish_count > bullish_count:
                sentiments.append(-50.0)
            else:
                sentiments.append(0.0)

        return sentiments

    def _get_social_sentiment(self, symbol: str, lookback_days: int) -> Dict:
        """
        Get social media sentiment (Reddit, StockTwits).

        Returns score from -100 to 100.
        """
        try:
            if self.mock_mode:
                return self._mock_social_sentiment(symbol)

            # For now, return neutral sentiment
            # In production, would integrate with Reddit API and StockTwits API
            return {
                'score': 0.0,
                'details': {
                    'available': False,
                    'message': 'Social sentiment requires API keys'
                }
            }

        except Exception as e:
            logger.error(f"Error fetching social sentiment for {symbol}: {e}")
            return {'score': 0.0, 'details': {'available': False}}

    def _get_analyst_sentiment(self, symbol: str) -> Dict:
        """
        Get analyst sentiment from ratings and target prices.

        Returns score from -100 to 100.
        """
        try:
            if self.mock_mode:
                return self._mock_analyst_sentiment(symbol)

            ticker = yf.Ticker(symbol)
            recommendations = ticker.recommendations

            if recommendations is None or len(recommendations) == 0:
                return {'score': 0.0, 'details': {'available': False}}

            # Get recent recommendations (last 30 days)
            recent = recommendations.tail(10)

            # Map ratings to scores
            rating_scores = {
                'strong buy': 100,
                'buy': 70,
                'outperform': 60,
                'hold': 0,
                'neutral': 0,
                'underperform': -60,
                'sell': -70,
                'strong sell': -100
            }

            scores = []
            for _, row in recent.iterrows():
                rating = row['To Grade'].lower() if 'To Grade' in row else ''
                score = rating_scores.get(rating, 0)
                scores.append(score)

            avg_score = np.mean(scores) if scores else 0.0

            return {
                'score': float(np.clip(avg_score, -100, 100)),
                'details': {
                    'available': True,
                    'recommendation_count': len(recent),
                    'avg_score': float(avg_score)
                }
            }

        except Exception as e:
            logger.error(f"Error fetching analyst sentiment for {symbol}: {e}")
            return {'score': 0.0, 'details': {'available': False}}

    def _get_short_interest_sentiment(self, symbol: str) -> Dict:
        """
        Get sentiment from short interest data.

        High short interest can be bearish (or bullish for squeeze potential).

        Returns score from -100 to 100.
        """
        try:
            if self.mock_mode:
                return self._mock_short_interest_sentiment(symbol)

            ticker = yf.Ticker(symbol)
            info = ticker.info

            short_percent = info.get('shortPercentOfFloat', 0.0)

            if short_percent == 0.0:
                return {'score': 0.0, 'details': {'available': False}}

            # Score interpretation:
            # < 5%: Neutral to slightly bullish (0 to 20)
            # 5-10%: Neutral (-10 to 10)
            # 10-20%: Bearish (-40 to -10)
            # 20%+: Very bearish but squeeze potential (-60 to -20)

            if short_percent < 0.05:
                score = 20.0
            elif short_percent < 0.10:
                score = 0.0
            elif short_percent < 0.20:
                score = -30.0
            else:
                # High short interest - bearish but with squeeze potential
                score = -40.0

            return {
                'score': float(score),
                'details': {
                    'available': True,
                    'short_percent': float(short_percent * 100),
                    'interpretation': 'bearish' if score < 0 else 'neutral' if score == 0 else 'bullish'
                }
            }

        except Exception as e:
            logger.error(f"Error fetching short interest for {symbol}: {e}")
            return {'score': 0.0, 'details': {'available': False}}

    def _calculate_aggregate_score(self, news: float, social: float,
                                   analyst: float, short: float) -> float:
        """
        Calculate weighted aggregate sentiment score.

        Weights:
        - News: 30%
        - Social: 20%
        - Analyst: 35%
        - Short Interest: 15%
        """
        aggregate = (
            news * 0.30 +
            social * 0.20 +
            analyst * 0.35 +
            short * 0.15
        )

        return float(np.clip(aggregate, -100, 100))

    def _calculate_confidence(self, news_data: Dict, social_data: Dict,
                             analyst_data: Dict, short_data: Dict) -> float:
        """
        Calculate confidence score based on data availability.
        """
        sources_available = sum([
            news_data['details'].get('available', False),
            social_data['details'].get('available', False),
            analyst_data['details'].get('available', False),
            short_data['details'].get('available', False)
        ])

        # Base confidence from availability
        confidence = (sources_available / 4) * 100

        return float(np.clip(confidence, 0, 100))

    # Mock data methods for testing
    def _mock_news_sentiment(self, symbol: str) -> Dict:
        """Mock news sentiment data."""
        score = np.random.uniform(-50, 80)
        return {
            'score': float(score),
            'details': {
                'available': True,
                'article_count': 15,
                'analyzed_count': 10,
                'avg_sentiment': float(score)
            }
        }

    def _mock_social_sentiment(self, symbol: str) -> Dict:
        """Mock social sentiment data."""
        score = np.random.uniform(-40, 60)
        return {
            'score': float(score),
            'details': {
                'available': True,
                'reddit_mentions': np.random.randint(50, 500),
                'stocktwits_mentions': np.random.randint(100, 1000)
            }
        }

    def _mock_analyst_sentiment(self, symbol: str) -> Dict:
        """Mock analyst sentiment data."""
        score = np.random.uniform(-30, 70)
        return {
            'score': float(score),
            'details': {
                'available': True,
                'recommendation_count': 8,
                'avg_score': float(score)
            }
        }

    def _mock_short_interest_sentiment(self, symbol: str) -> Dict:
        """Mock short interest data."""
        short_percent = np.random.uniform(2, 25)
        if short_percent < 5:
            score = 20.0
        elif short_percent < 10:
            score = 0.0
        elif short_percent < 20:
            score = -30.0
        else:
            score = -40.0

        return {
            'score': float(score),
            'details': {
                'available': True,
                'short_percent': float(short_percent),
                'interpretation': 'bearish' if score < 0 else 'neutral' if score == 0 else 'bullish'
            }
        }

    def _default_result(self, symbol: str) -> Dict:
        """Return default result when analysis fails."""
        return {
            'symbol': symbol,
            'aggregate_sentiment': 'neutral',
            'aggregate_score': 0.0,
            'news_sentiment': 0.0,
            'social_sentiment': 0.0,
            'analyst_sentiment': 0.0,
            'short_interest_sentiment': 0.0,
            'confidence': 0.0,
            'sentiment_details': {
                'news': {'available': False},
                'social': {'available': False},
                'analyst': {'available': False},
                'short_interest': {'available': False}
            },
            'analysis_date': datetime.now().isoformat()
        }


# Module-level instance
_aggregator = SentimentAggregator()


def aggregate_sentiment(symbol: str, lookback_days: int = 7) -> Dict:
    """Convenience function for sentiment aggregation."""
    return _aggregator.aggregate_sentiment(symbol, lookback_days)
