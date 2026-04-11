# Auto Alpha Miner

퀀트 전략 백테스팅 시스템. 데이터 수집 → 전략 실행 → 평가/리포트 파이프라인.

## 프로젝트 구조

```
src/auto_alpha_miner/
├── config.py                # YAML config 로드, 전략 레지스트리
├── cli.py                   # CLI 진입점 (typer)
├── __main__.py              # python -m 지원
├── data/
│   ├── base.py              # BaseDataCollector ABC
│   ├── yfinance_collector.py # yfinance OHLCV 수집
│   └── cache.py             # parquet 캐시
├── strategy/
│   ├── base.py              # BaseStrategy ABC, Signal
│   ├── turtle.py            # 터틀 트레이딩 (도치안 채널 돌파)
│   ├── rsi_divergence.py    # RSI 과매도/과매수 반전
│   └── ma_cross.py          # 이동평균 골든/데드 크로스
├── backtest/
│   ├── trade.py             # Trade 데이터클래스
│   ├── portfolio.py         # 포지션/자본 추적
│   ├── engine.py            # BacktestEngine, BacktestResult
│   ├── allocator.py         # 자본 배분 (Equal Weight)
│   └── multi_engine.py      # 멀티 심볼 포트폴리오 백테스트
└── evaluation/
    ├── metrics.py           # Sharpe, MDD, CAGR, 승률, Profit Factor
    └── report.py            # 텍스트 리포트 + matplotlib 차트

config.yaml                  # 심볼 매핑 + 포트폴리오 유니버스 설정
```

## 설치

```bash
uv sync
```

## 사용법

### 단일 심볼 백테스트

```bash
auto-miner run --symbol SPY --strategy turtle --start 2020-01-01 --end 2024-12-31
auto-miner run --symbol BTC --strategy rsi --plot              # 차트 포함
auto-miner run --symbol NASDAQ --strategy ma_cross --save-chart result.png  # 차트 저장
```

### 모든 전략 비교

```bash
auto-miner run-all --symbol SP500 --start 2020-01-01 --end 2024-12-31
```

### 멀티 심볼 포트폴리오 백테스트

여러 종목에 전략을 동시 실행합니다. Equal Weight(균등 배분)로 자본을 배분하며, 리밸런싱 주기를 설정할 수 있습니다.

```bash
# 고정 균등 배분
auto-miner run-portfolio --universe crypto --strategy rsi

# 월간 리밸런싱 — 매월 균등 비중 재조정 (드리프트 보정)
auto-miner run-portfolio --universe crypto --strategy rsi --rebalance M

# 주간/분기별 리밸런싱
auto-miner run-portfolio --universe us_etf --strategy turtle --rebalance W
auto-miner run-portfolio --universe global --strategy ma_cross --rebalance Q

# 차트 포함
auto-miner run-portfolio --universe us_etf --strategy ma_cross --rebalance M --plot
```

#### 리밸런싱 주기

| 옵션 | 설명 |
|------|------|
| (미지정) | 고정 비중 — 초기 1/N 배분 후 변경 없음 |
| `W` | 매주 마지막 거래일에 1/N으로 재조정 |
| `M` | 매월 마지막 거래일에 1/N으로 재조정 |
| `Q` | 매분기 마지막 거래일에 1/N으로 재조정 |

리밸런싱은 시간이 지남에 따라 종목별 성과 차이로 발생하는 비중 드리프트를 보정합니다.

### 목록 확인

```bash
auto-miner list-strategies    # 전략 목록
auto-miner list-symbols       # 심볼 별칭 목록
auto-miner list-universes     # 포트폴리오 유니버스 목록
```

## 심볼 설정 (config.yaml)

심볼과 유니버스는 프로젝트 루트의 `config.yaml`에서 관리합니다:

```yaml
symbols:
  NASDAQ: "^IXIC"
  SP500: "^GSPC"
  BTC: "BTC-USD"
  SAMSUNG: "005930.KS"
  # ... yfinance 티커 자유롭게 추가

universes:
  crypto:
    - BTC
    - ETH
    - SOL
    - XRP
  global:
    - SP500
    - KOSPI
    - NIKKEI
    - FTSE
    - DAX
    - BTC
```

`config.yaml`에 없는 티커도 직접 사용 가능합니다: `--symbol AAPL`, `--symbol 005930.KS`

### 기본 제공 유니버스

| 유니버스 | 종목 |
|----------|------|
| `us_indices` | NASDAQ, SP500, DOW |
| `us_etf` | SPY, QQQ, IWM, DIA, VTI |
| `asia` | KOSPI, NIKKEI, HANGSENG, SHANGHAI |
| `crypto` | BTC, ETH, SOL, XRP |
| `global` | SP500, KOSPI, NIKKEI, FTSE, DAX, BTC |

## 전략 추가하기

`BaseStrategy`를 상속하고 `@register_strategy` 데코레이터를 붙이면 됩니다:

```python
from auto_alpha_miner.config import register_strategy
from auto_alpha_miner.strategy.base import BaseStrategy, Signal

@register_strategy
class MyStrategy(BaseStrategy):
    name = "my_strategy"

    def prepare(self, df):
        # 보조지표 추가
        df["indicator"] = ...
        df.dropna(inplace=True)
        return df

    def generate_signals(self, df):
        signals = []
        # 시그널 로직
        return signals
```

`strategy/` 디렉토리에 파일을 넣기만 하면 CLI에서 자동 인식됩니다. `cli.py` 수정 불필요.

## 평가 지표

| 지표 | 설명 |
|------|------|
| Total Return | 총 수익률 |
| CAGR | 연평균 복합 성장률 |
| Max Drawdown | 최대 낙폭 |
| Sharpe Ratio | 샤프 비율 (연율화) |
| Win Rate | 승률 |
| Profit Factor | 총이익 / 총손실 |
| Trade Count | 총 거래 수 |

## 테스트

```bash
uv run pytest
```
