# Research Journal

## Configuration
- **benchmark_symbols**: SP500, NASDAQ, SPY, QQQ, KOSPI, NIKKEI, HANGSENG, FTSE, DAX, BTC, ETH, GOLD, OIL
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

### [001] adx_ema — 2026-04-16
- **Approach**: ADX trend strength + EMA crossover.
- **Category**: trend-following
- **Indicators**: ADX, EMA
- **Parameters**: adx_period=14, adx_threshold=25, fast_ema=12, slow_ema=26
- **Results**:
  - SP500: sharpe=-0.95, return=-2.6%, cagr=-0.2%, mdd=17.5%, win_rate=37.5%
  - NASDAQ: sharpe=-0.65, return=2.3%, cagr=0.2%, mdd=17.9%, win_rate=33.3%
  - SPY: sharpe=-0.48, return=19.4%, cagr=1.2%, mdd=9.9%, win_rate=42.9%
  - QQQ: sharpe=-0.24, return=23.3%, cagr=1.4%, mdd=15.8%, win_rate=50.0%
  - KOSPI: sharpe=-0.41, return=19.9%, cagr=1.2%, mdd=7.2%, win_rate=62.5%
  - NIKKEI: sharpe=-1.33, return=-10.1%, cagr=-0.7%, mdd=14.5%, win_rate=0.0%
  - HANGSENG: sharpe=-0.76, return=-9.9%, cagr=-0.7%, mdd=23.9%, win_rate=20.0%
  - FTSE: sharpe=-1.22, return=-11.1%, cagr=-0.8%, mdd=14.7%, win_rate=22.2%
  - DAX: sharpe=-0.99, return=1.1%, cagr=0.1%, mdd=7.5%, win_rate=66.7%
  - BTC: sharpe=-0.39, return=-33.1%, cagr=-3.9%, mdd=56.9%, win_rate=20.0%
  - ETH: sharpe=-0.03, return=-11.4%, cagr=-1.7%, mdd=58.4%, win_rate=25.0%
  - GOLD: sharpe=-0.59, return=3.2%, cagr=0.2%, mdd=16.0%, win_rate=42.9%
  - OIL: sharpe=-0.20, return=7.2%, cagr=0.5%, mdd=38.5%, win_rate=25.0%
- **Analysis**: AI-generated strategy.
- **Status**: tested

### [002] baseline_turtle — 2026-04-16
- **Approach**: Baseline: Donchian channel breakout (20-period).
- **Category**: trend-following
- **Indicators**: Donchian
- **Parameters**: entry_period=20, exit_period=10
- **Results**:
  - SP500: sharpe=0.30, return=120.0%, cagr=5.4%, mdd=11.5%, win_rate=53.7%
  - NASDAQ: sharpe=0.28, return=124.7%, cagr=5.6%, mdd=18.9%, win_rate=50.7%
  - SPY: sharpe=0.46, return=173.1%, cagr=7.0%, mdd=9.3%, win_rate=56.9%
  - QQQ: sharpe=0.36, return=157.3%, cagr=6.5%, mdd=19.1%, win_rate=51.5%
  - KOSPI: sharpe=-0.11, return=29.3%, cagr=1.7%, mdd=20.4%, win_rate=41.9%
  - NIKKEI: sharpe=-0.08, return=25.3%, cagr=1.5%, mdd=31.4%, win_rate=36.1%
  - HANGSENG: sharpe=-0.53, return=-40.4%, cagr=-3.4%, mdd=49.1%, win_rate=33.8%
  - FTSE: sharpe=-0.85, return=-45.4%, cagr=-4.0%, mdd=49.7%, win_rate=31.4%
  - DAX: sharpe=-0.26, return=-3.2%, cagr=-0.2%, mdd=35.0%, win_rate=39.4%
  - BTC: sharpe=1.02, return=15542.4%, cagr=63.8%, mdd=56.1%, win_rate=50.0%
  - ETH: sharpe=0.82, return=2175.7%, cagr=55.4%, mdd=49.0%, win_rate=55.9%
  - GOLD: sharpe=-0.08, return=28.5%, cagr=1.7%, mdd=22.3%, win_rate=39.3%
  - OIL: sharpe=0.10, return=55.3%, cagr=3.0%, mdd=40.5%, win_rate=46.4%
- **Analysis**: Baseline strategy.
- **Status**: baseline

### [003] baseline_ma_cross — 2026-04-16
- **Approach**: Baseline: Golden cross / Death cross using SMA.
- **Category**: trend-following
- **Indicators**: SMA
- **Parameters**: fast=50, slow=200
- **Results**:
  - SP500: sharpe=0.42, return=206.5%, cagr=8.2%, mdd=33.9%, win_rate=57.1%
  - NASDAQ: sharpe=0.62, return=442.8%, cagr=12.6%, mdd=30.1%, win_rate=87.5%
  - SPY: sharpe=0.52, return=265.1%, cagr=9.5%, mdd=33.7%, win_rate=66.7%
  - QQQ: sharpe=0.78, return=722.5%, cagr=16.0%, mdd=28.6%, win_rate=85.7%
  - KOSPI: sharpe=-0.35, return=-18.6%, cagr=-1.4%, mdd=47.4%, win_rate=33.3%
  - NIKKEI: sharpe=0.26, return=124.5%, cagr=5.9%, mdd=36.5%, win_rate=46.2%
  - HANGSENG: sharpe=-0.43, return=-36.9%, cagr=-3.2%, mdd=54.8%, win_rate=30.0%
  - FTSE: sharpe=-0.29, return=-6.0%, cagr=-0.4%, mdd=37.6%, win_rate=50.0%
  - DAX: sharpe=0.14, return=76.3%, cagr=4.1%, mdd=41.3%, win_rate=75.0%
  - BTC: sharpe=0.95, return=18769.1%, cagr=71.2%, mdd=69.3%, win_rate=66.7%
  - ETH: sharpe=0.64, return=758.7%, cagr=38.5%, mdd=78.1%, win_rate=57.1%
  - GOLD: sharpe=-0.13, return=16.7%, cagr=1.1%, mdd=27.4%, win_rate=33.3%
  - OIL: sharpe=-0.05, return=-13.4%, cagr=-1.0%, mdd=62.7%, win_rate=30.8%
- **Analysis**: Baseline strategy.
- **Status**: baseline

### [004] bollinger_vol — 2026-04-16
- **Approach**: Bollinger Band + volume mean-reversion.
- **Category**: mean-reversion
- **Indicators**: Bollinger Bands, Volume
- **Parameters**: bb_period=20, bb_std=2.0, vol_ma=20
- **Results**:
  - SP500: sharpe=0.50, return=300.6%, cagr=9.7%, mdd=29.0%, win_rate=89.5%
  - NASDAQ: sharpe=0.34, return=200.6%, cagr=7.7%, mdd=33.7%, win_rate=76.7%
  - SPY: sharpe=0.50, return=294.9%, cagr=9.6%, mdd=28.9%, win_rate=89.5%
  - QQQ: sharpe=0.54, return=395.6%, cagr=11.3%, mdd=35.6%, win_rate=82.9%
  - KOSPI: sharpe=-0.10, return=11.4%, cagr=0.7%, mdd=36.8%, win_rate=55.6%
  - NIKKEI: sharpe=0.29, return=154.0%, cagr=6.4%, mdd=30.7%, win_rate=75.0%
  - HANGSENG: sharpe=-0.20, return=-20.3%, cagr=-1.5%, mdd=47.1%, win_rate=61.3%
  - FTSE: sharpe=0.12, return=72.1%, cagr=3.7%, mdd=34.2%, win_rate=79.4%
  - DAX: sharpe=0.24, return=132.5%, cagr=5.8%, mdd=38.8%, win_rate=71.1%
  - BTC: sharpe=0.14, return=8.0%, cagr=0.8%, mdd=82.3%, win_rate=59.4%
  - ETH: sharpe=-0.12, return=-74.3%, cagr=-17.4%, mdd=87.8%, win_rate=57.9%
  - GOLD: sharpe=-0.05, return=46.2%, cagr=2.6%, mdd=12.3%, win_rate=76.5%
  - OIL: sharpe=-0.25, return=-11.7%, cagr=-0.8%, mdd=143.2%, win_rate=64.9%
- **Analysis**: AI-generated strategy.
- **Status**: tested

### [005] macd_signal — 2026-04-16
- **Approach**: MACD histogram crossover with signal line.
- **Category**: trend-following
- **Indicators**: MACD
- **Parameters**: fast=12, slow=26, signal=9
- **Results**:
  - SP500: sharpe=-0.06, return=33.4%, cagr=2.0%, mdd=21.3%, win_rate=45.9%
  - NASDAQ: sharpe=0.09, return=63.8%, cagr=3.4%, mdd=25.1%, win_rate=46.8%
  - SPY: sharpe=0.03, return=52.5%, cagr=2.9%, mdd=18.3%, win_rate=45.8%
  - QQQ: sharpe=0.21, return=104.4%, cagr=4.9%, mdd=25.8%, win_rate=48.6%
  - KOSPI: sharpe=-0.05, return=32.8%, cagr=1.9%, mdd=23.6%, win_rate=40.6%
  - NIKKEI: sharpe=0.09, return=61.0%, cagr=3.3%, mdd=20.2%, win_rate=41.1%
  - HANGSENG: sharpe=-0.39, return=-37.9%, cagr=-3.2%, mdd=59.0%, win_rate=39.1%
  - FTSE: sharpe=-0.56, return=-34.4%, cagr=-2.8%, mdd=40.5%, win_rate=37.3%
  - DAX: sharpe=-0.16, return=4.0%, cagr=0.3%, mdd=46.8%, win_rate=40.8%
  - BTC: sharpe=1.13, return=34925.8%, cagr=77.6%, mdd=52.0%, win_rate=45.4%
  - ETH: sharpe=0.63, return=849.2%, cagr=37.6%, mdd=72.3%, win_rate=40.2%
  - GOLD: sharpe=-0.23, return=-3.6%, cagr=-0.2%, mdd=37.4%, win_rate=33.1%
  - OIL: sharpe=-0.36, return=-100.0%, cagr=-100.0%, mdd=221.0%, win_rate=49.5%
- **Analysis**: AI-generated strategy.
- **Status**: tested

### [006] baseline_rsi — 2026-04-16
- **Approach**: Baseline: RSI oversold/overbought mean reversion.
- **Category**: mean-reversion
- **Indicators**: RSI
- **Parameters**: period=14, oversold=30, overbought=70
- **Results**:
  - SP500: sharpe=0.31, return=155.9%, cagr=6.5%, mdd=28.5%, win_rate=86.7%
  - NASDAQ: sharpe=0.32, return=173.5%, cagr=6.9%, mdd=27.2%, win_rate=85.7%
  - SPY: sharpe=0.32, return=151.9%, cagr=6.4%, mdd=28.3%, win_rate=85.7%
  - QQQ: sharpe=0.36, return=196.2%, cagr=7.5%, mdd=29.6%, win_rate=93.8%
  - KOSPI: sharpe=0.13, return=76.8%, cagr=3.9%, mdd=37.7%, win_rate=76.5%
  - NIKKEI: sharpe=0.38, return=197.7%, cagr=7.5%, mdd=25.3%, win_rate=93.3%
  - HANGSENG: sharpe=-0.10, return=0.8%, cagr=0.1%, mdd=47.9%, win_rate=53.8%
  - FTSE: sharpe=0.05, return=53.1%, cagr=2.9%, mdd=27.5%, win_rate=91.7%
  - DAX: sharpe=0.60, return=373.1%, cagr=10.9%, mdd=26.4%, win_rate=88.2%
  - BTC: sharpe=0.37, return=341.1%, cagr=15.5%, mdd=67.8%, win_rate=72.2%
  - ETH: sharpe=0.32, return=125.9%, cagr=12.1%, mdd=76.8%, win_rate=81.8%
  - GOLD: sharpe=0.02, return=51.9%, cagr=2.8%, mdd=28.4%, win_rate=85.7%
  - OIL: sharpe=-0.20, return=74.1%, cagr=3.8%, mdd=158.6%, win_rate=71.4%
- **Analysis**: Baseline strategy.
- **Status**: baseline

### [007] cci_reversion — 2026-04-16
- **Approach**: Mean-reversion using CCI: buy when oversold, sell when overbought.
- **Category**: mean-reversion
- **Indicators**: CCI
- **Parameters**: period=20, oversold=-100, overbought=100
- **Results**:
  - SP500: sharpe=0.22, return=100.2%, cagr=4.8%, mdd=23.1%, win_rate=63.3%, pf=3.17, trades=30
  - NASDAQ: sharpe=-0.18, return=27.7%, cagr=1.7%, mdd=12.0%, win_rate=45.0%, pf=2.22, trades=40
  - SPY: sharpe=0.00, return=0.0%, cagr=0.0%, mdd=0.0%, win_rate=0.0%, pf=0.00, trades=0
  - QQQ: sharpe=0.00, return=0.0%, cagr=0.0%, mdd=0.0%, win_rate=0.0%, pf=0.00, trades=0
  - KOSPI: sharpe=-0.08, return=29.9%, cagr=1.8%, mdd=18.0%, win_rate=64.3%, pf=3.91, trades=14
  - NIKKEI: sharpe=-4.65, return=-1.7%, cagr=-0.1%, mdd=2.6%, win_rate=42.9%, pf=0.65, trades=7
  - HANGSENG: sharpe=0.00, return=0.0%, cagr=0.0%, mdd=0.0%, win_rate=0.0%, pf=0.00, trades=0
  - FTSE: sharpe=-1.59, return=-22.8%, cagr=-1.7%, mdd=22.8%, win_rate=38.4%, pf=0.65, trades=99
  - DAX: sharpe=-1.86, return=-6.6%, cagr=-0.5%, mdd=9.6%, win_rate=48.8%, pf=0.82, trades=43
  - BTC: sharpe=0.30, return=115.4%, cagr=7.8%, mdd=10.9%, win_rate=54.5%, pf=6.97, trades=11
  - ETH: sharpe=0.37, return=145.0%, cagr=13.5%, mdd=43.1%, win_rate=38.5%, pf=2.80, trades=26
  - GOLD: sharpe=-0.18, return=42.5%, cagr=2.4%, mdd=4.6%, win_rate=100.0%, pf=inf, trades=5
  - OIL: sharpe=0.00, return=0.0%, cagr=0.0%, mdd=0.0%, win_rate=0.0%, pf=0.00, trades=0
- **Analysis**: AI-generated strategy from automated research cycle.
- **Status**: tested

### [008] aroon_trend — 2026-04-16
- **Approach**: Trend-following using Aroon indicator crossover.
- **Category**: trend-following
- **Indicators**: Aroon
- **Parameters**: period=25, threshold=70
- **Results**:
  - SP500: sharpe=0.16, return=89.8%, cagr=4.4%, mdd=33.9%, win_rate=80.4%, pf=2.15, trades=56
  - NASDAQ: sharpe=0.26, return=136.3%, cagr=5.9%, mdd=25.9%, win_rate=72.7%, pf=2.39, trades=55
  - SPY: sharpe=0.24, return=119.0%, cagr=5.4%, mdd=28.7%, win_rate=80.7%, pf=2.80, trades=57
  - QQQ: sharpe=0.18, return=99.6%, cagr=4.7%, mdd=26.8%, win_rate=75.9%, pf=2.06, trades=54
  - KOSPI: sharpe=-0.24, return=-15.4%, cagr=-1.1%, mdd=35.8%, win_rate=66.7%, pf=0.91, trades=57
  - NIKKEI: sharpe=0.20, return=103.0%, cagr=4.9%, mdd=30.7%, win_rate=71.4%, pf=2.13, trades=63
  - HANGSENG: sharpe=-0.06, return=13.5%, cagr=0.9%, mdd=35.5%, win_rate=65.5%, pf=1.14, trades=58
  - FTSE: sharpe=0.05, return=52.1%, cagr=2.9%, mdd=34.8%, win_rate=74.6%, pf=1.56, trades=63
  - DAX: sharpe=0.12, return=73.1%, cagr=3.7%, mdd=37.7%, win_rate=71.4%, pf=1.87, trades=63
  - BTC: sharpe=0.18, return=51.2%, cagr=4.1%, mdd=83.0%, win_rate=60.0%, pf=1.10, trades=50
  - ETH: sharpe=-0.17, return=-84.3%, cagr=-23.0%, mdd=94.7%, win_rate=59.0%, pf=0.30, trades=39
  - GOLD: sharpe=-0.10, return=21.5%, cagr=1.3%, mdd=35.7%, win_rate=67.2%, pf=1.38, trades=58
  - OIL: sharpe=-0.28, return=-38.6%, cagr=-3.2%, mdd=127.0%, win_rate=67.3%, pf=0.88, trades=55
- **Analysis**: AI-generated strategy from automated research cycle.
- **Status**: tested

### [009] atr_breakout — 2026-04-16
- **Approach**: Volatility breakout: buy when price breaks above SMA + ATR multiplier.
- **Category**: breakout
- **Indicators**: ATR, SMA
- **Parameters**: sma_period=20, atr_period=14, multiplier=1.5
- **Results**:
  - SP500: sharpe=-0.07, return=37.5%, cagr=2.2%, mdd=17.0%, win_rate=50.0%, pf=1.55, trades=92
  - NASDAQ: sharpe=0.17, return=85.9%, cagr=4.2%, mdd=20.9%, win_rate=46.8%, pf=1.83, trades=94
  - SPY: sharpe=0.15, return=78.7%, cagr=4.0%, mdd=16.3%, win_rate=50.0%, pf=1.97, trades=92
  - QQQ: sharpe=0.16, return=84.2%, cagr=4.2%, mdd=22.0%, win_rate=49.5%, pf=1.67, trades=95
  - KOSPI: sharpe=-0.01, return=46.2%, cagr=2.6%, mdd=13.4%, win_rate=40.3%, pf=1.69, trades=77
  - NIKKEI: sharpe=-0.15, return=12.1%, cagr=0.8%, mdd=25.0%, win_rate=35.1%, pf=1.16, trades=94
  - HANGSENG: sharpe=-0.28, return=-7.7%, cagr=-0.5%, mdd=33.7%, win_rate=38.3%, pf=1.00, trades=81
  - FTSE: sharpe=-0.95, return=-44.5%, cagr=-3.9%, mdd=49.2%, win_rate=34.8%, pf=0.55, trades=92
  - DAX: sharpe=-0.12, return=23.3%, cagr=1.4%, mdd=24.6%, win_rate=46.1%, pf=1.29, trades=89
  - BTC: sharpe=1.09, return=18310.4%, cagr=66.4%, mdd=53.2%, win_rate=50.7%, pf=2.09, trades=75
  - ETH: sharpe=0.88, return=2543.6%, cagr=58.7%, mdd=41.6%, win_rate=56.0%, pf=2.29, trades=50
  - GOLD: sharpe=-0.22, return=6.1%, cagr=0.4%, mdd=27.8%, win_rate=31.5%, pf=1.12, trades=92
  - OIL: sharpe=0.22, return=121.7%, cagr=5.5%, mdd=38.2%, win_rate=45.6%, pf=1.75, trades=68
- **Analysis**: AI-generated strategy from automated research cycle.
- **Status**: tested

### [010] combined_trend — 2026-04-16
- **Approach**: Multi-indicator: EMA trend + RSI momentum + Volume confirmation.
- **Category**: trend-following
- **Indicators**: EMA, RSI, Volume
- **Parameters**: ema_fast=21, ema_slow=55, rsi_period=14
- **Results**:
  - SP500: sharpe=-0.28, return=21.0%, cagr=1.3%, mdd=16.3%, win_rate=44.4%, pf=2.25, trades=9
  - NASDAQ: sharpe=0.04, return=56.1%, cagr=3.1%, mdd=17.9%, win_rate=41.2%, pf=2.63, trades=17
  - SPY: sharpe=-0.02, return=50.1%, cagr=2.8%, mdd=10.4%, win_rate=57.1%, pf=6.29, trades=7
  - QQQ: sharpe=-0.18, return=33.2%, cagr=2.0%, mdd=12.1%, win_rate=66.7%, pf=4.06, trades=6
  - KOSPI: sharpe=-0.67, return=-14.1%, cagr=-1.0%, mdd=30.8%, win_rate=17.6%, pf=0.70, trades=17
  - NIKKEI: sharpe=-0.01, return=44.7%, cagr=2.5%, mdd=22.0%, win_rate=33.3%, pf=2.06, trades=18
  - HANGSENG: sharpe=-0.39, return=-10.4%, cagr=-0.7%, mdd=27.9%, win_rate=38.1%, pf=0.82, trades=21
  - FTSE: sharpe=-0.94, return=-16.1%, cagr=-1.2%, mdd=23.2%, win_rate=29.4%, pf=0.41, trades=17
  - DAX: sharpe=-0.43, return=0.8%, cagr=0.1%, mdd=29.0%, win_rate=36.4%, pf=1.06, trades=11
  - BTC: sharpe=0.65, return=1093.9%, cagr=27.7%, mdd=46.2%, win_rate=56.2%, pf=3.53, trades=16
  - ETH: sharpe=0.54, return=406.2%, cagr=26.1%, mdd=54.0%, win_rate=53.8%, pf=2.33, trades=13
  - GOLD: sharpe=-0.45, return=6.5%, cagr=0.4%, mdd=13.2%, win_rate=33.3%, pf=1.64, trades=6
  - OIL: sharpe=-0.06, return=12.4%, cagr=0.8%, mdd=41.4%, win_rate=36.8%, pf=1.26, trades=19
- **Analysis**: AI-generated strategy from automated research cycle.
- **Status**: tested

### [011] stochastic — 2026-04-16
- **Approach**: Stochastic %K/%D crossover in oversold/overbought zones.
- **Category**: mean-reversion
- **Indicators**: Stochastic
- **Parameters**: k_period=14, d_period=3, oversold=20, overbought=80
- **Results**:
  - SP500: sharpe=0.13, return=77.0%, cagr=3.9%, mdd=28.5%, win_rate=81.1%, pf=2.90, trades=37
  - NASDAQ: sharpe=0.33, return=167.3%, cagr=6.8%, mdd=23.9%, win_rate=85.7%, pf=3.17, trades=42
  - SPY: sharpe=0.23, return=108.6%, cagr=5.0%, mdd=28.3%, win_rate=86.5%, pf=3.56, trades=37
  - QQQ: sharpe=0.40, return=207.3%, cagr=7.8%, mdd=22.6%, win_rate=85.4%, pf=3.55, trades=41
  - KOSPI: sharpe=-0.12, return=12.7%, cagr=0.8%, mdd=30.1%, win_rate=60.0%, pf=1.29, trades=50
  - NIKKEI: sharpe=0.26, return=128.4%, cagr=5.7%, mdd=26.3%, win_rate=75.5%, pf=2.58, trades=49
  - HANGSENG: sharpe=-0.06, return=13.2%, cagr=0.8%, mdd=42.2%, win_rate=59.3%, pf=1.14, trades=54
  - FTSE: sharpe=0.61, return=294.7%, cagr=9.6%, mdd=33.7%, win_rate=84.7%, pf=4.06, trades=59
  - DAX: sharpe=0.20, return=105.0%, cagr=4.9%, mdd=30.6%, win_rate=77.1%, pf=2.22, trades=48
  - BTC: sharpe=0.07, return=-19.2%, cagr=-2.1%, mdd=84.7%, win_rate=68.3%, pf=0.96, trades=41
  - ETH: sharpe=0.00, return=-47.9%, cagr=-8.8%, mdd=86.2%, win_rate=63.0%, pf=0.59, trades=27
  - GOLD: sharpe=-0.12, return=19.0%, cagr=1.2%, mdd=25.3%, win_rate=62.7%, pf=1.31, trades=51
  - OIL: sharpe=-0.29, return=-50.3%, cagr=-4.6%, mdd=136.4%, win_rate=70.5%, pf=0.80, trades=44
- **Analysis**: AI-generated strategy from automated research cycle.
- **Status**: tested

## Next Steps
- 기존 3개 전략(turtle, rsi, ma_cross) baseline 결과 기록 완료
- 모멘텀 기반 전략 탐색: ADX + EMA 조합
- 평균회귀 전략 탐색: 볼린저 밴드 + 거래량 확인
- MACD 기반 시그널 전략 시도

## Best Results
| Rank | Strategy | Sharpe(SPY) | Return(SPY) | MDD(SPY) |
|------|----------|-------------|-------------|----------|
| 1 | baseline_ma_cross | 0.52 | 265.1% | 33.7% |
| 2 | bollinger_vol | 0.50 | 294.9% | 28.9% |
| 3 | baseline_turtle | 0.46 | 173.1% | 9.3% |
| 4 | baseline_rsi | 0.32 | 151.9% | 28.3% |
| 5 | aroon_trend | 0.24 | 119.0% | 28.7% |
| 6 | stochastic | 0.23 | 108.6% | 28.3% |
| 7 | atr_breakout | 0.15 | 78.7% | 16.3% |
| 8 | macd_signal | 0.03 | 52.5% | 18.3% |
| 9 | cci_reversion | 0.00 | 0.0% | 0.0% |
| 10 | combined_trend | -0.02 | 50.1% | 10.4% |
| 11 | adx_ema | -0.48 | 19.4% | 9.9% |
