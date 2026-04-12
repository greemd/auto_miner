"""Research journal parsing, repetition detection, and result recording."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path


@dataclass
class JournalConfig:
    """Parsed configuration from the journal."""

    benchmark_symbols: list[str] = field(default_factory=lambda: ["SPY", "QQQ", "BTC"])
    start: str = "2020-01-01"
    end: str = "2024-12-31"
    capital: float = 100_000.0


@dataclass
class TriedApproach:
    """A single tried approach entry."""

    id: int = 0
    name: str = ""
    date: str = ""
    approach: str = ""
    category: str = ""
    indicators: list[str] = field(default_factory=list)
    parameters: dict[str, str] = field(default_factory=dict)
    results: dict[str, dict[str, float]] = field(default_factory=dict)
    analysis: str = ""
    status: str = ""


class Journal:
    """Parse and manage the research journal markdown file."""

    def __init__(self, path: Path):
        self.path = path
        self._raw: str = ""
        self.config = JournalConfig()
        self.tried_approaches: list[TriedApproach] = []
        self.research_directions: list[str] = []
        self.next_steps: list[str] = []
        self.best_results_raw: str = ""

        if path.exists():
            self._raw = path.read_text(encoding="utf-8")
            self._parse()

    def _parse(self) -> None:
        """Parse the markdown into structured data."""
        sections = self._split_sections(self._raw)

        if "Configuration" in sections:
            self.config = self._parse_config(sections["Configuration"])
        if "Research Directions" in sections:
            self.research_directions = self._parse_list(sections["Research Directions"])
        if "Tried Approaches" in sections:
            self.tried_approaches = self._parse_tried(sections["Tried Approaches"])
        if "Next Steps" in sections:
            self.next_steps = self._parse_list(sections["Next Steps"])
        if "Best Results" in sections:
            self.best_results_raw = sections["Best Results"].strip()

    def _split_sections(self, text: str) -> dict[str, str]:
        """Split markdown by ## headers into a dict."""
        sections: dict[str, str] = {}
        current_name = ""
        current_lines: list[str] = []

        for line in text.split("\n"):
            if line.startswith("## "):
                if current_name:
                    sections[current_name] = "\n".join(current_lines)
                current_name = line[3:].strip()
                current_lines = []
            else:
                current_lines.append(line)

        if current_name:
            sections[current_name] = "\n".join(current_lines)

        return sections

    def _parse_config(self, text: str) -> JournalConfig:
        config = JournalConfig()
        for line in text.split("\n"):
            m = re.match(r"^- \*\*(\w+)\*\*:\s*(.+)$", line.strip())
            if not m:
                continue
            key, val = m.group(1), m.group(2).strip()
            if key == "benchmark_symbols":
                config.benchmark_symbols = [s.strip() for s in val.split(",")]
            elif key == "start":
                config.start = val
            elif key == "end":
                config.end = val
            elif key == "capital":
                config.capital = float(val)
        return config

    def _parse_list(self, text: str) -> list[str]:
        items: list[str] = []
        for line in text.split("\n"):
            line = line.strip()
            if line.startswith("- "):
                items.append(line[2:].strip())
        return items

    def _parse_tried(self, text: str) -> list[TriedApproach]:
        """Parse ### [NNN] entries within the Tried Approaches section."""
        approaches: list[TriedApproach] = []
        # Split by ### headers
        entries = re.split(r"^### ", text, flags=re.MULTILINE)

        for entry in entries:
            entry = entry.strip()
            if not entry:
                continue
            # Parse header: [001] name — date
            header_match = re.match(r"\[(\d+)\]\s+(\S+)\s+—\s+(.+)", entry.split("\n")[0])
            if not header_match:
                continue

            approach = TriedApproach(
                id=int(header_match.group(1)),
                name=header_match.group(2),
                date=header_match.group(3).strip(),
            )

            # Parse fields
            for line in entry.split("\n")[1:]:
                line = line.strip()
                m = re.match(r"^- \*\*(\w+)\*\*:\s*(.+)$", line)
                if not m:
                    # Check for result sub-items
                    rm = re.match(r"^- (\w+):\s*(.+)$", line)
                    if rm and approach.results is not None:
                        symbol = rm.group(1)
                        metrics = self._parse_inline_metrics(rm.group(2))
                        if metrics:
                            approach.results[symbol] = metrics
                    continue

                key, val = m.group(1), m.group(2).strip()
                if key == "Approach":
                    approach.approach = val
                elif key == "Category":
                    approach.category = val
                elif key == "Indicators":
                    approach.indicators = [s.strip() for s in val.split(",")]
                elif key == "Parameters":
                    approach.parameters = self._parse_inline_params(val)
                elif key == "Analysis":
                    approach.analysis = val
                elif key == "Status":
                    approach.status = val

            approaches.append(approach)

        return approaches

    def _parse_inline_metrics(self, text: str) -> dict[str, float]:
        """Parse 'sharpe=0.65, return=32.1%, mdd=18.5%, trades=12'."""
        metrics: dict[str, float] = {}
        for pair in text.split(","):
            pair = pair.strip()
            if "=" not in pair:
                continue
            k, v = pair.split("=", 1)
            k = k.strip()
            v = v.strip().rstrip("%")
            try:
                metrics[k] = float(v)
            except ValueError:
                continue
        return metrics

    def _parse_inline_params(self, text: str) -> dict[str, str]:
        """Parse 'fast=50, slow=200'."""
        params: dict[str, str] = {}
        for pair in text.split(","):
            pair = pair.strip()
            if "=" not in pair:
                continue
            k, v = pair.split("=", 1)
            params[k.strip()] = v.strip()
        return params

    def next_id(self) -> int:
        """Return the next available approach ID."""
        if not self.tried_approaches:
            return 1
        return max(a.id for a in self.tried_approaches) + 1

    def is_too_similar(self, category: str, indicators: list[str], parameters: dict[str, str]) -> tuple[bool, str]:
        """Check if a proposed approach is too similar to an existing one.

        Returns (True, reason) if too similar, (False, "") otherwise.
        """
        ind_set = set(i.upper() for i in indicators)

        for existing in self.tried_approaches:
            # Must match on ALL three criteria to be "too similar"
            same_category = existing.category.lower().strip() == category.lower().strip()
            existing_ind_set = set(i.upper() for i in existing.indicators)
            same_indicators = ind_set == existing_ind_set

            if not (same_category and same_indicators):
                continue

            # Check parameter overlap
            if not parameters or not existing.parameters:
                return True, f"Too similar to [{existing.id:03d}] {existing.name}: same category and indicators"

            all_keys = set(parameters.keys()) | set(existing.parameters.keys())
            matching = sum(1 for k in all_keys if parameters.get(k) == existing.parameters.get(k))
            overlap = matching / len(all_keys) if all_keys else 1.0

            if overlap > 0.7:
                return True, f"Too similar to [{existing.id:03d}] {existing.name}: {overlap:.0%} parameter overlap"

        return False, ""

    def has_strategy(self, name: str) -> bool:
        """Check if a strategy name already exists in tried approaches."""
        return any(a.name == name for a in self.tried_approaches)

    def add_result(self, approach: TriedApproach) -> None:
        """Add a new tried approach."""
        self.tried_approaches.append(approach)

    def update_best_results(self) -> None:
        """Rebuild best results table from tried approaches, sorted by avg Sharpe."""
        entries: list[tuple[str, float, float, float]] = []
        for a in self.tried_approaches:
            spy_metrics = a.results.get("SPY", {})
            sharpe = spy_metrics.get("sharpe", spy_metrics.get("sharpe_ratio", 0.0))
            ret = spy_metrics.get("return", spy_metrics.get("total_return", 0.0))
            mdd = spy_metrics.get("mdd", spy_metrics.get("max_drawdown", 0.0))
            entries.append((a.name, sharpe, ret, mdd))

        entries.sort(key=lambda x: x[1], reverse=True)

        lines = ["| Rank | Strategy | Sharpe(SPY) | Return(SPY) | MDD(SPY) |"]
        lines.append("|------|----------|-------------|-------------|----------|")
        for i, (name, sharpe, ret, mdd) in enumerate(entries, 1):
            lines.append(f"| {i} | {name} | {sharpe:.2f} | {ret:.1f}% | {mdd:.1f}% |")

        self.best_results_raw = "\n".join(lines)

    def save(self) -> None:
        """Write the journal back to disk."""
        self.path.parent.mkdir(parents=True, exist_ok=True)

        lines: list[str] = []
        lines.append("# Research Journal\n")

        # Configuration
        lines.append("## Configuration")
        lines.append(f"- **benchmark_symbols**: {', '.join(self.config.benchmark_symbols)}")
        lines.append(f"- **start**: {self.config.start}")
        lines.append(f"- **end**: {self.config.end}")
        lines.append(f"- **capital**: {int(self.config.capital)}")
        lines.append("")

        # Research Directions
        lines.append("## Research Directions")
        for d in self.research_directions:
            lines.append(f"- {d}")
        lines.append("")

        # Tried Approaches
        lines.append("## Tried Approaches")
        lines.append("")
        for a in self.tried_approaches:
            lines.append(f"### [{a.id:03d}] {a.name} — {a.date}")
            lines.append(f"- **Approach**: {a.approach}")
            lines.append(f"- **Category**: {a.category}")
            lines.append(f"- **Indicators**: {', '.join(a.indicators)}")
            if a.parameters:
                params_str = ", ".join(f"{k}={v}" for k, v in a.parameters.items())
                lines.append(f"- **Parameters**: {params_str}")
            lines.append("- **Results**:")
            for symbol, metrics in a.results.items():
                parts = []
                for mk, mv in metrics.items():
                    if mk in ("total_return", "return"):
                        parts.append(f"return={mv:.1f}%")
                    elif mk in ("max_drawdown", "mdd"):
                        parts.append(f"mdd={mv:.1f}%")
                    elif mk in ("sharpe_ratio", "sharpe"):
                        parts.append(f"sharpe={mv:.2f}")
                    elif mk == "trade_count":
                        parts.append(f"trades={int(mv)}")
                    elif mk == "win_rate":
                        parts.append(f"win_rate={mv:.1f}%")
                    elif mk == "profit_factor":
                        parts.append(f"pf={mv:.2f}")
                    elif mk == "cagr":
                        parts.append(f"cagr={mv:.1f}%")
                lines.append(f"  - {symbol}: {', '.join(parts)}")
            lines.append(f"- **Analysis**: {a.analysis}")
            lines.append(f"- **Status**: {a.status}")
            lines.append("")

        # Next Steps
        lines.append("## Next Steps")
        for s in self.next_steps:
            lines.append(f"- {s}")
        lines.append("")

        # Best Results
        lines.append("## Best Results")
        lines.append(self.best_results_raw)
        lines.append("")

        self.path.write_text("\n".join(lines), encoding="utf-8")


def create_default_journal(path: Path) -> Journal:
    """Create a new journal with configuration from config.yaml."""
    from auto_alpha_miner.config import RESEARCH_CONFIG

    journal = Journal.__new__(Journal)
    journal.path = path
    journal._raw = ""

    rc = RESEARCH_CONFIG
    journal.config = JournalConfig(
        benchmark_symbols=rc.get("benchmark_symbols", ["SPY", "QQQ", "BTC"]),
        start=rc.get("start", "2020-01-01"),
        end=rc.get("end", "2024-12-31"),
        capital=float(rc.get("capital", 100_000)),
    )
    journal.tried_approaches = []
    journal.research_directions = [
        "모멘텀 기반 전략 (ADX, MACD, Aroon 등 트렌드 지표 활용)",
        "평균회귀 전략 (볼린저 밴드, RSI, CCI 등 오실레이터 활용)",
        "브레이크아웃 전략 (도치안 채널, ATR 기반 변동성 돌파)",
        "복합 지표 전략 (트렌드 + 모멘텀 + 거래량 조합)",
        "멀티 타임프레임 시그널 확인",
    ]
    journal.next_steps = [
        "기존 3개 전략(turtle, rsi, ma_cross) baseline 결과 기록 완료",
        "모멘텀 기반 전략 탐색: ADX + EMA 조합",
        "평균회귀 전략 탐색: 볼린저 밴드 + 거래량 확인",
        "MACD 기반 시그널 전략 시도",
    ]
    journal.best_results_raw = "| Rank | Strategy | Sharpe(SPY) | Return(SPY) | MDD(SPY) |\n|------|----------|-------------|-------------|----------|"
    return journal
