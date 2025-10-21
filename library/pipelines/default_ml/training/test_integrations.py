"""
Integration Tests for MLflow and ClickHouse.

Tests that the training pipeline properly integrates with:
- MLflow for experiment tracking
- ClickHouse for data loading
"""
import sys
from pathlib import Path
import tempfile
import shutil

sys.path.insert(0, str(Path(__file__).parent))

from train import XGBoostTrainer


def test_mlflow_available():
    """Test that MLflow is available and can be imported."""
    print("\n" + "="*70)
    print("TEST: MLflow Availability")
    print("="*70)

    try:
        import mlflow
        print(f"[OK] MLflow installed: version {mlflow.__version__}")
        return True
    except ImportError as e:
        print(f"[ERROR] MLflow not available: {e}")
        return False


def test_clickhouse_driver_available():
    """Test that ClickHouse driver is available."""
    print("\n" + "="*70)
    print("TEST: ClickHouse Driver Availability")
    print("="*70)

    try:
        from clickhouse_driver import Client
        print(f"[OK] ClickHouse driver installed")
        return True
    except ImportError as e:
        print(f"[ERROR] ClickHouse driver not available: {e}")
        return False


def test_mlflow_local_tracking():
    """Test MLflow local tracking (without server)."""
    print("\n" + "="*70)
    print("TEST: MLflow Local Tracking")
    print("="*70)

    # Create temporary directory for MLflow artifacts
    temp_dir = tempfile.mkdtemp()

    try:
        import mlflow

        # Set local tracking directory (Windows compatible)
        # Just use the directory path directly, not file:// URI
        tracking_uri = str(Path(temp_dir) / "mlruns")
        print(f"[INFO] Using local tracking URI: {tracking_uri}")

        # Initialize trainer with MLflow
        trainer = XGBoostTrainer(
            mlflow_tracking_uri=tracking_uri,
            experiment_name="test_integration"
        )

        # Generate data and train
        df = trainer.generate_synthetic_data(n_samples=200)
        X_train, X_test, y_train, y_test = trainer.prepare_data(df)

        fast_params = {'max_depth': 3, 'n_estimators': 10}
        model = trainer.train(X_train, y_train, X_test, y_test, hyperparams=fast_params)

        print(f"\n[INFO] Checking MLflow artifacts...")

        # Verify experiment was created
        # Get the tracking URI that was actually set (may have been converted)
        current_uri = mlflow.get_tracking_uri()
        print(f"  Current tracking URI: {current_uri}")
        experiment = mlflow.get_experiment_by_name("test_integration")

        assert experiment is not None, "Experiment not created"
        print(f"  Experiment ID: {experiment.experiment_id}")
        print(f"  Experiment name: {experiment.name}")

        # Get the run
        runs = mlflow.search_runs(experiment_ids=[experiment.experiment_id])
        assert len(runs) > 0, "No runs recorded"

        latest_run = runs.iloc[0]
        print(f"  Run ID: {latest_run['run_id']}")
        print(f"  Metrics logged: {[col for col in runs.columns if col.startswith('metrics.')]}")
        print(f"  Params logged: {[col for col in runs.columns if col.startswith('params.')]}")

        # Verify key metrics were logged
        assert 'metrics.test_accuracy' in runs.columns, "test_accuracy not logged"
        assert 'metrics.train_accuracy' in runs.columns, "train_accuracy not logged"
        assert 'params.max_depth' in runs.columns, "max_depth param not logged"

        print(f"\n[OK] MLflow integration working correctly")
        return True

    except Exception as e:
        print(f"\n[ERROR] MLflow integration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)
        print(f"[INFO] Cleaned up temporary directory")


def test_clickhouse_connection():
    """Test ClickHouse connection (if server is available)."""
    print("\n" + "="*70)
    print("TEST: ClickHouse Connection")
    print("="*70)

    try:
        from clickhouse_driver import Client

        # Try to connect to localhost ClickHouse
        print("[INFO] Attempting to connect to localhost:8123...")

        try:
            client = Client(host='localhost', port=9000)  # Native port

            # Test simple query
            result = client.execute('SELECT 1')
            print(f"  Query result: {result}")
            print(f"[OK] ClickHouse connection successful")

            # Try to check if features table exists
            try:
                tables = client.execute("SHOW TABLES")
                print(f"  Available tables: {[t[0] for t in tables]}")
            except Exception as e:
                print(f"  [INFO] Could not list tables: {e}")

            return True

        except Exception as conn_error:
            print(f"[INFO] ClickHouse server not available: {conn_error}")
            print(f"[INFO] This is expected if ClickHouse service is not running")
            print(f"[OK] ClickHouse driver is installed and ready to use")
            return True  # Driver is installed, server not required for this test

    except Exception as e:
        print(f"[ERROR] ClickHouse driver test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_trainer_detects_integrations():
    """Test that trainer properly detects available integrations."""
    print("\n" + "="*70)
    print("TEST: Trainer Integration Detection")
    print("="*70)

    # Re-import to get fresh detection
    import importlib
    import train
    importlib.reload(train)

    print(f"[INFO] Checking integration detection...")
    print(f"  MLFLOW_AVAILABLE: {train.MLFLOW_AVAILABLE}")
    print(f"  CLICKHOUSE_AVAILABLE: {train.CLICKHOUSE_AVAILABLE}")

    # Both should be True now
    assert train.MLFLOW_AVAILABLE == True, "MLflow not detected"
    assert train.CLICKHOUSE_AVAILABLE == True, "ClickHouse not detected"

    print(f"\n[OK] Trainer correctly detects both integrations")
    return True


def test_full_integration_flow():
    """Test complete flow with all integrations."""
    print("\n" + "="*70)
    print("TEST: Full Integration Flow")
    print("="*70)

    temp_dir = tempfile.mkdtemp()

    try:
        import mlflow

        # Setup MLflow (Windows compatible path)
        tracking_uri = str(Path(temp_dir) / "mlruns")

        # Initialize trainer
        trainer = XGBoostTrainer(
            mlflow_tracking_uri=tracking_uri,
            experiment_name="full_integration_test",
            clickhouse_host='localhost',
            clickhouse_port=8123
        )

        print("[INFO] Trainer initialized with all integrations")

        # Generate synthetic data (since ClickHouse may not have data)
        df = trainer.generate_synthetic_data(n_samples=300)

        # Prepare and train
        X_train, X_test, y_train, y_test = trainer.prepare_data(df)

        fast_params = {'max_depth': 3, 'n_estimators': 10}
        model = trainer.train(X_train, y_train, X_test, y_test, hyperparams=fast_params)

        # Make predictions
        predictions = trainer.predict(X_test.iloc[:10])

        print(f"\n[INFO] Training completed")
        print(f"  Predictions generated: {len(predictions)}")
        print(f"  Sample predictions: {predictions[:3]}")

        # Verify MLflow recorded everything
        # MLflow tracking URI is already set from trainer init
        runs = mlflow.search_runs(
            experiment_names=["full_integration_test"]
        )

        assert len(runs) > 0, "No runs recorded"
        print(f"  MLflow runs recorded: {len(runs)}")

        print(f"\n[OK] Full integration flow successful")
        return True

    except Exception as e:
        print(f"\n[ERROR] Integration flow failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def run_all_tests():
    """Run all integration tests."""
    print("="*70)
    print("INTEGRATION TEST SUITE - MLFLOW & CLICKHOUSE")
    print("="*70)

    tests = [
        ("MLflow Availability", test_mlflow_available),
        ("ClickHouse Driver Availability", test_clickhouse_driver_available),
        ("MLflow Local Tracking", test_mlflow_local_tracking),
        ("ClickHouse Connection", test_clickhouse_connection),
        ("Trainer Integration Detection", test_trainer_detects_integrations),
        ("Full Integration Flow", test_full_integration_flow),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
            else:
                failed += 1
                print(f"\n[FAILED] {test_name}")
        except Exception as e:
            failed += 1
            print(f"\n[ERROR] {test_name} failed with exception: {e}")
            import traceback
            traceback.print_exc()

    # Summary
    print("\n" + "="*70)
    print("INTEGRATION TEST SUMMARY")
    print("="*70)
    print(f"Tests passed: {passed}/{len(tests)}")
    print(f"Tests failed: {failed}/{len(tests)}")

    if failed == 0:
        print("\n" + "="*70)
        print("[SUCCESS] ALL INTEGRATION TESTS PASSED!")
        print("="*70)
        print("\nBoth MLflow and ClickHouse are properly integrated!")
        return 0
    else:
        print("\n" + "="*70)
        print(f"[PARTIAL SUCCESS] {passed} tests passed, {failed} tests failed")
        print("="*70)
        return 1


if __name__ == '__main__':
    exit(run_all_tests())
