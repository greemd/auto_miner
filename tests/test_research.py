"""Tests for the research loop: journal, validator, runner."""

import textwrap
from pathlib import Path

import pandas as pd
import pytest

from auto_alpha_miner.research.journal import (
    Journal,
    JournalConfig,
    TriedApproach,
    create_default_journal,
)
from auto_alpha_miner.research.validator import validate_strategy_file


# ── Journal tests ─────────────────────────────────────────────────

SAMPLE_JOURNAL = textwrap.dedent("""\
    # Research Journal

    ## Configuration
    - **benchmark_symbols**: SPY, BTC
    - **start**: 2021-01-01
    - **end**: 2023-12-31
    - **capital**: 50000

    ## Research Directions
    - Direction A
    - Direction B

    ## Tried Approaches

    ### [001] baseline_ma — 2026-04-11
    - **Approach**: SMA cross
    - **Category**: trend-following
    - **Indicators**: SMA
    - **Parameters**: fast=50, slow=200
    - **Results**:
      - SPY: sharpe=0.65, return=32.1%, mdd=18.5%, trades=12
      - BTC: sharpe=0.31, return=45.0%, mdd=35.2%, trades=8
    - **Analysis**: Decent baseline.
    - **Status**: baseline

    ### [002] research_002_rsi — 2026-04-11
    - **Approach**: RSI bounce
    - **Category**: mean-reversion
    - **Indicators**: RSI
    - **Parameters**: period=14, oversold=30, overbought=70
    - **Results**:
      - SPY: sharpe=0.40, return=15.0%, mdd=25.0%, trades=6
      - BTC: sharpe=0.20, return=10.0%, mdd=40.0%, trades=4
    - **Analysis**: Underperformed.
    - **Status**: done

    ## Next Steps
    - Try MACD
    - Add volume filter

    ## Best Results
    | Rank | Strategy | Sharpe(SPY) | Return(SPY) | MDD(SPY) |
    |------|----------|-------------|-------------|----------|
    | 1    | baseline_ma | 0.65 | 32.1% | 18.5% |
""")


class TestJournalParsing:
    def test_parse_config(self, tmp_path):
        p = tmp_path / "journal.md"
        p.write_text(SAMPLE_JOURNAL)
        j = Journal(p)
        assert j.config.benchmark_symbols == ["SPY", "BTC"]
        assert j.config.start == "2021-01-01"
        assert j.config.end == "2023-12-31"
        assert j.config.capital == 50000.0

    def test_parse_tried_approaches(self, tmp_path):
        p = tmp_path / "journal.md"
        p.write_text(SAMPLE_JOURNAL)
        j = Journal(p)
        assert len(j.tried_approaches) == 2
        assert j.tried_approaches[0].name == "baseline_ma"
        assert j.tried_approaches[0].id == 1
        assert j.tried_approaches[0].category == "trend-following"
        assert j.tried_approaches[0].indicators == ["SMA"]
        assert j.tried_approaches[0].parameters == {"fast": "50", "slow": "200"}

    def test_parse_results(self, tmp_path):
        p = tmp_path / "journal.md"
        p.write_text(SAMPLE_JOURNAL)
        j = Journal(p)
        spy_results = j.tried_approaches[0].results["SPY"]
        assert spy_results["sharpe"] == 0.65
        assert spy_results["return"] == 32.1

    def test_parse_next_steps(self, tmp_path):
        p = tmp_path / "journal.md"
        p.write_text(SAMPLE_JOURNAL)
        j = Journal(p)
        assert j.next_steps == ["Try MACD", "Add volume filter"]

    def test_parse_research_directions(self, tmp_path):
        p = tmp_path / "journal.md"
        p.write_text(SAMPLE_JOURNAL)
        j = Journal(p)
        assert j.research_directions == ["Direction A", "Direction B"]

    def test_next_id(self, tmp_path):
        p = tmp_path / "journal.md"
        p.write_text(SAMPLE_JOURNAL)
        j = Journal(p)
        assert j.next_id() == 3

    def test_has_strategy(self, tmp_path):
        p = tmp_path / "journal.md"
        p.write_text(SAMPLE_JOURNAL)
        j = Journal(p)
        assert j.has_strategy("baseline_ma")
        assert not j.has_strategy("nonexistent")


class TestJournalRoundtrip:
    def test_save_and_reload(self, tmp_path):
        p = tmp_path / "journal.md"
        p.write_text(SAMPLE_JOURNAL)
        j = Journal(p)

        # Add a new approach
        j.add_result(TriedApproach(
            id=3, name="research_003_test", date="2026-04-12",
            approach="Test approach", category="momentum",
            indicators=["MACD", "ADX"], parameters={"fast": "12", "slow": "26"},
            results={"SPY": {"sharpe_ratio": 0.80, "total_return": 40.0, "max_drawdown": 15.0, "trade_count": 10}},
            analysis="Good results.", status="done",
        ))
        j.save()

        # Reload and verify
        j2 = Journal(p)
        assert len(j2.tried_approaches) == 3
        assert j2.tried_approaches[2].name == "research_003_test"
        assert j2.tried_approaches[2].category == "momentum"
        assert j2.config.benchmark_symbols == ["SPY", "BTC"]
        assert j2.next_steps == ["Try MACD", "Add volume filter"]


class TestIsTooSimilar:
    def test_same_everything_is_too_similar(self, tmp_path):
        p = tmp_path / "journal.md"
        p.write_text(SAMPLE_JOURNAL)
        j = Journal(p)
        similar, reason = j.is_too_similar("trend-following", ["SMA"], {"fast": "50", "slow": "200"})
        assert similar
        assert "baseline_ma" in reason

    def test_different_category_is_ok(self, tmp_path):
        p = tmp_path / "journal.md"
        p.write_text(SAMPLE_JOURNAL)
        j = Journal(p)
        similar, _ = j.is_too_similar("momentum", ["SMA"], {"fast": "50", "slow": "200"})
        assert not similar

    def test_different_indicators_is_ok(self, tmp_path):
        p = tmp_path / "journal.md"
        p.write_text(SAMPLE_JOURNAL)
        j = Journal(p)
        similar, _ = j.is_too_similar("trend-following", ["EMA"], {"fast": "50", "slow": "200"})
        assert not similar

    def test_very_different_params_is_ok(self, tmp_path):
        p = tmp_path / "journal.md"
        p.write_text(SAMPLE_JOURNAL)
        j = Journal(p)
        similar, _ = j.is_too_similar("trend-following", ["SMA"], {"fast": "5", "slow": "20"})
        assert not similar

    def test_empty_journal_is_never_similar(self, tmp_path):
        p = tmp_path / "empty.md"
        j = create_default_journal(p)
        similar, _ = j.is_too_similar("anything", ["X"], {"a": "1"})
        assert not similar


class TestCreateDefaultJournal:
    def test_creates_with_defaults(self, tmp_path):
        p = tmp_path / "journal.md"
        j = create_default_journal(p)
        from auto_alpha_miner.config import RESEARCH_CONFIG
        expected = RESEARCH_CONFIG.get("benchmark_symbols", ["SPY", "QQQ", "BTC"])
        assert j.config.benchmark_symbols == expected
        assert len(j.research_directions) > 0
        assert len(j.next_steps) > 0
        j.save()
        assert p.exists()


# ── Validator tests ───────────────────────────────────────────────

class TestValidator:
    def test_valid_existing_strategy(self):
        path = Path("src/auto_alpha_miner/strategy/turtle.py")
        valid, error = validate_strategy_file(path)
        assert valid, f"Expected valid but got: {error}"

    def test_invalid_syntax(self, tmp_path):
        p = tmp_path / "bad_syntax.py"
        p.write_text("def broken(:\n  pass")
        valid, error = validate_strategy_file(p)
        assert not valid
        assert "Syntax error" in error

    def test_missing_register_decorator(self, tmp_path):
        p = tmp_path / "no_decorator.py"
        p.write_text(textwrap.dedent("""\
            from auto_alpha_miner.strategy.base import BaseStrategy, Signal
            class MyStrat(BaseStrategy):
                name = "test"
                def prepare(self, df): return df
                def generate_signals(self, df): return []
        """))
        valid, error = validate_strategy_file(p)
        assert not valid
        assert "register_strategy" in error

    def test_missing_file(self, tmp_path):
        valid, error = validate_strategy_file(tmp_path / "nonexistent.py")
        assert not valid
        assert "not found" in error

    def test_missing_name_attribute(self, tmp_path):
        p = tmp_path / "no_name.py"
        p.write_text(textwrap.dedent("""\
            from auto_alpha_miner.config import register_strategy
            from auto_alpha_miner.strategy.base import BaseStrategy, Signal
            @register_strategy
            class MyStrat(BaseStrategy):
                def prepare(self, df): return df
                def generate_signals(self, df): return []
        """))
        valid, error = validate_strategy_file(p)
        assert not valid
        assert "name" in error
