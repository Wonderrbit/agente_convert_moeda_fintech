"""Configuration settings for CambioBot."""

import os
from functools import lru_cache
from typing import Any, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "CambioBot"
    app_version: str = "0.1.0"
    debug: bool = False
    environment: str = "development"  # development, staging, production

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/cambiobot",
        description="PostgreSQL async connection URL",
    )
    database_pool_size: int = 10
    database_max_overflow: int = 20

    # Redis
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL",
    )
    redis_max_connections: int = 50

    # Evolution API (WhatsApp)
    evolution_api_url: str = Field(
        default="http://localhost:8080",
        description="Evolution API base URL",
    )
    evolution_api_key: str = Field(
        default="",
        description="Evolution API key",
    )
    evolution_instance_name: str = "cambiobot"

    # LLM Providers (at least one required)
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    openrouter_api_key: Optional[str] = None
    deepseek_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    xai_api_key: Optional[str] = None
    mistral_api_key: Optional[str] = None
    dashscope_api_key: Optional[str] = None
    zhipu_api_key: Optional[str] = None
    minimax_api_key: Optional[str] = None
    ollama_base_url: str = "http://localhost:11434/v1"

    # LLM Configuration
    llm_provider: str = "openrouter"  # openai, anthropic, google, openrouter, deepseek, groq, xai, mistral, ollama, openai_compatible
    deep_think_llm: str = "anthropic/claude-3.5-sonnet"  # Model for complex reasoning
    quick_think_llm: str = "openai/gpt-4o-mini"  # Model for quick tasks
    backend_url: Optional[str] = None  # Custom OpenAI-compatible endpoint
    temperature: float = 0.1
    max_tokens: int = 8192
    llm_max_retries: int = 3

    # OpenRouter specific
    openrouter_site_url: str = "https://github.com/Wonderrbit/agente_convert_moeda_fintech"
    openrouter_app_name: str = "CambioBot"

    # TradingAgents Integration
    tradingagents_enabled: bool = True
    tradingagents_debug: bool = False
    tradingagents_max_debate_rounds: int = 1
    tradingagents_max_risk_rounds: int = 1
    tradingagents_checkpoint_enabled: bool = False
    tradingagents_data_vendors: dict = Field(
        default_factory=lambda: {
            "core_stock_apis": "yfinance",
            "technical_indicators": "yfinance",
            "fundamental_data": "yfinance",
            "news_data": "yfinance",
            "macro_data": "fred",
            "prediction_markets": "polymarket",
        }
    )

    # FX Data Providers
    alpha_vantage_api_key: Optional[str] = None
    fred_api_key: Optional[str] = None
    exchange_rate_api_key: Optional[str] = None  # exchangerate-api.com
    currencyapi_key: Optional[str] = None  # currencyapi.com

    # Observability
    langfuse_public_key: Optional[str] = None
    langfuse_secret_key: Optional[str] = None
    langfuse_host: str = "https://cloud.langfuse.com"
    grafana_url: str = "http://localhost:3000"
    prometheus_port: int = 9090

    # Affiliate Partners
    nomad_affiliate_url: str = "https://nomad.app.link/cambiobot?utm_source=cambiobot"
    wise_affiliate_url: str = "https://wise.com/invite/cambiobot"
    avenue_affiliate_url: str = "https://avenue.us/cambiobot"
    western_union_affiliate_url: str = "https://westernunion.com.br/cambiobot"

    # Security
    secret_key: str = Field(
        default="dev-secret-change-in-production",
        description="Secret key for JWT/sessions",
    )
    encryption_key: Optional[str] = None
    webhook_secret: Optional[str] = None

    # Monitoring
    sentry_dsn: Optional[str] = None
    log_level: str = "INFO"
    log_format: str = "json"  # json, console

    @field_validator("llm_provider")
    @classmethod
    def validate_llm_provider(cls, v: str) -> str:
        valid = {
            "openai", "anthropic", "google", "openrouter", "deepseek",
            "groq", "xai", "mistral", "ollama", "openai_compatible",
            "azure", "bedrock",
        }
        if v.lower() not in valid:
            raise ValueError(f"Invalid llm_provider: {v}. Must be one of {valid}")
        return v.lower()

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        valid = {"development", "staging", "production"}
        if v.lower() not in valid:
            raise ValueError(f"Invalid environment: {v}. Must be one of {valid}")
        return v.lower()

    def get_llm_api_key(self) -> Optional[str]:
        """Get the API key for the configured LLM provider."""
        key_map = {
            "openai": self.openai_api_key,
            "anthropic": self.anthropic_api_key,
            "google": self.google_api_key,
            "openrouter": self.openrouter_api_key,
            "deepseek": self.deepseek_api_key,
            "groq": self.groq_api_key,
            "xai": self.xai_api_key,
            "mistral": self.mistral_api_key,
            "qwen": self.dashscope_api_key,
            "glm": self.zhipu_api_key,
            "minimax": self.minimax_api_key,
            "ollama": None,
            "openai_compatible": None,  # Uses OPENAI_COMPATIBLE_API_KEY if set
        }
        return key_map.get(self.llm_provider.lower())

    def to_tradingagents_config(self) -> dict[str, Any]:
        """Convert settings to TradingAgents config dict."""
        return {
            "llm_provider": self.llm_provider,
            "deep_think_llm": self.deep_think_llm,
            "quick_think_llm": self.quick_think_llm,
            "backend_url": self.backend_url,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "llm_max_retries": self.llm_max_retries,
            "max_debate_rounds": self.tradingagents_max_debate_rounds,
            "max_risk_discuss_rounds": self.tradingagents_max_risk_rounds,
            "checkpoint_enabled": self.tradingagents_checkpoint_enabled,
            "data_vendors": self.tradingagents_data_vendors,
            "debug": self.tradingagents_debug,
        }


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()