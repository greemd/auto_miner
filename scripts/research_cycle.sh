#!/usr/bin/env bash
# Run one research cycle via Claude Code.
# Usage: ./scripts/research_cycle.sh

set -euo pipefail
cd "$(dirname "$0")/.."

export PATH="$HOME/.local/bin:$HOME/.cargo/bin:/usr/local/bin:$PATH"

exec 9>/tmp/auto_miner_research_cycle.lock
flock -n 9 || { echo "research_cycle already running — exiting"; exit 0; }

JOURNAL="research/journal.md"

if [ ! -f "$JOURNAL" ]; then
  echo "Journal not found. Initializing..."
  uv run auto-miner research-init
fi

claude -p "$(cat <<'PROMPT'
You are an automated quant strategy researcher. Execute exactly ONE research cycle.

## Project Context
- Working directory contains a Python quant backtesting framework.
- Strategies are in `src/auto_alpha_miner/strategy/` and auto-discovered.
- Each strategy inherits `BaseStrategy`, uses `@register_strategy`, implements `prepare()` (add indicators via pandas-ta) and `generate_signals()` (return list of Signal).
- Available pandas-ta indicators: sma, ema, rsi, macd, bbands, adx, atr, donchian, stoch, cci, obv, supertrend, aroon, psar, willr, roc, mfi, cmf, vwap, etc.

## Your Task — Execute ONE cycle:

### Step 1: Read & Analyze
- Read `research/journal.md`
- Identify what has been tried (Tried Approaches)
- Identify what to try next (Next Steps)
- Note the best Sharpe(SPY) to beat

### Step 2: Develop a New Strategy
- Pick a direction from Next Steps that is DIFFERENT from all Tried Approaches
- The strategy name MUST follow the format: `research_NNN_descriptive_name` where NNN is the next ID from the journal
- Write the strategy file to `src/auto_alpha_miner/strategy/research_NNN_descriptive_name.py`
- The strategy MUST:
  - Import and use `@register_strategy` from `auto_alpha_miner.config`
  - Import `BaseStrategy, Signal` from `auto_alpha_miner.strategy.base`
  - Set a `name` class attribute matching the filename stem
  - Implement `prepare(self, df)` — add indicator columns using pandas_ta, call `df.dropna(inplace=True)`, return df
  - Implement `generate_signals(self, df)` — iterate rows, track `in_position` state, return list of Signal(date=, action="BUY"/"SELL")
- Use existing strategies in `src/auto_alpha_miner/strategy/` as reference for the pattern

### Step 3: Validate
- Run: `uv run auto-miner research-validate --file src/auto_alpha_miner/strategy/<filename>.py`
- If INVALID, fix the code and re-validate (up to 3 attempts)

### Step 4: Backtest
- Run: `uv run auto-miner research-run --strategy <strategy_name>`
- Read the structured output

### Step 5: Update Journal
- Read the current `research/journal.md`
- Append a new entry under `## Tried Approaches` with the format:
  ```
  ### [NNN] strategy_name — YYYY-MM-DD
  - **Approach**: brief description
  - **Category**: trend-following / mean-reversion / momentum / volatility / composite
  - **Indicators**: comma-separated list
  - **Parameters**: key=value pairs
  - **Results**:
    - SPY: sharpe=X.XX, return=XX.X%, cagr=XX.X%, mdd=XX.X%, win_rate=XX.X%, pf=X.XX, trades=N
    - QQQ: ...
    - BTC: ...
  - **Analysis**: 2-3 sentences analyzing why it worked or didn't, compared to best result
  - **Status**: done
  ```
- Update `## Best Results` table — re-sort by Sharpe(SPY) descending
- Update `## Next Steps` — based on what you learned, suggest 3-4 NEW directions for the next cycle. NEVER repeat a direction that has already been tried.

## Rules
- NEVER copy an existing strategy with minor parameter changes
- Your strategy must use at least one indicator NOT used in any previous approach, OR combine indicators in a genuinely new way
- If backtest results are poor, still record them honestly and analyze WHY
- Keep the journal entries concise but informative
PROMPT
)" --dangerously-skip-permissions --model sonnet
