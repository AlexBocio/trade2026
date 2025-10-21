-- ==================================================
-- Sample Data for Testing
-- ==================================================

-- Insert sample strategy
INSERT INTO entities (
    name,
    type,
    category,
    description,
    version,
    author,
    tags,
    status,
    health_status,
    config,
    parameters
) VALUES (
    'default_ml_strategy',
    'strategy',
    'ml_based',
    'Default XGBoost-based trading strategy with RSI, MACD, and Bollinger Bands',
    '1.0.0',
    'Trade2026 Team',
    ARRAY['ml', 'xgboost', 'technical_analysis'],
    'registered',
    'unknown',
    '{"model_type": "xgboost", "features": ["rsi", "macd", "bbands"]}'::jsonb,
    '{"n_estimators": 100, "max_depth": 5, "learning_rate": 0.1}'::jsonb
);

-- Insert sample pipeline
INSERT INTO entities (
    name,
    type,
    category,
    description,
    version,
    author,
    tags,
    status,
    health_status,
    config
) VALUES (
    'default_ml_pipeline',
    'pipeline',
    'feature_engineering',
    'Feature engineering pipeline for default ML strategy',
    '1.0.0',
    'Trade2026 Team',
    ARRAY['pipeline', 'features', 'preprocessing'],
    'registered',
    'unknown',
    '{"features": ["RSI", "MACD", "BBands"], "lookback": 20}'::jsonb
);

-- Insert sample event
INSERT INTO events (
    event_type,
    event_category,
    severity,
    entity_id,
    message,
    details,
    source
) VALUES (
    'entity_registered',
    'entity_lifecycle',
    'info',
    (SELECT entity_id FROM entities WHERE name = 'default_ml_strategy'),
    'Default ML strategy registered in library',
    '{"version": "1.0.0", "author": "Trade2026 Team"}'::jsonb,
    'init_script'
);

-- ==================================================
-- END OF SAMPLE DATA
-- ==================================================
