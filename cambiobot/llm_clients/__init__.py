"""LLM Client abstraction for CambioBot - supports multiple providers including OpenRouter."""

import os
import re
from dataclasses import dataclass
from typing import Any, Optional
from urllib.parse import urlparse

from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI

from .config import settings


# Provider-specific chat classes (following TradingAgents pattern)
class NormalizedChatOpenAI(ChatOpenAI):
    """ChatOpenAI with normalized content output."""

    def invoke(self, input, config=None, **kwargs):
        result = super().invoke(input, config, **kwargs)
        return self._normalize_content(result)

    def _normalize_content(self, result):
        """Normalize content from various API response formats to string."""
        if hasattr(result, 'content'):
            content = result.content
            if isinstance(content, list):
                # Handle list of content blocks (reasoning + text)
                text_parts = []
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        text_parts.append(block.get("text", ""))
                    elif isinstance(block, str):
                        text_parts.append(block)
                result.content = "\n".join(text_parts)
        return result


class DeepSeekChatOpenAI(NormalizedChatOpenAI):
    """DeepSeek-specific overrides for thinking-mode round-trip."""

    def _get_request_payload(self, input_, *, stop=None, **kwargs):
        payload = super()._get_request_payload(input_, stop=stop, **kwargs)
        outgoing = payload.get("messages", [])
        for message_dict, message in zip(outgoing, self._input_to_messages(input_), strict=False):
            if not isinstance(message, AIMessage):
                continue
            reasoning = message.additional_kwargs.get("reasoning_content")
            if reasoning is not None:
                message_dict["reasoning_content"] = reasoning
        return payload

    def _create_chat_result(self, response, generation_info=None):
        chat_result = super()._create_chat_result(response, generation_info)
        response_dict = (
            response
            if isinstance(response, dict)
            else response.model_dump(
                exclude={"choices": {"__all__": {"message": {"parsed"}}}}
            )
        )
        for generation, choice in zip(
            chat_result.generations, response_dict.get("choices", []), strict=False
        ):
            reasoning = choice.get("message", {}).get("reasoning_content")
            if reasoning is not None:
                generation.message.additional_kwargs["reasoning_content"] = reasoning
        return chat_result

    def _input_to_messages(self, input_) -> list:
        if isinstance(input_, list):
            return input_
        if hasattr(input_, "to_messages"):
            return input_.to_messages()
        return []


class MinimaxChatOpenAI(NormalizedChatOpenAI):
    """MiniMax-specific overrides for reasoning_split."""

    def _get_request_payload(self, input_, *, stop=None, **kwargs):
        payload = super()._get_request_payload(input_, stop=stop, **kwargs)
        # MiniMax M2.x reasoning models need reasoning_split=True
        # This is handled via capabilities in TradingAgents
        return payload


class LocalCompatibleChatOpenAI(NormalizedChatOpenAI):
    """OpenAI-compatible client for arbitrary local servers (LM Studio, vLLM, llama.cpp)."""

    def with_structured_output(self, schema, *, method=None, **kwargs):
        # Local servers often reject tool_choice object
        kwargs.setdefault("tool_choice", None)
        return super().with_structured_output(schema, method=method, **kwargs)


# Provider specifications (single source of truth, following TradingAgents)
@dataclass(frozen=True)
class ProviderSpec:
    """Declarative config for one OpenAI-compatible provider."""
    chat_class: type = NormalizedChatOpenAI
    base_url: str | None = None
    base_url_env: str | None = None
    key_optional: bool = False
    placeholder_key: str = "EMPTY"
    require_base_url: bool = False
    use_responses_api: bool = False


# OpenAI-compatible provider registry (includes OpenRouter)
OPENAI_COMPATIBLE_PROVIDERS: dict[str, ProviderSpec] = {
    "openai": ProviderSpec(use_responses_api=True),
    "xai": ProviderSpec(base_url="https://api.x.ai/v1"),
    "deepseek": ProviderSpec(base_url="https://api.deepseek.com", chat_class=DeepSeekChatOpenAI),
    "qwen": ProviderSpec(base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1"),
    "qwen-cn": ProviderSpec(base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"),
    "glm": ProviderSpec(base_url="https://api.z.ai/api/paas/v4/"),
    "glm-cn": ProviderSpec(base_url="https://open.bigmodel.cn/api/paas/v4/"),
    "minimax": ProviderSpec(base_url="https://api.minimax.io/v1", chat_class=MinimaxChatOpenAI),
    "minimax-cn": ProviderSpec(base_url="https://api.minimaxi.com/v1", chat_class=MinimaxChatOpenAI),
    "openrouter": ProviderSpec(base_url="https://openrouter.ai/api/v1"),
    "mistral": ProviderSpec(base_url="https://api.mistral.ai/v1"),
    "kimi": ProviderSpec(base_url="https://api.moonshot.ai/v1"),
    "groq": ProviderSpec(base_url="https://api.groq.com/openai/v1"),
    "nvidia": ProviderSpec(base_url="https://integrate.api.nvidia.com/v1"),
    "ollama": ProviderSpec(
        base_url="http://localhost:11434/v1",
        base_url_env="OLLAMA_BASE_URL",
        key_optional=True,
        placeholder_key="ollama"
    ),
    "openai_compatible": ProviderSpec(
        require_base_url=True,
        key_optional=True,
        chat_class=LocalCompatibleChatOpenAI
    ),
}


# Provider -> API key env var mapping
PROVIDER_API_KEY_ENV: dict[str, str | None] = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "google": "GOOGLE_API_KEY",
    "azure": "AZURE_OPENAI_API_KEY",
    "bedrock": None,
    "xai": "XAI_API_KEY",
    "deepseek": "DEEPSEEK_API_KEY",
    "qwen": "DASHSCOPE_API_KEY",
    "qwen-cn": "DASHSCOPE_CN_API_KEY",
    "glm": "ZHIPU_API_KEY",
    "glm-cn": "ZHIPU_CN_API_KEY",
    "minimax": "MINIMAX_API_KEY",
    "minimax-cn": "MINIMAX_CN_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
    "mistral": "MISTRAL_API_KEY",
    "kimi": "MOONSHOT_API_KEY",
    "groq": "GROQ_API_KEY",
    "nvidia": "NVIDIA_API_KEY",
    "ollama": None,
    "openai_compatible": "OPENAI_COMPATIBLE_API_KEY",
}


def get_api_key_env(provider: str) -> str | None:
    """Return the env var name for provider's API key."""
    return PROVIDER_API_KEY_ENV.get(provider.lower())


# Passthrough kwargs for ChatOpenAI
_PASSTHROUGH_KWARGS = (
    "timeout", "max_retries", "reasoning_effort", "temperature", "max_tokens",
    "api_key", "callbacks", "http_client", "http_async_client",
)

_OPENAI_REASONING_MODEL = re.compile(r"^(gpt-5|o[1-9])")


def _supports_reasoning_effort(model: str) -> bool:
    return bool(_OPENAI_REASONING_MODEL.match(model.lower().strip()))


def _is_native_openai_base_url(base_url: str | None) -> bool:
    if not base_url:
        return True
    if "://" not in base_url:
        base_url = "https://" + base_url
    host = urlparse(base_url).hostname or ""
    return host == "api.openai.com" or host.endswith(".openai.com")


class LLMClient:
    """Unified LLM client for CambioBot supporting multiple providers."""

    def __init__(
        self,
        model: str,
        provider: str | None = None,
        base_url: str | None = None,
        **kwargs,
    ):
        self.model = model
        self.provider = (provider or settings.llm_provider).lower()
        self.base_url = base_url
        self.kwargs = kwargs

    def get_llm(self) -> Any:
        """Return a configured LLM instance based on provider."""
        self._warn_if_unknown_model()

        llm_kwargs = {"model": self.model}
        provider_lower = self.provider

        # Handle OpenAI-compatible providers (including OpenRouter)
        if provider_lower in OPENAI_COMPATIBLE_PROVIDERS:
            return self._create_openai_compatible_llm(llm_kwargs)

        # Handle native Anthropic
        if provider_lower == "anthropic":
            return self._create_anthropic_llm(llm_kwargs)

        # Handle native Google
        if provider_lower == "google":
            return self._create_google_llm(llm_kwargs)

        # Handle Azure
        if provider_lower == "azure":
            return self._create_azure_llm(llm_kwargs)

        # Handle Bedrock
        if provider_lower == "bedrock":
            return self._create_bedrock_llm(llm_kwargs)

        raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def _create_openai_compatible_llm(self, llm_kwargs: dict) -> Any:
        """Create LLM for OpenAI-compatible providers (OpenRouter, etc)."""
        spec = OPENAI_COMPATIBLE_PROVIDERS[self.provider]
        chat_cls = spec.chat_class

        # Resolve base_url: explicit > env override > provider default
        env_base_url = os.environ.get(spec.base_url_env) if spec.base_url_env else None
        base_url = self.base_url or env_base_url or spec.base_url

        if spec.require_base_url and not base_url:
            raise ValueError(
                f"Provider '{self.provider}' requires a base_url. Set via "
                "backend_url / TRADINGAGENTS_LLM_BACKEND_URL to your endpoint."
            )

        if base_url:
            llm_kwargs["base_url"] = base_url

        # API key handling
        api_key_env = get_api_key_env(self.provider)
        api_key = os.environ.get(api_key_env) if api_key_env else None

        # OpenRouter specific: add headers
        if self.provider == "openrouter":
            llm_kwargs.setdefault("default_headers", {}).update({
                "HTTP-Referer": settings.openrouter_site_url,
                "X-Title": settings.openrouter_app_name,
            })

        if api_key:
            llm_kwargs["api_key"] = api_key
        elif spec.key_optional:
            llm_kwargs["api_key"] = spec.placeholder_key
        elif api_key_env:
            raise ValueError(
                f"API key for provider '{self.provider}' is not set. "
                f"Please set {api_key_env} environment variable."
            )

        # Responses API only for native OpenAI
        if spec.use_responses_api and _is_native_openai_base_url(base_url):
            llm_kwargs["use_responses_api"] = True

        # Forward user-provided kwargs
        for key in _PASSTHROUGH_KWARGS:
            if key not in self.kwargs:
                continue
            if key == "reasoning_effort" and not _supports_reasoning_effort(self.model):
                continue
            llm_kwargs[key] = self.kwargs[key]

        return chat_cls(**llm_kwargs)

    def _create_anthropic_llm(self, llm_kwargs: dict) -> Any:
        """Create Anthropic LLM client."""
        from langchain_anthropic import ChatAnthropic

        api_key = os.environ.get("ANTHROPIC_API_KEY") or settings.anthropic_api_key
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")

        llm_kwargs["api_key"] = api_key
        return ChatAnthropic(**llm_kwargs)

    def _create_google_llm(self, llm_kwargs: dict) -> Any:
        """Create Google Gemini LLM client."""
        from langchain_google_genai import ChatGoogleGenerativeAI

        api_key = os.environ.get("GOOGLE_API_KEY") or settings.google_api_key
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not set")

        llm_kwargs["api_key"] = api_key
        return ChatGoogleGenerativeAI(**llm_kwargs)

    def _create_azure_llm(self, llm_kwargs: dict) -> Any:
        """Create Azure OpenAI LLM client."""
        from langchain_openai import AzureChatOpenAI

        api_key = os.environ.get("AZURE_OPENAI_API_KEY")
        endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
        api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-01")

        if not api_key or not endpoint:
            raise ValueError("AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT required")

        llm_kwargs.update({
            "azure_endpoint": endpoint,
            "api_key": api_key,
            "api_version": api_version,
            "azure_deployment": self.model,
        })
        return AzureChatOpenAI(**llm_kwargs)

    def _create_bedrock_llm(self, llm_kwargs: dict) -> Any:
        """Create AWS Bedrock LLM client."""
        from langchain_aws import ChatBedrockConverse

        # Bedrock uses AWS credential chain
        region = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
        llm_kwargs["region_name"] = region
        llm_kwargs["model"] = self.model
        return ChatBedrockConverse(**llm_kwargs)

    def _warn_if_unknown_model(self) -> None:
        """Warn if model might not be supported by provider."""
        # This is a soft check - providers may support models not in our catalog
        pass

    def validate_model(self) -> bool:
        """Validate model for the provider (best effort)."""
        return True  # Defer to provider API


def create_llm(
    model: str | None = None,
    provider: str | None = None,
    **kwargs,
) -> Any:
    """Factory function to create LLM instance."""
    model = model or settings.deep_think_llm
    provider = provider or settings.llm_provider
    client = LLMClient(model=model, provider=provider, **kwargs)
    return client.get_llm()


def create_deep_llm(**kwargs) -> Any:
    """Create deep thinking LLM (for complex reasoning)."""
    return create_llm(model=settings.deep_think_llm, **kwargs)


def create_quick_llm(**kwargs) -> Any:
    """Create quick thinking LLM (for simple tasks)."""
    return create_llm(model=settings.quick_think_llm, **kwargs)