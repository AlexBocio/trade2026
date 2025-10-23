# config.py - Configuration for Fractional Differentiation Engine

import os
import logging

class Config:
    """Configuration class for Fractional Differentiation service."""

    # Flask configuration
    HOST = os.getenv('FRACDIFF_HOST', '0.0.0.0')
    PORT = int(os.getenv('FRACDIFF_PORT', 5000))
    DEBUG = os.getenv('FRACDIFF_DEBUG', 'True').lower() == 'true'

    # Service metadata
    SERVICE_NAME = 'Fractional Differentiation Engine'
    VERSION = '1.0.0'

    # Fractional differentiation defaults
    DEFAULT_D = 0.5
    DEFAULT_THRESHOLD = 1e-5
    MIN_D = 0.0
    MAX_D = 1.0
    DEFAULT_D_STEP = 0.05

    # Stationarity test defaults
    DEFAULT_ALPHA = 0.05  # Significance level
    ADF_REGRESSION = 'c'  # 'c' (constant), 'ct' (constant + trend), 'ctt' (constant + trend + trend^2), 'nc' (no constant)
    ADF_MAXLAG = None     # Auto-select optimal lag
    KPSS_REGRESSION = 'c' # 'c' (constant), 'ct' (constant + trend)
    KPSS_NLAGS = 'auto'

    # Memory metrics defaults
    DEFAULT_LAGS = 20
    HURST_LAG_RANGE = (2, 100)

    # Data validation
    MIN_DATA_POINTS = 100
    MAX_DATA_POINTS = 100000

    # Logging configuration
    LOG_LEVEL = logging.INFO
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # Cache settings
    ENABLE_CACHE = True
    CACHE_TTL = 3600  # seconds

    @classmethod
    def validate(cls):
        """Validate configuration settings."""
        assert cls.PORT > 0 and cls.PORT < 65536, "Invalid port number"
        assert 0 <= cls.DEFAULT_D <= 1, "Default d must be between 0 and 1"
        assert cls.DEFAULT_THRESHOLD > 0, "Threshold must be positive"
        assert 0 < cls.DEFAULT_ALPHA < 1, "Alpha must be between 0 and 1"
        return True


# Initialize logging
logging.basicConfig(
    level=Config.LOG_LEVEL,
    format=Config.LOG_FORMAT
)

logger = logging.getLogger(__name__)
