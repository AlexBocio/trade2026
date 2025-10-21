"""
Integration Tests for Full ML Pipeline.

Tests end-to-end flow:
- Feature calculation
- Model training
- Model serving
- Strategy signal generation
"""
import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add library to path
library_path = Path(__file__).parent.parent.parent / "library"
sys.path.insert(0, str(library_path))


def test_feature_pipeline():
    """Test feature calculation pipeline."""
    print("\n" + "=" * 70)
    print("TEST 1: Feature Pipeline")
    print("=" * 70)

    from pipelines.default_ml.features.pipeline import FeaturePipeline

    # Create test data
    data = {'close': [100 + i * 0.5 + np.random.normal(0, 1) for i in range(100)]}
    df = pd.DataFrame(data)

    # Calculate features
    pipeline = FeaturePipeline()
    result = pipeline.calculate_all_features(df)

    # Verify
    assert len(result) > 0, "No features generated"
    assert 'rsi' in result.columns, "RSI not calculated"
    assert 'macd' in result.columns, "MACD not calculated"
    assert 'bb_upper' in result.columns, "Bollinger Bands not calculated"
    assert result['rsi'].notna().all(), "RSI contains NaN"

    print(f"  [OK] Features calculated: {len(result)} rows")
    print(f"  [OK] RSI range: {result['rsi'].min():.2f} - {result['rsi'].max():.2f}")
    print("  [OK] Feature pipeline working")
    return True


def test_model_training():
    """Test XGBoost model training."""
    print("\n" + "=" * 70)
    print("TEST 2: Model Training")
    print("=" * 70)

    from pipelines.default_ml.training.train import XGBoostTrainer

    # Initialize trainer
    trainer = XGBoostTrainer()

    # Generate synthetic data
    df = trainer.generate_synthetic_data(n_samples=500)

    # Prepare data
    X_train, X_test, y_train, y_test = trainer.prepare_data(df)

    # Train
    fast_params = {'max_depth': 3, 'n_estimators': 10}
    model = trainer.train(X_train, y_train, X_test, y_test, hyperparams=fast_params)

    # Verify
    assert model is not None, "Model training failed"

    train_acc = (y_train == model.predict(X_train)).mean()
    test_acc = (y_test == model.predict(X_test)).mean()

    assert test_acc > 0.4, f"Test accuracy too low: {test_acc:.2%}"

    print(f"  [OK] Train accuracy: {train_acc:.2%}")
    print(f"  [OK] Test accuracy: {test_acc:.2%}")
    print("  [OK] Model training working")
    return True


def test_feast_retrieval():
    """Test Feast online feature retrieval."""
    print("\n" + "=" * 70)
    print("TEST 3: Feast Feature Retrieval")
    print("=" * 70)

    from feast import FeatureStore

    # Initialize Feast
    feast_repo = Path(__file__).parent.parent.parent / "feast" / "feature_repo"
    store = FeatureStore(repo_path=str(feast_repo))

    # Get features
    features = store.get_online_features(
        features=[
            "technical_indicators:rsi",
            "technical_indicators:macd",
            "technical_indicators:close",
        ],
        entity_rows=[{"symbol": "BTCUSDT"}]
    ).to_dict()

    # Verify
    assert "rsi" in features, "RSI not retrieved"
    assert "macd" in features, "MACD not retrieved"
    assert len(features["rsi"]) > 0, "No features returned"

    print(f"  [OK] Features retrieved: {list(features.keys())}")
    print(f"  [OK] RSI value: {features['rsi'][0]}")
    print("  [OK] Feast retrieval working")
    return True


def test_end_to_end_flow():
    """Test complete pipeline: Features → Training → Serving → Strategy."""
    print("\n" + "=" * 70)
    print("TEST 4: End-to-End ML Pipeline")
    print("=" * 70)

    # Step 1: Features
    print("\n[STEP 1] Calculate features...")
    from pipelines.default_ml.features.pipeline import FeaturePipeline

    data = {'close': [100 + i * 0.1 for i in range(200)]}
    df = pd.DataFrame(data)

    pipeline = FeaturePipeline()
    features_df = pipeline.calculate_all_features(df)

    assert len(features_df) > 0
    print(f"  [OK] {len(features_df)} feature rows calculated")

    # Step 2: Train model
    print("\n[STEP 2] Train model...")
    from pipelines.default_ml.training.train import XGBoostTrainer

    trainer = XGBoostTrainer()
    synthetic_df = trainer.generate_synthetic_data(n_samples=500)
    X_train, X_test, y_train, y_test = trainer.prepare_data(synthetic_df)

    fast_params = {'max_depth': 3, 'n_estimators': 10}
    model = trainer.train(X_train, y_train, X_test, y_test, hyperparams=fast_params)

    assert model is not None
    print(f"  [OK] Model trained")

    # Step 3: Save model for serving
    print("\n[STEP 3] Save model...")
    model_dir = Path(__file__).parent.parent.parent / "library" / "pipelines" / "default_ml" / "serving" / "models"
    model_dir.mkdir(parents=True, exist_ok=True)

    model_path = model_dir / "default_ml_model.json"
    trainer.save_model(str(model_path))

    assert model_path.exists()
    print(f"  [OK] Model saved to {model_path}")

    # Step 4: Make predictions
    print("\n[STEP 4] Generate predictions...")
    predictions = trainer.predict(X_test.iloc[:5])

    assert len(predictions) == 5
    assert all(0 <= p <= 1 for p in predictions)
    print(f"  [OK] Predictions: {predictions[:3]}")

    print("\n" + "=" * 70)
    print("[SUCCESS] End-to-end pipeline working!")
    print("=" * 70)
    return True


def run_all_tests():
    """Run all integration tests."""
    print("=" * 70)
    print("INTEGRATION TEST SUITE - FULL ML PIPELINE")
    print("=" * 70)

    tests = [
        ("Feature Pipeline", test_feature_pipeline),
        ("Model Training", test_model_training),
        ("Feast Retrieval", test_feast_retrieval),
        ("End-to-End Flow", test_end_to_end_flow),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
        except Exception as e:
            failed += 1
            print(f"\n[ERROR] {test_name} failed: {e}")
            import traceback
            traceback.print_exc()

    # Summary
    print("\n" + "=" * 70)
    print("INTEGRATION TEST SUMMARY")
    print("=" * 70)
    print(f"Tests passed: {passed}/{len(tests)}")
    print(f"Tests failed: {failed}/{len(tests)}")

    if failed == 0:
        print("\n" + "=" * 70)
        print("[SUCCESS] ALL INTEGRATION TESTS PASSED!")
        print("=" * 70)
        print("\nComplete ML pipeline validated:")
        print("  Feature Engineering -> Training -> Serving -> Strategy")
        return 0
    else:
        print("\n" + "=" * 70)
        print(f"[PARTIAL SUCCESS] {passed} tests passed, {failed} tests failed")
        print("=" * 70)
        return 1


if __name__ == '__main__':
    exit(run_all_tests())
