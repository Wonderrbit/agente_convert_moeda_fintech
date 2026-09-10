"""Integrations package for CambioBot."""

from .tradingagents import (
    FXTradingAgentsConfig,
    FXTradingAgentsWrapper,
    create_fx_tradingagents,
    get_fx_tradingagents,
    TRADINGAGENTS_AVAILABLE,
)

__all__ = [
    "FXTradingAgentsConfig",
    "FXTradingAgentsWrapper",
    "create_fx_tradingagents",
    "get_fx_tradingagents",
    "TRADINGAGENTS_AVAILABLE",
]