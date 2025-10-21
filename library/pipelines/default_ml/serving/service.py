"""
FastAPI Model Serving Service for Default ML Strategy.

Serves XGBoost predictions via HTTP with sub-100ms latency.
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import xgboost as xgb
import numpy as np
from typing import List
import time
from pathlib import Path

app = FastAPI(title="Default ML Strategy Serving", version="1.0.0")

# Model storage
MODEL_PATH = Path(__file__).parent / "models" / "default_ml_model.json"
model = None


class PredictionRequest(BaseModel):
    """Request schema for predictions."""
    features: List[List[float]] = Field(
        ...,
        description="List of feature vectors, each with 9 features: "
                    "[rsi, macd, macd_signal, macd_histogram, bb_upper, bb_middle, "
                    "bb_lower, bb_bandwidth, bb_percent_b]"
    )


class PredictionResponse(BaseModel):
    """Response schema for predictions."""
    predictions: List[float] = Field(..., description="Probability of price increase (0-1)")
    model: str = "default_ml_strategy"
    version: str = "1.0.0"
    latency_ms: float


@app.on_event("startup")
async def load_model():
    """Load model on startup."""
    global model
    try:
        model = xgb.XGBClassifier()
        model.load_model(str(MODEL_PATH))
        print(f"[INFO] Model loaded from {MODEL_PATH}")
    except FileNotFoundError:
        print(f"[WARNING] Model file not found at {MODEL_PATH}")
        print("[INFO] Service will start but predictions will fail until model is provided")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "model_path": str(MODEL_PATH)
    }


@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """
    Generate predictions for given features.

    Returns probability that price will increase in next period.
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    start_time = time.time()

    try:
        # Convert to numpy array
        X = np.array(request.features)

        # Validate shape
        if X.shape[1] != 9:
            raise HTTPException(
                status_code=400,
                detail=f"Expected 9 features, got {X.shape[1]}"
            )

        # Generate predictions (probability of class 1 - price increase)
        predictions = model.predict_proba(X)[:, 1].tolist()

        latency_ms = (time.time() - start_time) * 1000

        return PredictionResponse(
            predictions=predictions,
            latency_ms=latency_ms
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "service": "Default ML Strategy Serving",
        "version": "1.0.0",
        "model_loaded": model is not None,
        "endpoints": {
            "health": "/health",
            "predict": "/predict (POST)",
            "docs": "/docs"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
