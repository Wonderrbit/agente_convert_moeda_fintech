"""TradingAgents Integration for CambioBot.

This module provides integration with the TradingAgents framework
for advanced multi-agent financial analysis adapted for FX markets.
"""

import os
from typing import Any, Optional
from dataclasses import dataclass, field

try:
    from tradingagents.graph.trading_graph import TradingAgentsGraph
    from tradingagents.default_config import DEFAULT_CONFIG
    TRADINGAGENTS_AVAILABLE = True
except ImportError:
    TRADINGAGENTS_AVAILABLE = False
    TradingAgentsGraph = None
    DEFAULT_CONFIG = {}

from ..config import settings


@dataclass
class FXTradingAgentsConfig:
    """Configuration for FX TradingAgents integration."""
    # Base config from TradingAgents
    llm_provider: str = "openrouter"
    deep_think_llm: str = "anthropic/claude-3.5-sonnet"
    quick_think_llm: str = "openai/gpt-4o-mini"
    backend_url: str = "https://openrouter.ai/api/v1"
    temperature: float = 0.1
    max_tokens: int = 8192
    max_debate_rounds: int = 1
    max_risk_discuss_rounds: int = 1
    checkpoint_enabled: bool = False

    # FX-specific
    base_currency: str = "BRL"
    target_currencies: list[str] = field(default_factory=lambda: ["USD", "EUR"])
    analysis_horizon_days: int = 90

    def to_dict(self) -> dict[str, Any]:
        """Convert to TradingAgents config dict."""
        return {
            "llm_provider": self.llm_provider,
            "deep_think_llm": self.deep_think_llm,
            "quick_think_llm": self.quick_think_llm,
            "backend_url": self.backend_url,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "max_debate_rounds": self.max_debate_rounds,
            "max_risk_discuss_rounds": self.max_risk_discuss_rounds,
            "checkpoint_enabled": self.checkpoint_enabled,
            "data_vendors": {
                "core_stock_apis": "yfinance",
                "technical_indicators": "yfinance",
                "fundamental_data": "yfinance",
                "news_data": "yfinance",
                "macro_data": "fred",
                "prediction_markets": "polymarket",
            },
        }


class FXTradingAgentsWrapper:
    """Wrapper around TradingAgents for FX analysis."""

    def __init__(self, config: FXTradingAgentsConfig | None = None):
        if not TRADINGAGENTS_AVAILABLE:
            raise ImportError(
                "TradingAgents not installed. "
                "Install with: pip install -e '.[tradingagents]'"
            )

        self.config = config or FXTradingAgentsConfig()
        self._ta_graph: Optional[TradingAgentsGraph] = None

    def _get_graph(self) -> TradingAgentsGraph:
        """Get or create TradingAgentsGraph instance."""
        if self._ta_graph is None:
            ta_config = DEFAULT_CONFIG.copy()
            ta_config.update(self.config.to_dict())

            # Set API keys from settings
            os.environ["OPENROUTER_API_KEY"] = settings.openrouter_api_key or ""
            if settings.anthropic_api_key:
                os.environ["ANTHROPIC_API_KEY"] = settings.anthropic_api_key
            if settings.google_api_key:
                os.environ["GOOGLE_API_KEY"] = settings.google_api_key
            if settings.openai_api_key:
                os.environ["OPENAI_API_KEY"] = settings.openai_api_key

            self._ta_graph = TradingAgentsGraph(debug=settings.tradingagents_debug, config=ta_config)
        return self._ta_graph

    async def analyze_currency_pair(
        self,
        base: str,
        target: str,
        date: str | None = None,
    ) -> dict[str, Any]:
        """Analyze a currency pair using TradingAgents.

        Note: TradingAgents is designed for equity analysis.
        For FX, we map currency pairs to proxy tickers:
        - USD/BRL -> EWZ (Brazil ETF) vs SPY (US ETF) or USDBRL=X
        - EUR/BRL -> EWZ vs EZU (Eurozone ETF) or EURBRL=X
        """
        graph = self._get_graph()

        # Map FX pairs to tradeable proxies
        proxy_map = {
            ("BRL", "USD"): "USDBRL=X",
            ("BRL", "EUR"): "EURBRL=X",
            ("BRL", "GBP"): "GBPBRL=X",
            ("BRL", "JPY"): "JPYBRL=X",
            ("BRL", "ARS"): "ARSBRL=X",
            ("USD", "BRL"): "USDBRL=X",
            ("EUR", "BRL"): "EURBRL=X",
        }

        ticker = proxy_map.get((base, target), f"{target}{base}=X")

        # Run analysis
        _, decision = graph.propagate(ticker, date or "2025-01-15")

        return {
            "pair": f"{base}/{target}",
            "proxy_ticker": ticker,
            "decision": decision,
            "config_used": self.config.to_dict(),
        }

    async def analyze_multiple_pairs(
        self,
        base: str,
        targets: list[str],
        date: str | None = None,
    ) -> dict[str, Any]:
        """Analyze multiple currency pairs."""
        results = {}
        for target in targets:
            try:
                results[target] = await self.analyze_currency_pair(base, target, date)
            except Exception as e:
                results[target] = {"error": str(e), "pair": f"{base}/{target}"}
        return results


def create_fx_tradingagents(config: FXTradingAgentsConfig | None = None) -> FXTradingAgentsWrapper:
    """Factory function to create FX TradingAgents wrapper."""
    return FXTradingAgentsWrapper(config)


# Fallback for when TradingAgents is not available
class MockFXTradingAgentsWrapper:
    """Mock wrapper when TradingAgents is not installed."""

    def __init__(self, config: FXTradingAgentsConfig | None = None):
        self.config = config or FXTradingAgentsConfig()

    async def analyze_currency_pair(self, base: str, target: str, date: str | None = None) -> dict:
        return {
            "pair": f"{base}/{target}",
            "error": "TradingAgents not installed. Install with: pip install -e '.[tradingagents]'",
            "mock": True,
        }

    async def analyze_multiple_pairs(self, base: str, targets: list[str], date: str | None = None) -> dict:
        return {t: await self.analyze_currency_pair(base, t, date) for t in targets}


def get_fx_tradingagents(config: FXTradingAgentsConfig | None = None):
    """Get FX TradingAgents wrapper (real or mock)."""
    if TRADINGAGENTS_AVAILABLE:
        return FXTradingAgentsWrapper(config)
    return MockFXTradingAgentsWrapper(config)