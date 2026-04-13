# Research Journal

## Configuration
- **benchmark_symbols**: SP500, KOSPI, NIKKEI, FTSE, DAX, BTC
- **start**: 2010-01-01
- **end**: 2024-12-31
- **capital**: 100000

## Research Directions
- 모멘텀 기반 전략 (ADX, MACD, Aroon 등 트렌드 지표 활용)
- 평균회귀 전략 (볼린저 밴드, RSI, CCI 등 오실레이터 활용)
- 브레이크아웃 전략 (도치안 채널, ATR 기반 변동성 돌파)
- 복합 지표 전략 (트렌드 + 모멘텀 + 거래량 조합)
- 멀티 타임프레임 시그널 확인

## Tried Approaches

### [001] baseline_ma_cross — 2026-04-12
- **Approach**: Baseline: Golden cross (buy) / Death cross (sell) using SMA.
- **Category**: trend-following
- **Indicators**: SMA
- **Parameters**: fast=50, slow=200
- **Results**:
  - SP500: sharpe=0.64, return=210.7%, cagr=8.3%, mdd=33.9%, win_rate=57.1%, pf=10.22, trades=7
  - KOSPI: sharpe=-0.11, return=-22.0%, cagr=-1.7%, mdd=46.7%, win_rate=26.7%, pf=0.65, trades=15
  - NIKKEI: sharpe=0.44, return=128.4%, cagr=6.0%, mdd=36.7%, win_rate=53.8%, pf=2.57, trades=13
  - FTSE: sharpe=0.03, return=-3.3%, cagr=-0.2%, mdd=36.8%, win_rate=50.0%, pf=0.93, trades=10
  - DAX: sharpe=0.33, return=66.2%, cagr=3.6%, mdd=44.9%, win_rate=75.0%, pf=2.23, trades=8
  - BTC: sharpe=1.01, return=19319.4%, cagr=71.7%, mdd=69.2%, win_rate=66.7%, pf=11.50, trades=9
- **Analysis**: Baseline strategy for comparison.
- **Status**: baseline

### [002] baseline_turtle — 2026-04-12
- **Approach**: Baseline: Donchian channel breakout (20-period).
- **Category**: trend-following
- **Indicators**: Donchian
- **Parameters**: entry_period=20, exit_period=10
- **Results**:
  - SP500: sharpe=0.75, return=158.1%, cagr=6.6%, mdd=9.6%, win_rate=53.7%, pf=3.13, trades=67
  - KOSPI: sharpe=0.38, return=51.1%, cagr=2.8%, mdd=15.5%, win_rate=48.4%, pf=1.69, trades=62
  - NIKKEI: sharpe=0.33, return=55.6%, cagr=3.0%, mdd=26.0%, win_rate=44.4%, pf=1.35, trades=72
  - FTSE: sharpe=-0.30, return=-32.8%, cagr=-2.6%, mdd=38.2%, win_rate=37.1%, pf=0.56, trades=70
  - DAX: sharpe=0.15, return=17.1%, cagr=1.1%, mdd=24.0%, win_rate=45.1%, pf=1.13, trades=71
  - BTC: sharpe=1.13, return=17985.4%, cagr=66.1%, mdd=55.9%, win_rate=50.0%, pf=2.68, trades=54
- **Analysis**: Baseline strategy for comparison.
- **Status**: baseline

### [003] baseline_rsi — 2026-04-12
- **Approach**: Baseline: Buy on RSI oversold bounce, sell on overbought reversal.
- **Category**: mean-reversion
- **Indicators**: RSI
- **Parameters**: period=14, oversold=30, overbought=70
- **Results**:
  - SP500: sharpe=0.56, return=169.7%, cagr=6.8%, mdd=28.5%, win_rate=86.7%, pf=17.46, trades=15
  - KOSPI: sharpe=0.35, return=73.6%, cagr=3.7%, mdd=38.4%, win_rate=76.5%, pf=2.08, trades=17
  - NIKKEI: sharpe=0.61, return=225.0%, cagr=8.2%, mdd=25.3%, win_rate=93.3%, pf=173.30, trades=15
  - FTSE: sharpe=0.30, return=58.7%, cagr=3.1%, mdd=27.3%, win_rate=91.7%, pf=5.81, trades=12
  - DAX: sharpe=0.80, return=363.3%, cagr=10.8%, mdd=26.4%, win_rate=88.2%, pf=12.95, trades=17
  - BTC: sharpe=0.47, return=366.7%, cagr=16.1%, mdd=67.4%, win_rate=72.2%, pf=2.36, trades=18
- **Analysis**: Baseline strategy for comparison.
- **Status**: baseline

### [005] research_005_supertrend — 2026-04-12
- **Approach**: ATR-based Supertrend indicator as a single clean signal source — buy when direction flips bullish (−1→+1), sell when it flips bearish (+1→−1).
- **Category**: trend-following
- **Indicators**: Supertrend (ATR)
- **Parameters**: atr_period=10, multiplier=3.0
- **Results**:
  - SP500: sharpe=0.48, return=93.3%, cagr=4.5%, mdd=19.8%, win_rate=51.5%, pf=1.63, trades=66
  - KOSPI: sharpe=0.02, return=-4.7%, cagr=-0.3%, mdd=35.3%, win_rate=43.3%, pf=0.96, trades=67
  - NIKKEI: sharpe=0.25, return=40.1%, cagr=2.3%, mdd=27.6%, win_rate=39.2%, pf=1.21, trades=79
  - FTSE: sharpe=-0.24, return=-32.6%, cagr=-2.6%, mdd=41.0%, win_rate=31.9%, pf=0.67, trades=69
  - DAX: sharpe=0.37, return=74.9%, cagr=3.8%, mdd=24.3%, win_rate=52.2%, pf=1.51, trades=67
  - BTC: sharpe=0.99, return=9092.3%, cagr=55.3%, mdd=53.6%, win_rate=49.1%, pf=2.12, trades=53
- **Analysis**: Supertrend generates similar trade frequency to Turtle (~66 trades) but achieves a lower Sharpe (0.48 vs 0.75) with nearly double the MDD (19.8% vs 9.6%). FTSE continues to underperform trend-following approaches, suggesting range-bound character. BTC remains the strongest asset for trend strategies. The ATR multiplier of 3.0 may be too loose — it lets drawdowns accumulate before flipping direction, whereas Turtle's channel exit is more responsive to price reversal.
- **Status**: done

### [006] research_006_aroon_roc_momentum — 2026-04-13
- **Approach**: Aroon Up/Down crossover (trend direction change) confirmed by positive ROC (price momentum). Enter long when Aroon Up crosses above Aroon Down AND ROC > 0. Exit when Aroon Down crosses above Aroon Up OR ROC turns negative.
- **Category**: momentum
- **Indicators**: Aroon, ROC
- **Parameters**: aroon_period=25, roc_period=20
- **Results**:
  - SP500: sharpe=0.52, return=70.7%, cagr=3.7%, mdd=19.7%, win_rate=50.0%, pf=2.23, trades=58
  - KOSPI: sharpe=0.59, return=91.6%, cagr=4.5%, mdd=13.9%, win_rate=47.5%, pf=2.42, trades=61
  - NIKKEI: sharpe=0.26, return=34.8%, cagr=2.0%, mdd=22.6%, win_rate=30.0%, pf=1.28, trades=70
  - FTSE: sharpe=-0.06, return=-9.3%, cagr=-0.7%, mdd=19.5%, win_rate=36.2%, pf=0.87, trades=69
  - DAX: sharpe=0.14, return=14.5%, cagr=0.9%, mdd=31.7%, win_rate=35.4%, pf=1.15, trades=65
  - BTC: sharpe=1.28, return=22722.0%, cagr=70.1%, mdd=39.3%, win_rate=49.1%, pf=3.38, trades=57
- **Analysis**: BTC Sharpe of 1.28 is the best single-asset result so far, beating turtle (1.13) — Aroon captures BTC's strong directional runs well. SP500 Sharpe (0.52) remains below the turtle baseline (0.75); the ROC < 0 exit fires too aggressively during normal pullbacks, cutting winners short and producing low win rates on choppy indices like NIKKEI (30%) and DAX (35%). KOSPI MDD of only 13.9% is notable, suggesting Aroon crossovers are effective at catching KOSPI regime changes. FTSE continues to resist all trend approaches tested.
- **Status**: done

### [007] research_007_macd_obv_volume — 2026-04-13
- **Approach**: MACD histogram sign-change as momentum flip signal, gated by OBV above its own EMA (volume confirms buyer participation). Enter long when MACD histogram crosses from negative to positive AND OBV > OBV_EMA(20). Exit when histogram flips negative OR OBV drops below its EMA.
- **Category**: momentum
- **Indicators**: MACD histogram, OBV, EMA(OBV)
- **Parameters**: macd_fast=12, macd_slow=26, macd_signal=9, obv_ema_period=20
- **Results**:
  - SP500: sharpe=0.70, return=84.4%, cagr=4.2%, mdd=13.2%, win_rate=50.4%, pf=2.00, trades=131
  - KOSPI: sharpe=0.14, return=10.3%, cagr=0.7%, mdd=17.9%, win_rate=37.0%, pf=1.15, trades=92
  - NIKKEI: sharpe=0.40, return=50.6%, cagr=2.8%, mdd=15.3%, win_rate=33.3%, pf=1.46, trades=108
  - FTSE: sharpe=-0.19, return=-16.8%, cagr=-1.2%, mdd=25.8%, win_rate=29.2%, pf=0.78, trades=106
  - DAX: sharpe=0.21, return=18.8%, cagr=1.2%, mdd=16.7%, win_rate=30.6%, pf=1.19, trades=108
  - BTC: sharpe=0.90, return=1935.3%, cagr=34.4%, mdd=47.6%, win_rate=37.5%, pf=2.23, trades=80
- **Analysis**: SP500 Sharpe of 0.70 is the best among all research strategies (004–007), closing in on the turtle baseline (0.75) while keeping MDD at 13.2% — much lower than MA-cross (33.9%) and RSI (28.5%). The OBV gate successfully filters many false MACD histogram flips, as evidenced by profit factor of 2.0 despite only 50% win rate. DAX and NIKKEI win rates are low (~30–33%), suggesting the OBV filter is too lenient for choppy markets — a tighter OBV slope confirmation (e.g. OBV > EMA AND OBV slope rising) might help. FTSE continues to underperform across all strategies. BTC Sharpe (0.90) is strong with only 80 trades, showing the MACD+OBV combo captures BTC's explosive runs well.
- **Status**: done

### [004] research_004_adx_ema_trend — 2026-04-12
- **Approach**: EMA(20/50) crossover gated by ADX(14) — only enter on bullish cross when ADX ≥ 25 (strong trend), exit on bearish cross or ADX < 20.
- **Category**: trend-following
- **Indicators**: EMA, ADX
- **Parameters**: fast=20, slow=50, adx_period=14, adx_entry=25, adx_exit=20
- **Results**:
  - SP500: sharpe=0.46, return=12.3%, cagr=0.8%, mdd=4.1%, win_rate=100.0%, pf=inf, trades=4
  - KOSPI: sharpe=0.00, return=-0.3%, cagr=0.0%, mdd=8.8%, win_rate=25.0%, pf=0.91, trades=4
  - NIKKEI: sharpe=-0.05, return=-2.3%, cagr=-0.2%, mdd=7.7%, win_rate=50.0%, pf=0.50, trades=4
  - FTSE: sharpe=-0.20, return=-3.0%, cagr=-0.2%, mdd=5.9%, win_rate=50.0%, pf=0.37, trades=4
  - DAX: sharpe=0.58, return=15.9%, cagr=1.0%, mdd=4.1%, win_rate=100.0%, pf=inf, trades=1
  - BTC: sharpe=0.19, return=31.5%, cagr=2.7%, mdd=48.3%, win_rate=41.7%, pf=1.29, trades=12
- **Analysis**: The ADX ≥ 25 gate was far too restrictive — only 1–4 trades over 14 years means the strategy sat in cash for the vast majority of the period, missing the bulk of equity gains. Win rate is artificially high (100% SP500) due to tiny sample size. The EMA(20/50) cross itself fires too rarely under strict ADX gating; the filter needs to be relaxed or replaced with a continuous trend-strength weighting. Sharpe of 0.46 is well below the turtle baseline of 0.75.
- **Status**: done

## Next Steps
- **Bollinger Band + OBV mean-reversion**: Enter long on BB lower-band touch when OBV is rising (buyers stepping in), exit at BB midline. Pure mean-reversion using volume confirmation — complements the trend-following strategies already tested.
- **MACD + OBV with tighter OBV slope filter**: Extend [007] by requiring OBV slope to be rising (e.g., OBV > EMA AND current OBV > previous OBV) rather than just OBV > EMA — addresses the low win rates on DAX/NIKKEI caused by the current lenient OBV gate.
- **CCI breakout**: CCI crossing above +100 as trend breakout entry (exit when CCI falls below 0) — uses oscillator as trend filter rather than mean-reversion, a different framing than RSI baseline. Unused indicator.
- **MFI + Donchian hybrid**: Money Flow Index (unused) as entry quality filter on top of Donchian channel breakout — buy Donchian breakout only when MFI > 50 (net buying pressure), aiming to improve turtle Sharpe by skipping low-conviction breakouts.

## Best Results
| Rank | Strategy | Sharpe(SP500) | Return(SP500) | MDD(SP500) |
|------|----------|--------------|--------------|-----------|
| 1 | baseline_turtle | 0.75 | 158.1% | 9.6% |
| 2 | research_007_macd_obv_volume | 0.70 | 84.4% | 13.2% |
| 3 | baseline_ma_cross | 0.64 | 210.7% | 33.9% |
| 4 | baseline_rsi | 0.56 | 169.7% | 28.5% |
| 5 | research_006_aroon_roc_momentum | 0.52 | 70.7% | 19.7% |
| 6 | research_005_supertrend | 0.48 | 93.3% | 19.8% |
| 7 | research_004_adx_ema_trend | 0.46 | 12.3% | 4.1% |
