/**
 * Internationalization (i18n) module for Auto Alpha Miner Dashboard.
 * Supports: English (en), Korean (ko)
 * Usage: Add data-i18n="key" to elements for text, data-i18n-placeholder="key" for placeholders.
 */

const TRANSLATIONS = {
  // === Sidebar / Nav ===
  "nav.brand": { en: "Alpha Miner", ko: "Alpha Miner" },
  "nav.overview": { en: "Lab Overview", ko: "Lab Overview" },
  "nav.backtest": { en: "Backtest", ko: "Backtest" },
  "nav.compare": { en: "Compare", ko: "Compare" },
  "nav.portfolio": { en: "Portfolio", ko: "Portfolio" },
  "nav.research": { en: "Research", ko: "Research" },
  "nav.footer.version": { en: "AI Alpha Lab v0.1", ko: "AI Alpha Lab v0.1" },
  "nav.footer.desc": { en: "Automated Strategy Discovery", ko: "자동화된 전략 발굴" },

  // === Overview Page ===
  "overview.title": { en: "AI Alpha Lab", ko: "AI Alpha Lab" },
  "overview.engine.title": { en: "AI Research Engine", ko: "AI 리서치 엔진" },
  "overview.engine.cycles": { en: "Cycles", ko: "사이클" },
  "overview.engine.discovered": { en: "Discovered", ko: "발굴" },
  "overview.engine.indicators": { en: "Indicators", ko: "지표" },
  "overview.engine.beatrate": { en: "Beat Rate", ko: "승률" },

  "overview.pipeline.hypothesis": { en: "Hypothesis", ko: "가설" },
  "overview.pipeline.directions": { en: "directions", ko: "방향" },
  "overview.pipeline.stratgen": { en: "Strategy Gen", ko: "전략 생성" },
  "overview.pipeline.indicators": { en: "indicators", ko: "지표" },
  "overview.pipeline.backtest": { en: "Backtest", ko: "백테스트" },
  "overview.pipeline.markets": { en: "markets", ko: "시장" },
  "overview.pipeline.evaluate": { en: "Evaluate", ko: "평가" },
  "overview.pipeline.tested": { en: "tested", ko: "테스트됨" },
  "overview.pipeline.select": { en: "Select", ko: "선별" },
  "overview.pipeline.alpha": { en: "alpha", ko: "알파" },

  "overview.hero.explored": { en: "Strategies Explored", ko: "탐색한 전략" },
  "overview.hero.aidriven": { en: "AI-Driven", ko: "AI 기반" },
  "overview.hero.baseline": { en: "baseline", ko: "베이스라인" },
  "overview.hero.aigenerated": { en: "AI-generated", ko: "AI 생성" },
  "overview.hero.beatrate": { en: "Beat Rate", ko: "승률" },
  "overview.hero.beatbaseline": { en: "beat baseline", ko: "베이스라인 초과" },
  "overview.hero.bestsharpe": { en: "Best Avg Sharpe", ko: "최고 평균 Sharpe" },
  "overview.hero.vsbaseline": { en: "Sharpe vs Baseline", ko: "Sharpe vs 베이스라인" },
  "overview.hero.vsbestbaseline": { en: "vs best baseline", ko: "vs 최고 베이스라인" },

  "overview.discovered.title": { en: "Discovered Strategies", ko: "발굴된 전략" },
  "overview.discovered.beat": { en: "strategies beat baseline", ko: "개 전략이 베이스라인 초과" },

  "overview.tried.title": { en: "Tried Hypotheses", ko: "시도한 가설" },
  "overview.next.title": { en: "Next Hypotheses", ko: "다음 가설" },
  "overview.next.planned": { en: "Planned Experiments", ko: "계획된 실험" },
  "overview.next.empty": { en: "No next steps defined yet.", ko: "다음 단계가 아직 정의되지 않았습니다." },
  "overview.directions.title": { en: "Research Directions", ko: "리서치 방향" },
  "overview.category.title": { en: "Category Performance", ko: "카테고리 성과" },
  "overview.category.strategies": { en: "strategies", ko: "전략" },
  "overview.indicators.title": { en: "Indicators Explored", ko: "탐색한 지표" },

  "overview.bestmarket.title": { en: "Best Strategy per Market", ko: "시장별 최적 전략" },
  "overview.heatmap.title": { en: "Cross-Market Performance Matrix", ko: "교차 시장 성과 매트릭스" },
  "overview.ranking.title": { en: "Full Strategy Ranking", ko: "전체 전략 순위" },

  // === Common Table Headers ===
  "table.market": { en: "Market", ko: "시장" },
  "table.strategy": { en: "Strategy", ko: "전략" },
  "table.aiselected": { en: "AI-Selected Strategy", ko: "AI 선택 전략" },
  "table.sharpe": { en: "Sharpe", ko: "Sharpe" },
  "table.return": { en: "Return", ko: "수익률" },
  "table.mdd": { en: "MDD", ko: "MDD" },
  "table.origin": { en: "Origin", ko: "출처" },
  "table.category": { en: "Category", ko: "카테고리" },
  "table.avg": { en: "Avg", ko: "평균" },
  "table.symbol": { en: "Symbol", ko: "종목" },
  "table.cagr": { en: "CAGR", ko: "CAGR" },
  "table.winrate": { en: "Win Rate", ko: "승률" },
  "table.pf": { en: "P/F", ko: "P/F" },
  "table.trades": { en: "Trades", ko: "거래수" },
  "table.weight": { en: "Weight", ko: "비중" },
  "table.metric": { en: "Metric", ko: "지표" },
  "table.totalreturn": { en: "Total Return (%)", ko: "총 수익률 (%)" },
  "table.cagr_pct": { en: "CAGR (%)", ko: "CAGR (%)" },
  "table.mdd_pct": { en: "Max Drawdown (%)", ko: "최대 낙폭 (%)" },
  "table.sharpe_ratio": { en: "Sharpe Ratio", ko: "Sharpe 비율" },
  "table.winrate_pct": { en: "Win Rate (%)", ko: "승률 (%)" },
  "table.profitfactor": { en: "Profit Factor", ko: "수익 팩터" },

  // === Badges ===
  "badge.human": { en: "Human", ko: "수동" },
  "badge.ai": { en: "AI", ko: "AI" },
  "badge.best": { en: "BEST", ko: "BEST" },
  "badge.alpha": { en: "ALPHA", ko: "ALPHA" },

  // === Strategy / Backtest Page ===
  "backtest.title": { en: "Backtest", ko: "백테스트" },
  "backtest.strategy": { en: "Strategy", ko: "전략" },
  "backtest.symbol": { en: "Symbol", ko: "종목" },
  "backtest.start": { en: "Start Date", ko: "시작일" },
  "backtest.end": { en: "End Date", ko: "종료일" },
  "backtest.capital": { en: "Capital ($)", ko: "자본금 ($)" },
  "backtest.run": { en: "Run Backtest", ko: "백테스트 실행" },
  "backtest.running": { en: "Running...", ko: "실행 중..." },
  "backtest.placeholder": { en: "Select a strategy and symbol, then click Run Backtest to see results.", ko: "전략과 종목을 선택한 후 백테스트 실행을 클릭하세요." },
  "backtest.tradehistory": { en: "Trade History", ko: "거래 내역" },

  // === Compare Page ===
  "compare.title": { en: "Strategy Comparison", ko: "전략 비교" },
  "compare.select": { en: "Strategies (select multiple)", ko: "전략 (복수 선택)" },
  "compare.run": { en: "Compare", ko: "비교" },
  "compare.running": { en: "Running...", ko: "실행 중..." },
  "compare.placeholder": { en: "Select 2 or more strategies and a symbol, then click Compare.", ko: "2개 이상의 전략과 종목을 선택한 후 비교를 클릭하세요." },
  "compare.min2": { en: "Please select at least 2 strategies.", ko: "최소 2개의 전략을 선택하세요." },
  "compare.metrics": { en: "Metrics Comparison", ko: "지표 비교" },

  // === Portfolio Page ===
  "portfolio.title": { en: "Portfolio Backtest", ko: "포트폴리오 백테스트" },
  "portfolio.universe": { en: "Universe", ko: "유니버스" },
  "portfolio.allocator": { en: "Allocator", ko: "배분기" },
  "portfolio.rebalance": { en: "Rebalance", ko: "리밸런싱" },
  "portfolio.fixed": { en: "Fixed (no rebalance)", ko: "고정 (리밸런싱 없음)" },
  "portfolio.weekly": { en: "Weekly", ko: "주간" },
  "portfolio.monthly": { en: "Monthly", ko: "월간" },
  "portfolio.quarterly": { en: "Quarterly", ko: "분기" },
  "portfolio.run": { en: "Run Portfolio", ko: "포트폴리오 실행" },
  "portfolio.running": { en: "Running...", ko: "실행 중..." },
  "portfolio.placeholder": { en: "Configure portfolio parameters and click Run Portfolio.", ko: "포트폴리오 파라미터를 설정하고 실행을 클릭하세요." },
  "portfolio.weights": { en: "Allocation Weights", ko: "배분 비중" },
  "portfolio.persymbol": { en: "Per-Symbol Equity", ko: "종목별 자산" },

  // === Research Page ===
  "research.title": { en: "AI Research Console", ko: "AI 리서치 콘솔" },
  "research.approaches": { en: "Approaches Tried", ko: "시도한 접근" },
  "research.benchmarks": { en: "Benchmark Symbols", ko: "벤치마크 종목" },
  "research.period": { en: "Test Period", ko: "테스트 기간" },
  "research.nextsteps": { en: "Next Steps", ko: "다음 단계" },
  "research.directions": { en: "Research Directions", ko: "리서치 방향" },
  "research.edit": { en: "edit", ko: "편집" },
  "research.nextsteps.empty": { en: "No next steps defined yet.", ko: "다음 단계가 아직 정의되지 않았습니다." },
  "research.directions.empty": { en: "No research directions defined yet.", ko: "리서치 방향이 아직 정의되지 않았습니다." },
  "research.add": { en: "Add", ko: "추가" },
  "research.save": { en: "Save", ko: "저장" },
  "research.cancel": { en: "Cancel", ko: "취소" },

  "research.aicycle.title": { en: "AI Research Cycle", ko: "AI 리서치 사이클" },
  "research.aicycle.subtitle": { en: "Autonomous Strategy Discovery", ko: "자율 전략 발굴" },
  "research.aicycle.desc": { en: "AI reads the research journal, identifies unexplored directions, generates a brand new strategy (Python code), validates it, backtests across all benchmark markets, and records the results — fully autonomous, no manual input needed.", ko: "AI가 리서치 저널을 읽고, 미탐색 방향을 식별하고, 새로운 전략(Python 코드)을 생성하고, 검증하고, 모든 벤치마크 시장에서 백테스트한 후 결과를 기록합니다 — 완전 자율, 수동 입력 불필요." },
  "research.aicycle.start": { en: "Start AI Cycle", ko: "AI 사이클 시작" },
  "research.aicycle.starting": { en: "Starting...", ko: "시작 중..." },
  "research.aicycle.init": { en: "Initializing...", ko: "초기화 중..." },
  "research.aicycle.running1": { en: "AI is researching... (this may take a few minutes)", ko: "AI 리서치 중... (몇 분 소요될 수 있습니다)" },
  "research.aicycle.running2": { en: "AI is researching... (generating strategy, backtesting, updating journal)", ko: "AI 리서치 중... (전략 생성, 백테스트, 저널 업데이트)" },
  "research.aicycle.success": { en: "Cycle completed successfully!", ko: "사이클 성공적으로 완료!" },
  "research.aicycle.newstrategy": { en: "New strategy discovered", ko: "새로운 전략 발굴" },
  "research.aicycle.updated": { en: "Journal updated. Refresh to see results.", ko: "저널 업데이트됨. 새로고침하여 결과를 확인하세요." },
  "research.aicycle.refresh": { en: "Refresh", ko: "새로고침" },
  "research.aicycle.completed": { en: "AI research cycle completed!", ko: "AI 리서치 사이클 완료!" },
  "research.aicycle.failed": { en: "Cycle failed", ko: "사이클 실패" },
  "research.aicycle.retry": { en: "Retry AI Cycle", ko: "AI 사이클 재시도" },

  "research.manual.title": { en: "Manual Backtest", ko: "수동 백테스트" },
  "research.manual.desc": { en: "Run an existing strategy across", ko: "기존 전략을 실행:" },
  "research.manual.category": { en: "Category", ko: "카테고리" },
  "research.manual.indicators": { en: "Indicators (comma-separated)", ko: "지표 (쉼표 구분)" },
  "research.manual.indicators.ph": { en: "e.g. RSI, MACD, EMA", ko: "예: RSI, MACD, EMA" },
  "research.manual.run": { en: "Run Research", ko: "리서치 실행" },
  "research.manual.approach": { en: "Approach Description", ko: "접근 설명" },
  "research.manual.approach.ph": { en: "Brief description of the strategy approach", ko: "전략 접근 방식에 대한 간단한 설명" },
  "research.manual.analysis": { en: "Analysis / Hypothesis", ko: "분석 / 가설" },
  "research.manual.analysis.ph": { en: "Why this strategy might work, what you're testing", ko: "이 전략이 작동할 수 있는 이유, 테스트 중인 것" },

  "research.tried.title": { en: "Tried Approaches", ko: "시도한 접근법" },
  "research.tried.delete": { en: "Delete", ko: "삭제" },
  "research.saved": { en: "Saved successfully", ko: "저장 완료" },
  "research.completed": { en: "Research completed and saved!", ko: "리서치 완료 및 저장!" },
  "research.refreshpage": { en: "Refresh Page", ko: "페이지 새로고침" },

  // === Category names ===
  "cat.trend-following": { en: "trend-following", ko: "추세추종" },
  "cat.mean-reversion": { en: "mean-reversion", ko: "평균회귀" },
  "cat.momentum": { en: "momentum", ko: "모멘텀" },
  "cat.breakout": { en: "breakout", ko: "돌파" },
  "cat.volatility": { en: "volatility", ko: "변동성" },
  "cat.composite": { en: "composite", ko: "복합" },
  "cat.other": { en: "other", ko: "기타" },

  // === Common ===
  "common.error": { en: "Error:", ko: "오류:" },
  "common.via": { en: "via", ko: "via" },

  // === Placeholder for add inputs ===
  "ph.addstep": { en: "Add new step...", ko: "새 단계 추가..." },
  "ph.adddirection": { en: "Add new direction...", ko: "새 방향 추가..." },
};

/** Get current language from localStorage, default to 'en' */
function getLang() {
  return localStorage.getItem("aam_lang") || "en";
}

/** Set language and re-apply */
function setLang(lang) {
  localStorage.setItem("aam_lang", lang);
  applyTranslations();
  updateLangToggle();
}

/** Translate a single key */
function t(key) {
  const lang = getLang();
  const entry = TRANSLATIONS[key];
  if (!entry) return null;
  return entry[lang] || entry["en"] || key;
}

/** Apply translations to all elements with data-i18n attributes */
function applyTranslations() {
  const lang = getLang();

  // Text content
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.getAttribute("data-i18n");
    const entry = TRANSLATIONS[key];
    if (entry) {
      el.textContent = entry[lang] || entry["en"];
    }
  });

  // Placeholders
  document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
    const key = el.getAttribute("data-i18n-placeholder");
    const entry = TRANSLATIONS[key];
    if (entry) {
      el.placeholder = entry[lang] || entry["en"];
    }
  });

  // Title attribute
  document.querySelectorAll("[data-i18n-title]").forEach((el) => {
    const key = el.getAttribute("data-i18n-title");
    const entry = TRANSLATIONS[key];
    if (entry) {
      el.title = entry[lang] || entry["en"];
    }
  });
}

/** Update the language toggle button state */
function updateLangToggle() {
  const lang = getLang();
  document.querySelectorAll(".lang-btn").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.lang === lang);
  });
}

/** Initialize on DOM ready */
document.addEventListener("DOMContentLoaded", () => {
  applyTranslations();
  updateLangToggle();
});
