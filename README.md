# Auto Alpha Miner

AI가 퀀트 트레이딩 전략을 자동으로 개발하고 백테스트하는 시스템.
Claude Code가 전략을 설계 → 코드 작성 → 백테스트 → 평가 → 다음 연구 방향 결정을 반복합니다.

## 1. 환경 설정

### Docker 실행 (권장)

필요한 것: **Docker** + Claude 인증 (자동 연구 루프 사용 시)

```bash
git clone <repo-url> && cd auto_miner

# 빌드
docker compose build
```

**Claude 인증** — 자동 연구 루프(`./scripts/research_cycle.sh`)를 사용하려면 둘 중 하나를 선택하세요:

| 방법 | 대상 | 설정 |
|------|------|------|
| **API 키** | [API 크레딧](https://console.anthropic.com/) 사용자 | `echo "ANTHROPIC_API_KEY=sk-ant-..." > .env` |
| **Max 구독** | [Claude Max](https://claude.ai/) 구독자 | 호스트에서 `claude login` (자동으로 컨테이너에 공유됨) |

```bash
# 컨테이너 진입
docker compose run --rm app bash

# 컨테이너 내부 초기 설정
uv sync --group dev
```

> 백테스트만 사용할 경우(`uv run auto-miner run ...`) Claude 인증은 필요 없습니다.

### 로컬 실행

필요한 것: **Python 3.12+**, [uv](https://docs.astral.sh/uv/)

```bash
git clone <repo-url> && cd auto_miner
uv sync
```

자동 연구 루프를 사용하려면 [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code)가 추가로 필요합니다. API 키(`export ANTHROPIC_API_KEY=sk-ant-...`) 또는 `claude login`으로 인증하세요.

## 2. 사용법

### 자동 연구 루프 (핵심 기능)

Claude Code가 전략을 자동 개발하고 평가합니다.

```bash
# 1) 연구 저널 초기화 (최초 1회)
uv run auto-miner research-init

# 2) 연구 사이클 실행 (매번 새로운 전략을 개발)
./scripts/research_cycle.sh
```

한 사이클에서 일어나는 일:
1. `research/journal.md`에서 기존 연구 결과와 다음 방향 확인
2. Claude Code가 새로운 전략 코드를 작성하고 검증
3. SPY, QQQ, BTC에 대해 백테스트 실행
4. 결과를 분석하고 journal에 기록, 다음 연구 방향 업데이트

반복 실행할수록 전략이 누적되고, 이전 결과를 바탕으로 점점 더 나은 전략을 탐색합니다.

```bash
# 현재 연구 진행 상황 확인
uv run auto-miner research-status
```

### 수동 백테스트

특정 전략을 직접 실행할 수도 있습니다.

```bash
# 단일 종목 백테스트
uv run auto-miner run --symbol SPY --strategy turtle
uv run auto-miner run --symbol BTC --strategy rsi --plot          # 차트 포함
uv run auto-miner run --symbol AAPL --strategy ma_cross --save-chart result.png

# 한 종목에 모든 전략 비교
uv run auto-miner run-all --symbol SP500

# 여러 종목 포트폴리오 백테스트
uv run auto-miner run-portfolio --universe crypto --strategy rsi
uv run auto-miner run-portfolio --universe global --strategy turtle --rebalance M
```

### 목록 확인

```bash
uv run auto-miner list-strategies    # 사용 가능한 전략
uv run auto-miner list-symbols       # 심볼 별칭
uv run auto-miner list-universes     # 포트폴리오 유니버스
```

## 3. 옵션 설정

### 심볼 & 유니버스 (`config.yaml`)

프로젝트 루트의 `config.yaml`에서 종목과 유니버스를 관리합니다.

```yaml
symbols:
  NASDAQ: "^IXIC"
  SP500: "^GSPC"
  BTC: "BTC-USD"
  SAMSUNG: "005930.KS"
  # yfinance 티커 자유롭게 추가

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

#### 기본 제공 유니버스

| 유니버스 | 종목 |
|----------|------|
| `us_indices` | NASDAQ, SP500, DOW |
| `us_etf` | SPY, QQQ, IWM, DIA, VTI |
| `asia` | KOSPI, NIKKEI, HANGSENG, SHANGHAI |
| `crypto` | BTC, ETH, SOL, XRP |
| `global` | SP500, KOSPI, NIKKEI, FTSE, DAX, BTC |

### 백테스트 옵션

| 옵션 | 기본값 | 설명 |
|------|--------|------|
| `--symbol` | SP500 | 종목 별칭 또는 yfinance 티커 |
| `--strategy` | turtle | 전략 이름 |
| `--start` | 2020-01-01 | 백테스트 시작일 |
| `--end` | 2024-12-31 | 백테스트 종료일 |
| `--capital` | 100000 | 초기 자본금 |
| `--plot` | false | matplotlib 차트 표시 |
| `--save-chart` | - | 차트 파일 저장 경로 |

### 포트폴리오 리밸런싱 주기

| 옵션 | 설명 |
|------|------|
| (미지정) | 고정 비중 — 초기 1/N 배분 후 변경 없음 |
| `--rebalance W` | 매주 마지막 거래일에 균등 재조정 |
| `--rebalance M` | 매월 마지막 거래일에 균등 재조정 |
| `--rebalance Q` | 매분기 마지막 거래일에 균등 재조정 |

### 연구 저널 설정 (`research/journal.md`)

`research-init`으로 생성되는 journal의 Configuration 섹션에서 벤치마크 심볼, 기간, 자본금을 수정할 수 있습니다.

```markdown
## Configuration
- **benchmark_symbols**: SPY, QQQ, BTC
- **start**: 2020-01-01
- **end**: 2024-12-31
- **capital**: 100000
```

### 평가 지표

| 지표 | 설명 |
|------|------|
| Total Return | 총 수익률 |
| CAGR | 연평균 복합 성장률 |
| Max Drawdown | 최대 낙폭 |
| Sharpe Ratio | 샤프 비율 (연율화) |
| Win Rate | 승률 |
| Profit Factor | 총이익 / 총손실 |
| Trade Count | 총 거래 수 |

## 4. 프로젝트 구조

```
auto_miner/
├── config.yaml                     # 심볼 매핑 + 유니버스 설정
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── scripts/
│   └── research_cycle.sh           # 자동 연구 루프 실행 스크립트
├── research/
│   └── journal.md                  # 연구 저널 (research-init으로 생성)
├── src/auto_alpha_miner/
│   ├── cli.py                      # CLI 진입점
│   ├── config.py                   # 설정 로드, 전략 레지스트리
│   ├── data/
│   │   ├── yfinance_collector.py   # OHLCV 데이터 수집 (yfinance)
│   │   └── cache.py                # parquet 캐시
│   ├── strategy/
│   │   ├── base.py                 # BaseStrategy 인터페이스
│   │   ├── turtle.py               # 터틀 트레이딩
│   │   ├── rsi_divergence.py       # RSI 과매도/과매수
│   │   ├── ma_cross.py             # 이동평균 크로스
│   │   └── research_NNN_*.py       # 자동 생성된 연구 전략들
│   ├── backtest/
│   │   ├── engine.py               # 백테스트 엔진
│   │   ├── portfolio.py            # 포지션/자본 추적
│   │   ├── allocator.py            # 자본 배분 (Equal Weight)
│   │   └── multi_engine.py         # 멀티 심볼 포트폴리오
│   ├── evaluation/
│   │   ├── metrics.py              # Sharpe, MDD, CAGR 등
│   │   └── report.py              # 텍스트/차트 리포트
│   └── research/
│       ├── journal.py              # 저널 파싱/관리
│       ├── validator.py            # 전략 파일 검증
│       └── runner.py               # 벤치마크 백테스트 실행
└── tests/                          # 67개 테스트
```
