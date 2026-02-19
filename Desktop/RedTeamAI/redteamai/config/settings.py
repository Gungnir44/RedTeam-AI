"""Pydantic Settings for RedTeam AI configuration."""
from __future__ import annotations
from typing import Optional, Literal
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class OllamaSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="REDTEAMAI_OLLAMA_")
    host: str = "http://localhost:11434"
    model: str = "llama3.1:8b"
    timeout: int = 120
    use_xml_fallback: bool = True  # For models without native tool calling


class GroqSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="REDTEAMAI_GROQ_")
    api_key: str = ""
    model: str = "llama3-70b-8192"
    timeout: int = 60


class AnthropicSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="REDTEAMAI_ANTHROPIC_")
    api_key: str = ""
    model: str = "claude-sonnet-4-5-20250929"
    timeout: int = 120
    max_tokens: int = 4096


class OpenAICompatSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="REDTEAMAI_OPENAI_")
    api_key: str = ""
    base_url: str = "https://api.openai.com/v1"
    model: str = "gpt-4o-mini"
    timeout: int = 120


class ToolPaths(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="REDTEAMAI_TOOL_")
    nmap: str = "nmap"
    whois: str = "whois"
    dig: str = "dig"
    gobuster: str = "gobuster"
    ffuf: str = "ffuf"
    nikto: str = "nikto"
    whatweb: str = "whatweb"
    theharvester: str = "theHarvester"
    subfinder: str = "subfinder"
    searchsploit: str = "searchsploit"
    metasploit_rpc_host: str = "127.0.0.1"
    metasploit_rpc_port: int = 55553
    metasploit_rpc_password: str = ""
    wsl_path: str = "wsl"


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="REDTEAMAI_",
        env_nested_delimiter="__",
    )
    # Active backend
    ai_backend: Literal["ollama", "groq", "anthropic", "openai_compat"] = "ollama"

    # Sub-settings (populated from toml/env)
    ollama: OllamaSettings = Field(default_factory=OllamaSettings)
    groq: GroqSettings = Field(default_factory=GroqSettings)
    anthropic: AnthropicSettings = Field(default_factory=AnthropicSettings)
    openai_compat: OpenAICompatSettings = Field(default_factory=OpenAICompatSettings)
    tools: ToolPaths = Field(default_factory=ToolPaths)

    # UI
    nav_expanded: bool = True
    ai_panel_width: int = 380
    theme: str = "dark"
    font_size: int = 13

    # Agent
    max_agent_iterations: int = 10
    require_confirm_dangerous: bool = True
    auto_save_session: bool = True

    # NVD API (free, no key needed for limited rate)
    nvd_api_key: str = ""
