# config.py - Configuration for Simulation Engine

import os
import logging

class Config:
    """Configuration class for Simulation Engine service."""

    # Flask configuration
    HOST = os.getenv('SIMULATION_HOST', '0.0.0.0')
    PORT = int(os.getenv('SIMULATION_PORT', 5000))
    DEBUG = os.getenv('SIMULATION_DEBUG', 'True').lower() == 'true'

    # Service metadata
    SERVICE_NAME = 'Simulation Engine'
    VERSION = '1.0.0'

    # Simulation defaults
    DEFAULT_N_SIMULATIONS = 1000
    DEFAULT_BLOCK_SIZE = 10
    DEFAULT_CONFIDENCE_LEVEL = 0.95

    # Walk-forward defaults
    DEFAULT_TRAIN_SIZE = 252  # 1 year
    DEFAULT_TEST_SIZE = 63    # 3 months
    DEFAULT_STEP_SIZE = 21    # 1 month

    # Monte Carlo defaults
    GARCH_P = 1
    GARCH_Q = 1
    DEFAULT_N_REGIMES = 2

    # GAN/VAE defaults
    GAN_EPOCHS = 100
    GAN_BATCH_SIZE = 32
    GAN_LEARNING_RATE = 0.0002
    VAE_LATENT_DIM = 10

    # Historical scenarios
    SCENARIOS = {
        '2008_crisis': {'start': '2008-09-01', 'end': '2009-03-31', 'name': '2008 Financial Crisis'},
        'covid_crash': {'start': '2020-02-15', 'end': '2020-04-30', 'name': 'COVID-19 Crash'},
        'dotcom_bubble': {'start': '2000-03-01', 'end': '2002-10-31', 'name': 'Dot-com Bubble'},
        '1987_crash': {'start': '1987-10-01', 'end': '1987-11-30', 'name': 'Black Monday 1987'},
        'volmageddon': {'start': '2018-02-01', 'end': '2018-02-28', 'name': 'Volmageddon 2018'},
        'repo_crisis': {'start': '2019-09-01', 'end': '2019-10-31', 'name': 'Repo Crisis 2019'}
    }

    # Logging configuration
    LOG_LEVEL = logging.INFO
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # Validation thresholds
    MAX_SIMULATIONS = 10000
    MIN_BLOCK_SIZE = 2
    MAX_BLOCK_SIZE = 100
    MIN_DATA_POINTS = 50

    # Cross-validation
    DEFAULT_CV_SPLITS = 5
    DEFAULT_EMBARGO_DAYS = 5

    # Cache settings
    ENABLE_CACHE = True
    CACHE_TTL = 3600  # seconds

    @classmethod
    def validate(cls):
        """Validate configuration settings."""
        assert cls.PORT > 0 and cls.PORT < 65536, "Invalid port number"
        assert cls.DEFAULT_N_SIMULATIONS > 0, "N simulations must be positive"
        assert cls.MIN_BLOCK_SIZE > 0, "Min block size must be positive"
        return True


# Initialize logging
logging.basicConfig(
    level=Config.LOG_LEVEL,
    format=Config.LOG_FORMAT
)

logger = logging.getLogger(__name__)
