"""
Comprehensive Test Suite for XGBoost Training Pipeline.

Tests training, prediction, model persistence, and various scenarios.
"""
import sys
from pathlib import Path
import tempfile
import shutil

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from train import XGBoostTrainer


def test_synthetic_data_generation():
    """Test synthetic data generation with different trends."""
    print("\n" + "="*70)
    print("TEST: Synthetic Data Generation")
    print("="*70)

    trainer = XGBoostTrainer()

    trends = ['up', 'down', 'sideways', 'mixed']
    for trend in trends:
        df = trainer.generate_synthetic_data(n_samples=100, trend=trend)

        print(f"\n[{trend.upper()}]")
        print(f"  Rows: {len(df)}")
        print(f"  Columns: {list(df.columns)}")
        print(f"  Price range: {df['close'].min():.2f} - {df['close'].max():.2f}")
        print(f"  RSI range: {df['rsi'].min():.2f} - {df['rsi'].max():.2f}")

        # Validate
        assert len(df) == 100, f"Expected 100 rows, got {len(df)}"
        assert 'close' in df.columns, "Missing 'close' column"
        assert 'rsi' in df.columns, "Missing 'rsi' column"
        assert (df['rsi'] >= 0).all() and (df['rsi'] <= 100).all(), "RSI out of range"

    print("\n[OK] All trend scenarios generated successfully")


def test_data_preparation():
    """Test data preparation and splitting."""
    print("\n" + "="*70)
    print("TEST: Data Preparation")
    print("="*70)

    trainer = XGBoostTrainer()
    df = trainer.generate_synthetic_data(n_samples=500)

    # Test different test sizes
    for test_size in [0.2, 0.3]:
        X_train, X_test, y_train, y_test = trainer.prepare_data(df, test_size=test_size)

        print(f"\n[test_size={test_size}]")
        print(f"  X_train shape: {X_train.shape}")
        print(f"  X_test shape: {X_test.shape}")
        print(f"  y_train shape: {y_train.shape}")
        print(f"  y_test shape: {y_test.shape}")

        # Validate
        expected_test_count = int(len(df) * test_size)
        assert len(X_test) == len(y_test), "X_test and y_test size mismatch"
        assert len(X_train) == len(y_train), "X_train and y_train size mismatch"
        assert abs(len(X_test) - expected_test_count) < 10, "Test size incorrect"

    print("\n[OK] Data preparation working correctly")


def test_training_with_different_sample_sizes():
    """Test training with varying dataset sizes."""
    print("\n" + "="*70)
    print("TEST: Training with Different Sample Sizes")
    print("="*70)

    trainer = XGBoostTrainer()

    sample_sizes = [200, 500, 1000]

    for n_samples in sample_sizes:
        print(f"\n[n_samples={n_samples}]")

        # Generate data
        df = trainer.generate_synthetic_data(n_samples=n_samples)
        X_train, X_test, y_train, y_test = trainer.prepare_data(df)

        # Train with faster params for testing
        fast_params = {
            'max_depth': 3,
            'n_estimators': 20,
            'learning_rate': 0.2
        }

        model = trainer.train(X_train, y_train, X_test, y_test, hyperparams=fast_params)

        assert model is not None, "Model training failed"
        print(f"  [OK] Model trained successfully with {n_samples} samples")

    print("\n[OK] Training works across different dataset sizes")


def test_model_persistence():
    """Test model saving and loading."""
    print("\n" + "="*70)
    print("TEST: Model Persistence (Save/Load)")
    print("="*70)

    # Create temporary directory for model
    temp_dir = tempfile.mkdtemp()

    try:
        model_path = Path(temp_dir) / "test_model.json"

        # Train a model
        trainer = XGBoostTrainer()
        df = trainer.generate_synthetic_data(n_samples=300)
        X_train, X_test, y_train, y_test = trainer.prepare_data(df)

        fast_params = {'max_depth': 3, 'n_estimators': 10}
        trainer.train(X_train, y_train, X_test, y_test, hyperparams=fast_params)

        # Save model
        print(f"\n[SAVE] Saving model to {model_path}")
        trainer.save_model(str(model_path))

        assert model_path.exists(), "Model file not created"
        print(f"  Model file size: {model_path.stat().st_size} bytes")

        # Get predictions from original model
        original_pred = trainer.predict(X_test.iloc[:10])
        print(f"  Original predictions (first 5): {original_pred[:5]}")

        # Load model in new trainer
        print(f"\n[LOAD] Loading model from {model_path}")
        new_trainer = XGBoostTrainer()
        new_trainer.load_model(str(model_path))

        # Get predictions from loaded model
        loaded_pred = new_trainer.predict(X_test.iloc[:10])
        print(f"  Loaded predictions (first 5): {loaded_pred[:5]}")

        # Verify predictions match
        import numpy as np
        assert np.allclose(original_pred, loaded_pred, rtol=1e-5), \
            "Predictions from loaded model don't match original"

        print(f"\n[OK] Model saved and loaded correctly")

    finally:
        # Cleanup
        shutil.rmtree(temp_dir)
        print(f"[INFO] Cleaned up temporary directory")


def test_prediction_edge_cases():
    """Test predictions with edge case inputs."""
    print("\n" + "="*70)
    print("TEST: Prediction Edge Cases")
    print("="*70)

    # Train model
    trainer = XGBoostTrainer()
    df = trainer.generate_synthetic_data(n_samples=500)
    X_train, X_test, y_train, y_test = trainer.prepare_data(df)

    fast_params = {'max_depth': 3, 'n_estimators': 10}
    trainer.train(X_train, y_train, X_test, y_test, hyperparams=fast_params)

    # Test 1: Single sample prediction
    print("\n[TEST] Single sample prediction")
    single_sample = X_test.iloc[[0]]
    pred = trainer.predict(single_sample)
    assert len(pred) == 1, "Single prediction failed"
    assert 0 <= pred[0] <= 1, f"Prediction out of range: {pred[0]}"
    print(f"  Prediction: {pred[0]:.4f} [OK]")

    # Test 2: Batch prediction
    print("\n[TEST] Batch prediction (100 samples)")
    batch = X_test.iloc[:100]
    preds = trainer.predict(batch)
    assert len(preds) == 100, "Batch prediction failed"
    assert (preds >= 0).all() and (preds <= 1).all(), "Some predictions out of range"
    print(f"  Min: {preds.min():.4f}, Max: {preds.max():.4f}, Mean: {preds.mean():.4f} [OK]")

    # Test 3: Extreme feature values
    print("\n[TEST] Extreme feature values")
    extreme_sample = X_test.iloc[[0]].copy()
    extreme_sample['rsi'] = 100.0  # Maximum RSI
    extreme_sample['macd'] = 10.0  # High MACD
    pred_extreme = trainer.predict(extreme_sample)
    assert 0 <= pred_extreme[0] <= 1, "Prediction with extreme values failed"
    print(f"  Prediction with extreme values: {pred_extreme[0]:.4f} [OK]")

    print("\n[OK] All prediction edge cases handled")


def test_class_balance_handling():
    """Test model handles different class balances."""
    print("\n" + "="*70)
    print("TEST: Class Balance Handling")
    print("="*70)

    trainer = XGBoostTrainer()

    # Generate data with different trends (affects class balance)
    for trend in ['up', 'down', 'mixed']:
        print(f"\n[{trend.upper()} trend]")

        df = trainer.generate_synthetic_data(n_samples=400, trend=trend)
        X_train, X_test, y_train, y_test = trainer.prepare_data(df)

        # Check class distribution
        train_dist = y_train.value_counts()
        test_dist = y_test.value_counts()

        print(f"  Train distribution: {train_dist.to_dict()}")
        print(f"  Test distribution: {test_dist.to_dict()}")

        # Train model
        fast_params = {'max_depth': 3, 'n_estimators': 10}
        model = trainer.train(X_train, y_train, X_test, y_test, hyperparams=fast_params)

        assert model is not None, f"Training failed for {trend} trend"
        print(f"  [OK] Model trained successfully")

    print("\n[OK] Handles different class balances")


def run_all_tests():
    """Run all tests."""
    print("="*70)
    print("COMPREHENSIVE TEST SUITE - XGBOOST TRAINING")
    print("="*70)

    tests = [
        test_synthetic_data_generation,
        test_data_preparation,
        test_training_with_different_sample_sizes,
        test_model_persistence,
        test_prediction_edge_cases,
        test_class_balance_handling
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"\n[ERROR] {test_func.__name__} failed: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests passed: {passed}")
    print(f"Tests failed: {failed}")

    if failed == 0:
        print("\n" + "="*70)
        print("[SUCCESS] ALL TESTS PASSED!")
        print("="*70)
        return 0
    else:
        print("\n" + "="*70)
        print(f"[FAILURE] {failed} test(s) failed")
        print("="*70)
        return 1


if __name__ == '__main__':
    exit(run_all_tests())
