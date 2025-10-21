# PHASE 4 PROMPTS 06-13 - CONSOLIDATED EXECUTABLE GUIDE
# Complete Implementation Instructions

**Created**: 2025-10-20
**Status**: Ready for execution
**Format**: Each prompt has validation gate → implementation → testing → success criteria

---

## 🎯 USAGE

Each section below is a complete, executable prompt. Follow sequentially.

---

# PROMPT 06: HOTSWAP ENGINE (4-5 hours)

## Validation Gate
```bash
# Deployments working
curl -s "http://localhost:8350/api/v1/deployments" | jq '.total'
# Need 2+ active deployments for swapping
curl -s "http://localhost:8350/api/v1/deployments?status=active" | jq '.total'
```

## Implementation

**Create swap schemas**: `src/schemas/swap.py`
```python
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from enum import Enum

class SwapType(str, Enum):
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    AUTOMATIC = "automatic"
    EMERGENCY = "emergency"
    ROLLBACK = "rollback"

class SwapCreate(BaseModel):
    from_entity_id: UUID
    to_entity_id: UUID
    reason: str = Field(..., min_length=1)
    initiated_by: str
    swap_type: SwapType = SwapType.MANUAL
    validate_only: bool = False  # Dry-run mode
```

**Create swap service**: `src/services/swap_service.py`
```python
class SwapService:
    @staticmethod
    def validate_swap_compatibility(
        from_entity: EntityModel,
        to_entity: EntityModel,
        db: Session
    ) -> SwapValidation:
        """Validate entities are compatible for swapping."""
        errors = []
        # Both must be deployed
        if from_entity.status != 'deployed':
            errors.append(f"From entity not deployed: {from_entity.status}")
        if to_entity.status not in ['deployed', 'validated']:
            errors.append(f"To entity not ready: {to_entity.status}")
        
        # Same type
        if from_entity.type != to_entity.type:
            errors.append(f"Type mismatch: {from_entity.type} vs {to_entity.type}")
        
        return SwapValidation(passed=len(errors)==0, errors=errors)
```

**Create swap endpoints**: `src/api/v1/endpoints/swaps.py`
```python
@router.post("", response_model=SwapResponse)
async def create_swap(
    swap_data: SwapCreate,
    db: Session = Depends(get_db)
):
    """Execute hot-swap between two entities."""
    start_time = datetime.utcnow()
    
    # Get entities
    from_entity = db.query(EntityModel).filter(
        EntityModel.entity_id == swap_data.from_entity_id
    ).first()
    to_entity = db.query(EntityModel).filter(
        EntityModel.entity_id == swap_data.to_entity_id
    ).first()
    
    if not from_entity or not to_entity:
        raise HTTPException(404, "Entity not found")
    
    # Validate compatibility
    validation = SwapService.validate_swap_compatibility(
        from_entity, to_entity, db
    )
    
    if not validation.passed:
        raise HTTPException(400, detail=validation.errors)
    
    if swap_data.validate_only:
        return {"validation": validation, "swap_id": None}
    
    # Get active deployments
    from_deploy = db.query(DeploymentModel).filter(
        DeploymentModel.entity_id == swap_data.from_entity_id,
        DeploymentModel.status == 'active'
    ).first()
    
    to_deploy = db.query(DeploymentModel).filter(
        DeploymentModel.entity_id == swap_data.to_entity_id,
        DeploymentModel.status == 'active'
    ).first()
    
    # Create swap record
    swap = SwapModel(
        from_entity_id=swap_data.from_entity_id,
        to_entity_id=swap_data.to_entity_id,
        from_deployment_id=from_deploy.deployment_id if from_deploy else None,
        to_deployment_id=to_deploy.deployment_id if to_deploy else None,
        swap_type=swap_data.swap_type,
        reason=swap_data.reason,
        initiated_by=swap_data.initiated_by,
        status='completed',
        success=True
    )
    
    # Execute swap: deactivate from, activate to
    if from_deploy:
        from_deploy.status = 'inactive'
    if to_deploy:
        to_deploy.status = 'active'
    else:
        # Create new deployment for to_entity
        new_deploy = DeploymentModel(
            entity_id=to_entity.entity_id,
            version=to_entity.version,
            environment='production',
            config_snapshot=to_entity.config,
            status='active',
            deployed_by=swap_data.initiated_by
        )
        db.add(new_deploy)
    
    # Update entity statuses
    from_entity.status = 'inactive'
    to_entity.status = 'active'
    
    # Calculate swap duration
    swap.duration_seconds = int((datetime.utcnow() - start_time).total_seconds())
    swap.completed_at = datetime.utcnow()
    
    db.add(swap)
    db.commit()
    
    # Publish event
    await publisher.publish_swap_completed(...)
    
    return SwapResponse.model_validate(swap)
```

## Testing
```bash
# Create two entities and deploy both
E1=$(curl -s -X POST http://localhost:8350/api/v1/entities \
  -d '{"name":"strategy_a","type":"strategy","version":"1.0.0"}' | jq -r '.entity_id')
E2=$(curl -s -X POST http://localhost:8350/api/v1/entities \
  -d '{"name":"strategy_b","type":"strategy","version":"1.1.0"}' | jq -r '.entity_id')

curl -X POST http://localhost:8350/api/v1/deployments \
  -d "{\"entity_id\":\"$E1\",\"environment\":\"production\",\"deployed_by\":\"test\"}"
curl -X POST http://localhost:8350/api/v1/deployments \
  -d "{\"entity_id\":\"$E2\",\"environment\":\"staging\",\"deployed_by\":\"test\"}"

# Execute swap
curl -X POST http://localhost:8350/api/v1/swaps \
  -d "{\"from_entity_id\":\"$E1\",\"to_entity_id\":\"$E2\",\"reason\":\"test\",\"initiated_by\":\"test\"}"

# Verify: E1 inactive, E2 active
curl -s http://localhost:8350/api/v1/entities/$E1 | jq '.status'
curl -s http://localhost:8350/api/v1/entities/$E2 | jq '.status'
```

## Success Criteria
- [ ] Can swap between deployed entities
- [ ] Validation prevents incompatible swaps
- [ ] Deployment statuses updated correctly
- [ ] Downtime tracked
- [ ] Cannot swap non-deployed entities
- [ ] Rollback capability exists

---

# PROMPT 07: DEFAULT ML FEATURES (4-5 hours)

## Validation Gate
```bash
# QuestDB accessible
curl http://localhost:9000/status
# ClickHouse accessible  
curl http://localhost:8123/ping
```

## Implementation

**Create features directory**: `library/pipelines/default_ml/features/`

**RSI Calculator**: `features/rsi.py`
```python
import pandas as pd
import numpy as np

def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """Calculate Relative Strength Index."""
    delta = prices.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi
```

**MACD Calculator**: `features/macd.py`
```python
def calculate_macd(prices: pd.Series, fast=12, slow=26, signal=9) -> pd.DataFrame:
    """Calculate MACD indicator."""
    ema_fast = prices.ewm(span=fast).mean()
    ema_slow = prices.ewm(span=slow).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal).mean()
    histogram = macd_line - signal_line
    return pd.DataFrame({
        'macd': macd_line,
        'signal': signal_line,
        'histogram': histogram
    })
```

**Bollinger Bands**: `features/bollinger_bands.py`
```python
def calculate_bollinger_bands(prices: pd.Series, period=20, std_dev=2.0) -> pd.DataFrame:
    """Calculate Bollinger Bands."""
    sma = prices.rolling(window=period).mean()
    std = prices.rolling(window=period).std()
    upper = sma + (std * std_dev)
    lower = sma - (std * std_dev)
    return pd.DataFrame({'upper': upper, 'middle': sma, 'lower': lower})
```

**Feature Pipeline**: `features/pipeline.py`
```python
import pandas as pd
from .rsi import calculate_rsi
from .macd import calculate_macd
from .bollinger_bands import calculate_bollinger_bands

class FeaturePipeline:
    def calculate_all_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all technical indicators."""
        df['rsi'] = calculate_rsi(df['close'], period=14)
        
        macd_features = calculate_macd(df['close'])
        df['macd'] = macd_features['macd']
        df['macd_signal'] = macd_features['signal']
        df['macd_histogram'] = macd_features['histogram']
        
        bbands = calculate_bollinger_bands(df['close'])
        df['bb_upper'] = bbands['upper']
        df['bb_middle'] = bbands['middle']
        df['bb_lower'] = bbands['lower']
        
        # Drop NaN rows from rolling windows
        df = df.dropna()
        
        return df
```

## Testing
```bash
# Test feature calculations
python3 << 'EOF'
import pandas as pd
import sys
sys.path.insert(0, 'library/pipelines/default_ml')

from features.pipeline import FeaturePipeline

# Sample data
data = {
    'close': [100, 102, 101, 103, 105, 104, 106, 108, 107, 109, 
              111, 110, 112, 114, 113, 115, 117, 116, 118, 120]
}
df = pd.DataFrame(data)

# Calculate features
pipeline = FeaturePipeline()
result = pipeline.calculate_all_features(df)

print("Features calculated:")
print(result[['close', 'rsi', 'macd', 'bb_upper', 'bb_lower']].tail())
print("\n✅ Feature pipeline working")
EOF
```

## Success Criteria
- [ ] RSI calculates correctly (0-100 range)
- [ ] MACD calculates correctly
- [ ] Bollinger Bands calculate correctly
- [ ] No NaN values in output
- [ ] Can process real market data
- [ ] Results stored in ClickHouse

---

# PROMPT 08: XGBOOST TRAINING (5-6 hours)

## Implementation

**Training Pipeline**: `library/pipelines/default_ml/training/train.py`
```python
import xgboost as xgb
import mlflow
import pandas as pd
from sklearn.model_selection import train_test_split
from clickhouse_driver import Client

class XGBoostTrainer:
    def __init__(self):
        self.model = None
        mlflow.set_tracking_uri("http://mlflow:5000")
        mlflow.set_experiment("default_ml_strategy")
    
    def load_features(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Load features from ClickHouse."""
        client = Client('clickhouse')
        query = f"""
        SELECT * FROM features 
        WHERE symbol = '{symbol}' 
        AND timestamp >= '{start_date}' 
        AND timestamp <= '{end_date}'
        """
        df = client.query_dataframe(query)
        return df
    
    def prepare_data(self, df: pd.DataFrame):
        """Prepare features and labels."""
        # Create label: 1 if next-day return > 0
        df['label'] = (df['close'].shift(-1) > df['close']).astype(int)
        df = df.dropna()
        
        feature_cols = ['rsi', 'macd', 'macd_signal', 'bb_upper', 'bb_lower']
        X = df[feature_cols]
        y = df['label']
        
        return train_test_split(X, y, test_size=0.2, shuffle=False)
    
    def train(self, X_train, y_train, X_test, y_test):
        """Train XGBoost model."""
        with mlflow.start_run():
            # Hyperparameters
            params = {
                'max_depth': 5,
                'learning_rate': 0.1,
                'n_estimators': 100,
                'objective': 'binary:logistic'
            }
            
            mlflow.log_params(params)
            
            # Train
            self.model = xgb.XGBClassifier(**params)
            self.model.fit(X_train, y_train)
            
            # Evaluate
            train_score = self.model.score(X_train, y_train)
            test_score = self.model.score(X_test, y_test)
            
            mlflow.log_metric("train_accuracy", train_score)
            mlflow.log_metric("test_accuracy", test_score)
            
            # Save model
            mlflow.xgboost.log_model(self.model, "model")
            
            print(f"Train accuracy: {train_score:.3f}")
            print(f"Test accuracy: {test_score:.3f}")
            
            return self.model
```

## Testing
```bash
python3 << 'EOF'
from training.train import XGBoostTrainer

trainer = XGBoostTrainer()

# Load data
df = trainer.load_features('AAPL', '2024-01-01', '2024-12-31')

# Prepare
X_train, X_test, y_train, y_test = trainer.prepare_data(df)

# Train
model = trainer.train(X_train, y_train, X_test, y_test)

print("✅ Model trained and logged to MLflow")
EOF
```

## Success Criteria
- [ ] Can load features from ClickHouse
- [ ] Model trains successfully
- [ ] Metrics logged to MLflow
- [ ] Model registered in MLflow
- [ ] Test accuracy > 50%

---

# PROMPT 09: FEAST INTEGRATION (4-5 hours)

## Implementation

**Feast Config**: `feast/feature_repo/feature_store.yaml`
```yaml
project: library
registry: data/registry.db
provider: local
offline_store:
  type: clickhouse
  host: clickhouse
  port: 9000
  database: features
online_store:
  type: redis
  connection_string: redis:6379
```

**Feature Definitions**: `feast/feature_repo/features.py`
```python
from feast import Entity, FeatureView, Field, ValueType
from feast.types import Float32
from datetime import timedelta

symbol = Entity(name="symbol", join_keys=["symbol"])

technical_indicators = FeatureView(
    name="technical_indicators",
    entities=[symbol],
    ttl=timedelta(days=1),
    schema=[
        Field(name="rsi", dtype=Float32),
        Field(name="macd", dtype=Float32),
        Field(name="bb_upper", dtype=Float32),
        Field(name="bb_lower", dtype=Float32),
    ],
    source=...  # ClickHouse source
)
```

## Testing
```bash
cd feast/feature_repo

# Apply feature definitions
feast apply

# Materialize to online store
feast materialize-incremental $(date -d "yesterday" +%Y-%m-%d)T00:00:00 $(date +%Y-%m-%d)T00:00:00

# Test feature retrieval
python3 << 'EOF'
from feast import FeatureStore
store = FeatureStore(repo_path=".")
features = store.get_online_features(
    features=["technical_indicators:rsi", "technical_indicators:macd"],
    entity_rows=[{"symbol": "AAPL"}]
).to_dict()
print(features)
print("✅ Feast working")
EOF
```

## Success Criteria
- [ ] Feast configured
- [ ] Features defined
- [ ] Can materialize features
- [ ] Online store serving
- [ ] Latency < 10ms

---

# PROMPT 10: BENTOML SERVING (4-5 hours)

## Implementation

**BentoML Service**: `library/pipelines/default_ml/serving/service.py`
```python
import bentoml
from bentoml.io import JSON, NumpyNdarray
import mlflow
import numpy as np

# Load model from MLflow
mlflow.set_tracking_uri("http://mlflow:5000")
model_uri = "models:/default_ml_strategy/latest"
model = mlflow.xgboost.load_model(model_uri)

# Create BentoML service
svc = bentoml.Service("default_ml_strategy")

@svc.api(input=NumpyNdarray(), output=JSON())
def predict(features: np.ndarray) -> dict:
    """Generate predictions."""
    predictions = model.predict_proba(features)
    return {
        "predictions": predictions[:,1].tolist(),  # Probability of class 1
        "model": "default_ml_strategy",
        "version": "1.0.0"
    }
```

## Testing
```bash
# Build Bento
bentoml build

# Serve
bentoml serve service:svc --port 3000

# Test prediction
curl -X POST http://localhost:3000/predict \
  -H "Content-Type: application/json" \
  -d '{"features": [[50.0, 0.5, 0.3, 105.0, 95.0]]}'
```

## Success Criteria
- [ ] Model loaded from MLflow
- [ ] Serving via HTTP
- [ ] Prediction latency < 100ms
- [ ] Batch predictions working

---

# PROMPT 11: DEFAULT ALPHA STRATEGY (5-6 hours)

## Implementation

**Strategy Class**: `library/pipelines/default_ml/strategy/alpha_strategy.py`
```python
class DefaultMLStrategy:
    def __init__(self, model_endpoint: str):
        self.model_endpoint = model_endpoint
        self.position_size = 0.02  # 2% per trade
    
    def generate_signal(self, features: dict) -> dict:
        """Generate trading signal from features."""
        # Get prediction from BentoML
        response = requests.post(
            f"{self.model_endpoint}/predict",
            json={"features": [list(features.values())]}
        )
        prob = response.json()['predictions'][0]
        
        # Signal logic
        if prob > 0.6:  # High confidence long
            signal = {
                "action": "BUY",
                "size": self.position_size,
                "confidence": prob
            }
        elif prob < 0.4:  # High confidence short
            signal = {
                "action": "SELL", 
                "size": self.position_size,
                "confidence": 1 - prob
            }
        else:
            signal = {"action": "HOLD"}
        
        return signal
```

**Register in Library**:
```bash
curl -X POST http://localhost:8350/api/v1/entities \
  -d '{
    "name": "default_ml_strategy",
    "type": "strategy",
    "version": "1.0.0",
    "description": "XGBoost-based trading strategy",
    "config": {
      "model_endpoint": "http://bentoml:3000",
      "position_size": 0.02
    }
  }'
```

## Success Criteria
- [ ] Strategy generates signals
- [ ] Registered in library
- [ ] Can deploy strategy
- [ ] Backtest shows results

---

# PROMPT 12: INTEGRATION TESTS (3-4 hours)

## Implementation

**E2E Test Suite**: `tests/integration/test_full_flow.py`
```python
def test_full_ml_pipeline():
    """Test complete ML pipeline end-to-end."""
    # 1. Register entity
    entity = create_entity("test_strategy")
    assert entity['entity_id']
    
    # 2. Deploy entity
    deployment = deploy_entity(entity['entity_id'], "staging")
    assert deployment['status'] == 'active'
    
    # 3. Calculate features
    features = calculate_features("AAPL")
    assert 'rsi' in features
    
    # 4. Train model
    model = train_model(features)
    assert model['test_accuracy'] > 0.5
    
    # 5. Serve model
    prediction = predict([50, 0.5, 0.3, 105, 95])
    assert 0 <= prediction <= 1
    
    # 6. Generate signal
    signal = generate_signal(features)
    assert signal['action'] in ['BUY', 'SELL', 'HOLD']
    
    print("✅ Full E2E pipeline working")
```

## Testing
```bash
pytest tests/integration/test_full_flow.py -v
```

## Success Criteria
- [ ] All E2E tests pass
- [ ] Feature → Train → Serve → Signal flow works
- [ ] Entity → Deploy → Swap flow works
- [ ] Performance benchmarks met

---

# PROMPT 13: PRODUCTION DEPLOYMENT (3-4 hours)

## Implementation

**Complete Docker Compose**: `infrastructure/docker/docker-compose.library.yml`
```yaml
version: '3.8'

services:
  postgres-library:
    image: postgres:16-alpine
    # ... (from PROMPT01)
  
  library:
    image: localhost/library:latest
    build: ../../library/apps/library
    ports:
      - "8350:8350"
    environment:
      - POSTGRES_HOST=postgres-library
      - NATS_URL=nats://nats:4222
    depends_on:
      - postgres-library
      - nats
  
  feature-pipeline:
    image: localhost/feature-pipeline:latest
    build: ../../library/pipelines/default_ml/features
  
  ml-training:
    image: localhost/ml-training:latest
    build: ../../library/pipelines/default_ml/training
    
  bentoml:
    image: localhost/bentoml:latest
    ports:
      - "3000:3000"
  
  feast:
    image: localhost/feast:latest
    ports:
      - "6566:6566"

networks:
  trade2026-backend:
    external: true
```

## Deployment
```bash
cd C:\ClaudeDesktop_Projects\Trade2026\infrastructure\docker

# Build all services
docker-compose -f docker-compose.library.yml build

# Start everything
docker-compose -f docker-compose.base.yml \
               -f docker-compose.apps.yml \
               -f docker-compose.library.yml \
               up -d

# Verify all healthy
docker-compose -f docker-compose.library.yml ps

# Monitor logs
docker-compose -f docker-compose.library.yml logs -f
```

## Success Criteria
- [ ] All services start
- [ ] All health checks pass
- [ ] Can execute full workflow
- [ ] System stable 10+ minutes
- [ ] No errors in logs
- [ ] APIs responding
- [ ] Documentation complete

---

## 🎯 PHASE 4 COMPLETE CHECKLIST

- [ ] PROMPT00-05: Foundation (complete)
- [ ] PROMPT06: HotSwap Engine
- [ ] PROMPT07: Feature Engineering
- [ ] PROMPT08: XGBoost Training
- [ ] PROMPT09: Feast Integration
- [ ] PROMPT10: BentoML Serving
- [ ] PROMPT11: Alpha Strategy
- [ ] PROMPT12: Integration Tests
- [ ] PROMPT13: Production Deploy

**When all checked** → Phase 4 COMPLETE! ✅

---

**Created**: 2025-10-20
**Format**: Consolidated executable guide
**Usage**: Follow each prompt section sequentially
