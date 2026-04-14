from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException

from backend.app.auth import create_access_token, require_token, verify_credentials
from backend.app.schemas import CustomerFeatures, LoginRequest
from backend.app.services import (
    get_feature_importance,
    get_metrics,
    get_revenue_impact,
    get_segment_snapshot,
    predict_customer,
    predictor,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    predictor()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Churn Intelligence Platform API",
        version="2.0.0",
        lifespan=lifespan,
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/auth/login")
    def login(payload: LoginRequest) -> dict[str, str]:
        if not verify_credentials(payload.username, payload.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        token = create_access_token(payload.username)
        return {"access_token": token, "token_type": "bearer"}

    @app.post("/predict")
    def predict(
        customer: CustomerFeatures,
        _: str = Depends(require_token),
    ) -> dict[str, object]:
        return predict_customer(customer.model_dump())

    @app.get("/metrics")
    def metrics(_: str = Depends(require_token)) -> dict[str, object]:
        return get_metrics()

    @app.get("/feature-importance")
    def feature_importance(
        limit: int = 20,
        _: str = Depends(require_token),
    ) -> list[dict[str, object]]:
        return get_feature_importance(limit=limit)

    @app.get("/segments")
    def segments(_: str = Depends(require_token)) -> dict[str, object]:
        return get_segment_snapshot()

    @app.get("/insights")
    def insights(_: str = Depends(require_token)) -> dict[str, object]:
        segment = get_segment_snapshot()
        return {
            "top_reasons": [
                "Low engagement and high support load correlate strongly with churn",
                "Month-to-month contracts are overrepresented in high-risk users",
                "Electronic check payment users show elevated volatility",
            ],
            "kpis": segment["kpis"],
        }

    @app.get("/revenue-impact")
    def revenue_impact(_: str = Depends(require_token)) -> dict[str, object]:
        return get_revenue_impact()

    return app


app = create_app()
