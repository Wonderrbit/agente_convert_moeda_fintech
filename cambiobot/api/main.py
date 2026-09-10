"""FastAPI application for CambioBot."""

from contextlib import asynccontextmanager
from decimal import Decimal
from typing import Any

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ..config import settings
from ..dataflows import get_fx_aggregator, calculate_dca_simulation
from ..agents import analyze_fx
from ..integrations import get_fx_tradingagents, TRADINGAGENTS_AVAILABLE


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    yield
    # Shutdown


app = FastAPI(
    title="CambioBot API",
    description="Agente Inteligente de Otimização Cambial para Viajantes via WhatsApp",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class SpotRateRequest(BaseModel):
    base: str = Field(default="BRL", description="Base currency (ISO 4217)")
    target: str = Field(..., description="Target currency (ISO 4217)")


class SpotRateResponse(BaseModel):
    base: str
    target: str
    rate: float
    timestamp: str
    source: str
    bid: float | None = None
    ask: float | None = None
    spread_pct: float | None = None


class MultiSpotRateRequest(BaseModel):
    base: str = Field(default="BRL")
    targets: list[str] = Field(..., min_length=1, max_length=20)


class MultiSpotRateResponse(BaseModel):
    rates: dict[str, SpotRateResponse | None]


class DCARequest(BaseModel):
    base: str = Field(default="BRL")
    target: str = Field(...)
    total_amount: float = Field(..., gt=0)
    installments: int = Field(..., ge=2, le=52)
    frequency_days: int = Field(default=7, ge=1, le=30)
    lookback_days: int = Field(default=365, ge=30, le=2555)


class DCAResponse(BaseModel):
    strategy: str
    installments: int
    frequency_days: int
    total_base_spent: float
    total_target_purchased: float
    average_rate: float
    final_rate: float
    current_value: float
    pnl: float
    pnl_pct: float
    comparison: dict
    period_analyzed: dict


class FXAnalysisRequest(BaseModel):
    base_currency: str = Field(default="BRL")
    target_currencies: list[str] = Field(default=["USD", "EUR"])
    travel_dates: dict[str, str] = Field(default_factory=dict)
    budget_per_currency: dict[str, float] = Field(default_factory=dict)
    user_profile: dict = Field(default_factory=dict)


class FXAnalysisResponse(BaseModel):
    recommendation: str
    confidence: float
    dca_plan: dict
    risk_assessment: dict
    metadata: dict


class TradingAgentsRequest(BaseModel):
    base: str = Field(default="BRL")
    targets: list[str] = Field(default=["USD", "EUR"])
    date: str | None = None


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    tradingagents_available: bool
    providers_configured: list[str]


# Health Check
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    providers = []
    if settings.alpha_vantage_api_key:
        providers.append("alphavantage")
    if settings.exchange_rate_api_key:
        providers.append("exchangerate-api")
    if settings.currencyapi_key:
        providers.append("currencyapi")
    providers.append("yfinance")  # Always available

    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        environment=settings.environment,
        tradingagents_available=TRADINGAGENTS_AVAILABLE,
        providers_configured=providers,
    )


# FX Rates Endpoints
@app.post("/v1/rates/spot", response_model=SpotRateResponse)
async def get_spot_rate(request: SpotRateRequest):
    """Get current spot rate for a currency pair."""
    try:
        aggregator = get_fx_aggregator()
        rate = await aggregator.get_spot_rate(request.base.upper(), request.target.upper())
        return SpotRateResponse(
            base=rate.base,
            target=rate.target,
            rate=float(rate.rate),
            timestamp=rate.timestamp.isoformat(),
            source=rate.source,
            bid=float(rate.bid) if rate.bid else None,
            ask=float(rate.ask) if rate.ask else None,
            spread_pct=rate.spread_pct,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/rates/multi", response_model=MultiSpotRateResponse)
async def get_multiple_spot_rates(request: MultiSpotRateRequest):
    """Get spot rates for multiple currency pairs."""
    try:
        aggregator = get_fx_aggregator()
        rates = await aggregator.get_multiple_spot_rates(
            request.base.upper(),
            [t.upper() for t in request.targets]
        )
        return MultiSpotRateResponse(
            rates={
                target: SpotRateResponse(
                    base=rate.base,
                    target=rate.target,
                    rate=float(rate.rate),
                    timestamp=rate.timestamp.isoformat(),
                    source=rate.source,
                    bid=float(rate.bid) if rate.bid else None,
                    ask=float(rate.ask) if rate.ask else None,
                    spread_pct=rate.spread_pct,
                ) if rate else None
                for target, rate in rates.items()
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# DCA Simulation Endpoint
@app.post("/v1/dca/simulate", response_model=DCAResponse)
async def simulate_dca(request: DCARequest):
    """Simulate DCA strategy on historical data."""
    try:
        result = await calculate_dca_simulation(
            base=request.base.upper(),
            target=request.target.upper(),
            total_amount=Decimal(str(request.total_amount)),
            installments=request.installments,
            frequency_days=request.frequency_days,
            lookback_days=request.lookback_days,
        )
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return DCAResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# FX Analysis Endpoint (Multi-agent)
@app.post("/v1/analysis/fx", response_model=FXAnalysisResponse)
async def analyze_fx_endpoint(request: FXAnalysisRequest):
    """Run full multi-agent FX analysis."""
    try:
        result = await analyze_fx(
            base_currency=request.base_currency.upper(),
            target_currencies=[c.upper() for c in request.target_currencies],
            travel_dates=request.travel_dates,
            budget_per_currency=request.budget_per_currency,
            user_profile=request.user_profile,
        )
        return FXAnalysisResponse(
            recommendation=result.get("recommendation", ""),
            confidence=result.get("confidence", 0.0),
            dca_plan=result.get("dca_plan", {}),
            risk_assessment=result.get("risk_assessment", {}),
            metadata=result.get("metadata", {}),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# TradingAgents Integration Endpoint
@app.post("/v1/analysis/tradingagents")
async def tradingagents_analysis(request: TradingAgentsRequest):
    """Run TradingAgents analysis on FX pairs (via proxy tickers)."""
    if not TRADINGAGENTS_AVAILABLE:
        raise HTTPException(
            status_code=501,
            detail="TradingAgents not installed. Install with: pip install -e '.[tradingagents]'"
        )

    try:
        wrapper = get_fx_tradingagents()
        results = await wrapper.analyze_multiple_pairs(
            request.base.upper(),
            [t.upper() for t in request.targets],
            request.date,
        )
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Webhook for Evolution API (WhatsApp)
@app.post("/v1/webhook/whatsapp")
async def whatsapp_webhook(payload: dict[str, Any]):
    """Receive WhatsApp messages via Evolution API webhook."""
    # TODO: Implement message processing
    return {"status": "received", "message_id": payload.get("message_id")}


# Affiliate Links Endpoint
@app.get("/v1/affiliates/links")
async def get_affiliate_links(country: str = Query(...), currency: str = Query(...)):
    """Get affiliate links for a destination."""
    links = []

    # Nomad - US only
    if country.upper() in ("US", "USA", "UNITED STATES") and currency.upper() == "USD":
        links.append({
            "partner": "Nomad",
            "type": "account",
            "url": settings.nomad_affiliate_url,
            "commission_usd": 30,
            "requirements": {"min_budget_usd": 100},
        })

    # Wise - Multiple countries
    wise_countries = {"US", "USA", "EUR", "GBR", "GBP", "JPN", "JPY", "CAN", "CAD", "AUS", "AUD"}
    if country.upper() in wise_countries:
        links.append({
            "partner": "Wise",
            "type": "account",
            "url": settings.wise_affiliate_url,
            "commission_bps": 50,
            "requirements": {"min_transfer_usd": 100},
        })

    # Avenue - US only
    if country.upper() in ("US", "USA") and currency.upper() == "USD":
        links.append({
            "partner": "Avenue",
            "type": "account",
            "url": settings.avenue_affiliate_url,
            "commission_usd": 40,
            "requirements": {"min_budget_usd": 500},
        })

    # Western Union - Argentina
    if country.upper() in ("ARG", "ARGENTINA"):
        links.append({
            "partner": "Western Union",
            "type": "remittance",
            "url": settings.western_union_affiliate_url,
            "commission_usd": 35,
            "requirements": {"destination": "ARG"},
        })

    return {"country": country, "currency": currency, "links": links}


# Configuration endpoint (for debugging)
@app.get("/v1/config")
async def get_config():
    """Get non-sensitive configuration."""
    return {
        "app_name": settings.app_name,
        "app_version": settings.app_version,
        "environment": settings.environment,
        "llm_provider": settings.llm_provider,
        "deep_think_llm": settings.deep_think_llm,
        "quick_think_llm": settings.quick_think_llm,
        "tradingagents_enabled": settings.tradingagents_enabled,
    }


def run():
    """Run the API server."""
    import uvicorn
    uvicorn.run(
        "cambiobot.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    run()