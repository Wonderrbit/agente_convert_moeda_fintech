"""Dataflows package for CambioBot."""

from .fx_data import (
    FXRate,
    FXTimeSeries,
    FXDataProvider,
    YFinanceProvider,
    ExchangeRateAPIProvider,
    CurrencyAPIProvider,
    AlphaVantageProvider,
    FREDProvider,
    FXDataAggregator,
    get_fx_aggregator,
    get_spot_rate,
    get_multiple_spot_rates,
    get_historical_rates,
    calculate_dca_simulation,
)

__all__ = [
    "FXRate",
    "FXTimeSeries",
    "FXDataProvider",
    "YFinanceProvider",
    "ExchangeRateAPIProvider",
    "CurrencyAPIProvider",
    "AlphaVantageProvider",
    "FREDProvider",
    "FXDataAggregator",
    "get_fx_aggregator",
    "get_spot_rate",
    "get_multiple_spot_rates",
    "get_historical_rates",
    "calculate_dca_simulation",
]