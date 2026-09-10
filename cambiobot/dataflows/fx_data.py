"""FX Data Flows for CambioBot - Multi-source FX data retrieval."""

import asyncio
from datetime import datetime, timedelta
from typing import Any, Optional
from dataclasses import dataclass
from decimal import Decimal

import httpx
import yfinance as yf
import pandas as pd

from ..config import settings


@dataclass
class FXRate:
    """FX Rate data point."""
    base: str
    target: str
    rate: Decimal
    timestamp: datetime
    source: str
    bid: Optional[Decimal] = None
    ask: Optional[Decimal] = None
    spread_pct: Optional[float] = None


@dataclass
class FXTimeSeries:
    """FX Time series data."""
    base: str
    target: str
    rates: list[FXRate]
    source: str
    interval: str  # 1m, 5m, 1h, 1d, 1w


class FXDataProvider:
    """Base class for FX data providers."""

    async def get_spot_rate(self, base: str, target: str) -> FXRate:
        raise NotImplementedError

    async def get_time_series(
        self,
        base: str,
        target: str,
        start: datetime,
        end: datetime,
        interval: str = "1d",
    ) -> FXTimeSeries:
        raise NotImplementedError

    async def get_historical_rates(
        self,
        base: str,
        target: str,
        days: int = 365,
    ) -> list[FXRate]:
        raise NotImplementedError


class YFinanceProvider(FXDataProvider):
    """Yahoo Finance FX data provider."""

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)

    def _format_pair(self, base: str, target: str) -> str:
        """Format pair for yfinance (e.g., USDBRL=X)."""
        return f"{target}{base}=X"

    async def get_spot_rate(self, base: str, target: str) -> FXRate:
        """Get current spot rate from Yahoo Finance."""
        pair = self._format_pair(base, target)
        ticker = yf.Ticker(pair)

        # Get latest data
        hist = ticker.history(period="1d", interval="1m")
        if hist.empty:
            hist = ticker.history(period="5d", interval="1d")

        if hist.empty:
            raise ValueError(f"No data for {pair}")

        latest = hist.iloc[-1]
        rate = Decimal(str(latest["Close"]))

        return FXRate(
            base=base,
            target=target,
            rate=rate,
            timestamp=datetime.now(),
            source="yfinance",
            bid=Decimal(str(latest.get("Low", rate))),
            ask=Decimal(str(latest.get("High", rate))),
        )

    async def get_time_series(
        self,
        base: str,
        target: str,
        start: datetime,
        end: datetime,
        interval: str = "1d",
    ) -> FXTimeSeries:
        """Get time series from Yahoo Finance."""
        pair = self._format_pair(base, target)
        ticker = yf.Ticker(pair)

        # Map interval
        yf_interval_map = {
            "1m": "1m",
            "5m": "5m",
            "15m": "15m",
            "1h": "1h",
            "1d": "1d",
            "1w": "1wk",
            "1M": "1mo",
        }
        yf_interval = yf_interval_map.get(interval, "1d")

        # Calculate period
        days = (end - start).days
        if days <= 7:
            period = "7d"
        elif days <= 30:
            period = "1mo"
        elif days <= 90:
            period = "3mo"
        elif days <= 365:
            period = "1y"
        else:
            period = "max"

        hist = ticker.history(period=period, interval=yf_interval)

        if hist.empty:
            return FXTimeSeries(base=base, target=target, rates=[], source="yfinance", interval=interval)

        rates = []
        for idx, row in hist.iterrows():
            rates.append(FXRate(
                base=base,
                target=target,
                rate=Decimal(str(row["Close"])),
                timestamp=idx.to_pydatetime() if hasattr(idx, 'to_pydatetime') else idx,
                source="yfinance",
                bid=Decimal(str(row.get("Low", row["Close"]))),
                ask=Decimal(str(row.get("High", row["Close"]))),
            ))

        return FXTimeSeries(
            base=base,
            target=target,
            rates=rates,
            source="yfinance",
            interval=interval,
        )

    async def get_historical_rates(self, base: str, target: str, days: int = 365) -> list[FXRate]:
        """Get historical daily rates."""
        end = datetime.now()
        start = end - timedelta(days=days)
        ts = await self.get_time_series(base, target, start, end, "1d")
        return ts.rates


class ExchangeRateAPIProvider(FXDataProvider):
    """ExchangeRate-API.com provider (free tier: 1500 req/month)."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or settings.exchange_rate_api_key
        self.base_url = "https://v6.exchangerate-api.com/v6"
        self.client = httpx.AsyncClient(timeout=30.0)

    async def get_spot_rate(self, base: str, target: str) -> FXRate:
        if not self.api_key:
            raise ValueError("ExchangeRate-API key not configured")

        url = f"{self.base_url}/{self.api_key}/pair/{base}/{target}"
        response = await self.client.get(url)
        response.raise_for_status()
        data = response.json()

        if data.get("result") != "success":
            raise ValueError(f"API error: {data.get('error-type', 'Unknown')}")

        rate = Decimal(str(data["conversion_rate"]))
        return FXRate(
            base=base,
            target=target,
            rate=rate,
            timestamp=datetime.fromtimestamp(data["time_last_update_unix"]),
            source="exchangerate-api",
        )

    async def get_time_series(self, base: str, target: str, start: datetime, end: datetime, interval: str = "1d") -> FXTimeSeries:
        # ExchangeRate-API doesn't provide historical time series in free tier
        # Would need paid plan
        return FXTimeSeries(base=base, target=target, rates=[], source="exchangerate-api", interval=interval)


class CurrencyAPIProvider(FXDataProvider):
    """CurrencyAPI.com provider."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or settings.currencyapi_key
        self.base_url = "https://api.currencyapi.com/v3"
        self.client = httpx.AsyncClient(timeout=30.0)

    async def get_spot_rate(self, base: str, target: str) -> FXRate:
        if not self.api_key:
            raise ValueError("CurrencyAPI key not configured")

        url = f"{self.base_url}/latest"
        params = {"apikey": self.api_key, "base_currency": base, "currencies": target}
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        rate = Decimal(str(data["data"][target]["value"]))
        return FXRate(
            base=base,
            target=target,
            rate=rate,
            timestamp=datetime.fromisoformat(data["meta"]["last_updated_at"].replace("Z", "+00:00")),
            source="currencyapi",
        )


class AlphaVantageProvider(FXDataProvider):
    """Alpha Vantage FX provider."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or settings.alpha_vantage_api_key
        self.base_url = "https://www.alphavantage.co/query"
        self.client = httpx.AsyncClient(timeout=30.0)

    async def get_spot_rate(self, base: str, target: str) -> FXRate:
        if not self.api_key:
            raise ValueError("Alpha Vantage API key not configured")

        params = {
            "function": "CURRENCY_EXCHANGE_RATE",
            "from_currency": base,
            "to_currency": target,
            "apikey": self.api_key,
        }
        response = await self.client.get(self.base_url, params=params)
        response.raise_for_status()
        data = response.json()

        rate_info = data.get("Realtime Currency Exchange Rate", {})
        rate = Decimal(str(rate_info.get("5. Exchange Rate", 0)))
        bid = Decimal(str(rate_info.get("8. Bid Price", rate)))
        ask = Decimal(str(rate_info.get("9. Ask Price", rate)))

        return FXRate(
            base=base,
            target=target,
            rate=rate,
            timestamp=datetime.now(),
            source="alphavantage",
            bid=bid,
            ask=ask,
            spread_pct=float((ask - bid) / rate * 100) if rate else None,
        )

    async def get_time_series(
        self,
        base: str,
        target: str,
        start: datetime,
        end: datetime,
        interval: str = "1d",
    ) -> FXTimeSeries:
        if not self.api_key:
            raise ValueError("Alpha Vantage API key not configured")

        # Alpha Vantage FX_DAILY for daily, FX_INTRADAY for intraday
        function = "FX_DAILY" if interval in ("1d", "1w", "1M") else "FX_INTRADAY"
        params = {
            "function": function,
            "from_symbol": base,
            "to_symbol": target,
            "apikey": self.api_key,
            "outputsize": "full",
        }
        if function == "FX_INTRADAY":
            params["interval"] = "60min"  # 1h, 30min, 15min, 5min, 1min

        response = await self.client.get(self.base_url, params=params)
        response.raise_for_status()
        data = response.json()

        # Parse time series
        ts_key = [k for k in data.keys() if "Time Series" in k][0]
        ts_data = data[ts_key]

        rates = []
        for ts_str, values in ts_data.items():
            ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S" if " " in ts_str else "%Y-%m-%d")
            if start <= ts <= end:
                rate = Decimal(str(values["4. close"]))
                rates.append(FXRate(
                    base=base,
                    target=target,
                    rate=rate,
                    timestamp=ts,
                    source="alphavantage",
                    bid=Decimal(str(values.get("3. low", rate))),
                    ask=Decimal(str(values.get("2. high", rate))),
                ))

        return FXTimeSeries(
            base=base,
            target=target,
            rates=rates,
            source="alphavantage",
            interval=interval,
        )


class FREDProvider(FXDataProvider):
    """FRED (Federal Reserve) macro data provider."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or settings.fred_api_key
        self.base_url = "https://api.stlouisfed.org/fred/series/observations"
        self.client = httpx.AsyncClient(timeout=30.0)

    async def get_series(self, series_id: str, start: datetime, end: datetime) -> list[dict]:
        """Get FRED series observations."""
        if not self.api_key:
            raise ValueError("FRED API key not configured")

        params = {
            "series_id": series_id,
            "api_key": self.api_key,
            "file_type": "json",
            "observation_start": start.strftime("%Y-%m-%d"),
            "observation_end": end.strftime("%Y-%m-%d"),
        }
        response = await self.client.get(self.base_url, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("observations", [])

    # Key FRED series for FX analysis
    SERIES = {
        "fed_funds_rate": "FEDFUNDS",
        "cpi_us": "CPIAUCSL",
        "core_cpi_us": "CPILFESL",
        "pce_us": "PCEPI",
        "core_pce_us": "PCEPILFE",
        "unemployment_us": "UNRATE",
        "gdp_us": "GDP",
        "dxy": "DTWEXBGS",  # Trade Weighted US Dollar Index
        "vix": "VIXCLS",
        "embi_br": "EMBIGBRZ",  # EMBI+ Brazil
        "cds_br_5y": "CDSBRAZ5Y",  # CDS 5Y Brazil
        "selic": "BRARR",  # Brazil interest rate (if available)
        "ipca_br": "BRCPI",  # Brazil IPCA (if available)
    }


class FXDataAggregator:
    """Aggregates FX data from multiple providers with fallback."""

    def __init__(self):
        self.providers: list[FXDataProvider] = []

        # Add providers in priority order
        if settings.alpha_vantage_api_key:
            self.providers.append(AlphaVantageProvider())
        if settings.exchange_rate_api_key:
            self.providers.append(ExchangeRateAPIProvider())
        if settings.currencyapi_key:
            self.providers.append(CurrencyAPIProvider())
        # YFinance as last resort (free, no key needed)
        self.providers.append(YFinanceProvider())

    async def get_spot_rate(self, base: str, target: str) -> FXRate:
        """Get spot rate with provider fallback."""
        last_error = None
        for provider in self.providers:
            try:
                return await provider.get_spot_rate(base, target)
            except Exception as e:
                last_error = e
                continue
        raise last_error or ValueError("All providers failed")

    async def get_time_series(
        self,
        base: str,
        target: str,
        start: datetime,
        end: datetime,
        interval: str = "1d",
    ) -> FXTimeSeries:
        """Get time series with provider fallback."""
        for provider in self.providers:
            try:
                return await provider.get_time_series(base, target, start, end, interval)
            except Exception:
                continue
        return FXTimeSeries(base=base, target=target, rates=[], source="none", interval=interval)

    async def get_multiple_spot_rates(self, base: str, targets: list[str]) -> dict[str, FXRate]:
        """Get spot rates for multiple targets concurrently."""
        tasks = [self.get_spot_rate(base, target) for target in targets]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return {
            target: result if isinstance(result, FXRate) else None
            for target, result in zip(targets, results)
        }

    async def get_cross_rates(self, targets: list[str], base: str = "USD") -> dict[str, FXRate]:
        """Get cross rates for multiple pairs (e.g., EUR/USD, GBP/USD)."""
        tasks = [self.get_spot_rate(base, target) for target in targets]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return {
            target: result if isinstance(result, FXRate) else None
            for target, result in zip(targets, results)
        }


# Singleton instance
_fx_aggregator: Optional[FXDataAggregator] = None


def get_fx_aggregator() -> FXDataAggregator:
    """Get global FX data aggregator instance."""
    global _fx_aggregator
    if _fx_aggregator is None:
        _fx_aggregator = FXDataAggregator()
    return _fx_aggregator


# Convenience functions
async def get_spot_rate(base: str, target: str) -> FXRate:
    """Get current spot rate."""
    return await get_fx_aggregator().get_spot_rate(base, target)


async def get_multiple_spot_rates(base: str, targets: list[str]) -> dict[str, FXRate]:
    """Get spot rates for multiple targets."""
    return await get_fx_aggregator().get_multiple_spot_rates(base, targets)


async def get_historical_rates(base: str, target: str, days: int = 365) -> list[FXRate]:
    """Get historical daily rates."""
    end = datetime.now()
    start = end - timedelta(days=days)
    ts = await get_fx_aggregator().get_time_series(base, target, start, end, "1d")
    return ts.rates


async def calculate_dca_simulation(
    base: str,
    target: str,
    total_amount: Decimal,
    installments: int,
    frequency_days: int = 7,
    lookback_days: int = 365,
) -> dict[str, Any]:
    """Simulate DCA strategy on historical data."""
    rates = await get_historical_rates(base, target, lookback_days)

    if len(rates) < installments * frequency_days:
        return {"error": "Insufficient historical data"}

    # Simulate DCA
    interval = len(rates) // installments
    purchased_amount = Decimal("0")
    total_base_spent = Decimal("0")

    for i in range(installments):
        idx = min(i * interval, len(rates) - 1)
        rate = rates[idx].rate
        amount_per_installment = total_amount / installments
        purchased_amount += amount_per_installment / rate
        total_base_spent += amount_per_installment

    avg_rate = total_base_spent / purchased_amount if purchased_amount > 0 else Decimal("0")
    final_rate = rates[-1].rate
    current_value = purchased_amount * final_rate
    pnl = current_value - total_base_spent
    pnl_pct = float(pnl / total_base_spent * 100) if total_base_spent > 0 else 0

    # Compare with lump sum at start
    lump_sum_amount = total_amount / rates[0].rate
    lump_sum_value = lump_sum_amount * final_rate
    lump_sum_pnl = lump_sum_value - total_base_spent
    lump_sum_pnl_pct = float(lump_sum_pnl / total_base_spent * 100) if total_base_spent > 0 else 0

    return {
        "strategy": "DCA",
        "installments": installments,
        "frequency_days": frequency_days,
        "total_base_spent": float(total_base_spent),
        "total_target_purchased": float(purchased_amount),
        "average_rate": float(avg_rate),
        "final_rate": float(final_rate),
        "current_value": float(current_value),
        "pnl": float(pnl),
        "pnl_pct": pnl_pct,
        "comparison": {
            "lump_sum_pnl_pct": lump_sum_pnl_pct,
            "dca_advantage_pct": pnl_pct - lump_sum_pnl_pct,
        },
        "period_analyzed": {
            "start": rates[0].timestamp.isoformat(),
            "end": rates[-1].timestamp.isoformat(),
            "data_points": len(rates),
        },
    }