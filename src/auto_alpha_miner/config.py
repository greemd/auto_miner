"""Symbol mappings, universes, and strategy registry."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import yaml

if TYPE_CHECKING:
    from auto_alpha_miner.strategy.base import BaseStrategy

# Default config path: project root config.yaml
_DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[2] / "config.yaml"


def _load_config(path: Path | None = None) -> dict:
    """Load YAML config file."""
    config_path = path or _DEFAULT_CONFIG_PATH
    if config_path.exists():
        with open(config_path) as f:
            return yaml.safe_load(f) or {}
    return {}


_config = _load_config()

SYMBOL_MAP: dict[str, str] = _config.get("symbols", {})
UNIVERSES: dict[str, list[str]] = _config.get("universes", {})
RESEARCH_CONFIG: dict = _config.get("research", {})
DASHBOARD_API_KEY: str = _config.get("dashboard", {}).get("api_key", "")

STRATEGY_REGISTRY: dict[str, type[BaseStrategy]] = {}


def register_strategy(cls: type[BaseStrategy]) -> type[BaseStrategy]:
    """Decorator to register a strategy class by its name attribute."""
    STRATEGY_REGISTRY[cls.name] = cls
    return cls


def reload_config(path: Path | None = None) -> None:
    """Reload config from disk (useful for testing)."""
    global _config, SYMBOL_MAP, UNIVERSES
    _config = _load_config(path)
    SYMBOL_MAP.clear()
    SYMBOL_MAP.update(_config.get("symbols", {}))
    UNIVERSES.clear()
    UNIVERSES.update(_config.get("universes", {}))
