from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

if TYPE_CHECKING:
    from auto_alpha_miner.strategy.base import BaseStrategy


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Default config path: project root config.yaml
    config_path: Path = Field(default_factory=lambda: Path(__file__).resolve().parents[2] / "config.yaml")

    symbols: dict[str, str] = {}
    universes: dict[str, list[str]] = {}
    research: dict = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._load_config_from_yaml()

    def _load_config_from_yaml(self):
        if self.config_path.exists():
            with open(self.config_path) as f:
                yaml_config = yaml.safe_load(f) or {}
                self.symbols.update(yaml_config.get("symbols", {}))
                self.universes.update(yaml_config.get("universes", {}))
                self.research.update(yaml_config.get("research", {}))


settings = Settings()

SYMBOL_MAP: dict[str, str] = settings.symbols
UNIVERSES: dict[str, list[str]] = settings.universes
RESEARCH_CONFIG: dict = settings.research

STRATEGY_REGISTRY: dict[str, type[BaseStrategy]] = {}


def register_strategy(cls: type[BaseStrategy]) -> type[BaseStrategy]:
    """Decorator to register a strategy class by its name attribute."""
    STRATEGY_REGISTRY[cls.name] = cls
    return cls


def reload_config(path: Path | None = None) -> None:
    """Reload config from disk (useful for testing)."""
    global settings, SYMBOL_MAP, UNIVERSES, RESEARCH_CONFIG
    if path:
        settings.config_path = path
    settings._load_config_from_yaml()
    SYMBOL_MAP.clear()
    SYMBOL_MAP.update(settings.symbols)
    UNIVERSES.clear()
    UNIVERSES.update(settings.universes)
    RESEARCH_CONFIG.clear()
    RESEARCH_CONFIG.update(settings.research)
