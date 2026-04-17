// Plotly chart helpers for Auto Alpha Miner Dashboard

const chartColors = [
    '#6366f1', '#22c55e', '#f59e0b', '#ef4444', '#3b82f6',
    '#a855f7', '#ec4899', '#14b8a6', '#f97316', '#06b6d4'
];

const darkLayout = {
    margin: { t: 36, r: 20, b: 40, l: 60 },
    paper_bgcolor: 'transparent',
    plot_bgcolor: 'transparent',
    font: { size: 12, color: '#8b8fa3', family: 'Inter, sans-serif' },
    xaxis: {
        gridcolor: 'rgba(255,255,255,0.05)',
        linecolor: 'rgba(255,255,255,0.08)',
        zerolinecolor: 'rgba(255,255,255,0.08)',
    },
    yaxis: {
        gridcolor: 'rgba(255,255,255,0.05)',
        linecolor: 'rgba(255,255,255,0.08)',
        zerolinecolor: 'rgba(255,255,255,0.08)',
    },
    hovermode: 'x unified',
    hoverlabel: {
        bgcolor: '#1a1d27',
        bordercolor: '#2a2d3a',
        font: { size: 12, color: '#e4e6f0', family: 'JetBrains Mono, monospace' },
    },
    legend: {
        bgcolor: 'transparent',
        font: { color: '#8b8fa3' },
    },
    modebar: { bgcolor: 'transparent', color: '#5d6178', activecolor: '#6366f1' },
};

const plotConfig = {
    responsive: true,
    displaylogo: false,
    modeBarButtonsToRemove: ['lasso2d', 'select2d'],
};

function renderEquityChart(containerId, data) {
    const traces = [{
        x: data.equity_curve.dates,
        y: data.equity_curve.values,
        type: 'scatter',
        mode: 'lines',
        name: data.strategy,
        line: { color: '#6366f1', width: 2 },
        fill: 'tozeroy',
        fillcolor: 'rgba(99, 102, 241, 0.06)',
    }];

    // Add buy-and-hold benchmark if available
    if (data.benchmark) {
        traces.push({
            x: data.benchmark.dates,
            y: data.benchmark.values,
            type: 'scatter',
            mode: 'lines',
            name: 'Buy & Hold',
            line: { color: '#8b8fa3', width: 1.5, dash: 'dot' },
        });
    }

    const layout = {
        ...darkLayout,
        title: { text: `${data.strategy} vs Buy & Hold | ${data.symbol}`, font: { size: 14, color: '#e4e6f0' } },
        yaxis: { ...darkLayout.yaxis, title: { text: 'Equity ($)', font: { size: 11 } } },
    };

    Plotly.newPlot(containerId, traces, layout, plotConfig);
}

function renderDrawdownChart(containerId, data) {
    const traces = [{
        x: data.drawdown.dates,
        y: data.drawdown.values.map(v => v * 100),
        type: 'scatter',
        mode: 'lines',
        fill: 'tozeroy',
        name: 'Drawdown',
        line: { color: '#ef4444', width: 1.5 },
        fillcolor: 'rgba(239, 68, 68, 0.08)',
    }];

    const layout = {
        ...darkLayout,
        yaxis: { ...darkLayout.yaxis, title: { text: 'Drawdown', font: { size: 11 } }, ticksuffix: '%' },
        height: 200,
    };

    Plotly.newPlot(containerId, traces, layout, plotConfig);
}

function renderCompareChart(containerId, results) {
    const traces = results.map((r, i) => ({
        x: r.equity_curve.dates,
        y: r.equity_curve.values,
        type: 'scatter',
        mode: 'lines',
        name: r.strategy,
        line: { color: chartColors[i % chartColors.length], width: 2 },
    }));

    const layout = {
        ...darkLayout,
        title: { text: `Strategy Comparison | ${results[0]?.symbol || ''}`, font: { size: 14, color: '#e4e6f0' } },
        yaxis: { ...darkLayout.yaxis, title: { text: 'Equity ($)', font: { size: 11 } } },
    };

    Plotly.newPlot(containerId, traces, layout, plotConfig);
}

function renderHeatmap(containerId, data) {
    const trace = {
        x: data.symbols,
        y: data.strategies,
        z: data.values,
        type: 'heatmap',
        colorscale: [
            [0, '#7f1d1d'],
            [0.25, '#991b1b'],
            [0.4, '#854d0e'],
            [0.5, '#374151'],
            [0.6, '#365314'],
            [0.75, '#166534'],
            [1, '#14532d'],
        ],
        text: data.values.map(row => row.map(v => v !== null ? v.toFixed(2) : 'N/A')),
        texttemplate: '%{text}',
        textfont: { size: 12, color: '#e4e6f0', family: 'JetBrains Mono' },
        hovertemplate: '%{y} | %{x}<br>Sharpe: %{z:.2f}<extra></extra>',
        xgap: 3,
        ygap: 3,
    };

    const layout = {
        ...darkLayout,
        height: Math.max(300, data.strategies.length * 50 + 100),
        xaxis: { ...darkLayout.xaxis, fixedrange: true },
        yaxis: { ...darkLayout.yaxis, fixedrange: true },
    };

    Plotly.newPlot(containerId, [trace], layout, {
        ...plotConfig,
        staticPlot: true,
    });
}

function renderMetrics(containerId, metrics) {
    const sharpeColor = v => v >= 1 ? '#22c55e' : v >= 0.5 ? '#f59e0b' : '#ef4444';
    const retColor = v => v >= 0 ? '#22c55e' : '#ef4444';

    const items = [
        { label: 'Total Return', value: metrics.total_return + '%', color: retColor(metrics.total_return) },
        { label: 'CAGR', value: metrics.cagr + '%', color: retColor(metrics.cagr) },
        { label: 'Max Drawdown', value: metrics.max_drawdown + '%', color: '#ef4444' },
        { label: 'MDD Duration', value: metrics.max_dd_duration_days + 'd', color: '#ef4444' },
        { label: 'Sharpe', value: metrics.sharpe_ratio, color: sharpeColor(metrics.sharpe_ratio) },
        { label: 'Sortino', value: metrics.sortino_ratio, color: sharpeColor(metrics.sortino_ratio) },
        { label: 'Calmar', value: metrics.calmar_ratio, color: sharpeColor(metrics.calmar_ratio) },
        { label: 'Alpha', value: metrics.alpha + '%', color: retColor(metrics.alpha) },
        { label: 'Beta', value: metrics.beta, color: '#8b8fa3' },
        { label: 'Win Rate', value: metrics.win_rate + '%', color: metrics.win_rate >= 50 ? '#22c55e' : '#f59e0b' },
        { label: 'Profit Factor', value: metrics.profit_factor, color: metrics.profit_factor >= 1.5 ? '#22c55e' : metrics.profit_factor >= 1 ? '#f59e0b' : '#ef4444' },
        { label: 'Trades', value: metrics.trade_count, color: '#8b8fa3' },
        { label: 'Commission', value: '$' + metrics.total_commission.toLocaleString(), color: '#f59e0b' },
        { label: 'B&H Return', value: metrics.benchmark_return + '%', color: retColor(metrics.benchmark_return) },
    ];

    const html = items.map(item =>
        `<div class="metric-item">
            <div class="value" style="color:${item.color}">${item.value}</div>
            <div class="label">${item.label}</div>
        </div>`
    ).join('');

    document.getElementById(containerId).innerHTML = `<div class="metrics-grid">${html}</div>`;
}

function renderTradesTable(containerId, trades) {
    if (!trades || trades.length === 0) {
        document.getElementById(containerId).innerHTML = '<div class="empty-state"><p>No trades executed</p></div>';
        return;
    }

    let html = `<div class="table-wrap"><table>
        <thead><tr>
            <th>Entry Date</th><th>Exit Date</th><th>Entry Price</th><th>Exit Price</th><th>P&L</th><th>Return</th>
        </tr></thead><tbody>`;

    for (const t of trades) {
        const isProfit = (t.pnl || 0) >= 0;
        const cls = isProfit ? 'text-green' : 'text-red';
        html += `<tr>
            <td>${t.entry_date?.split('T')[0] || '-'}</td>
            <td>${t.exit_date?.split('T')[0] || '-'}</td>
            <td>$${t.entry_price?.toLocaleString() || '-'}</td>
            <td>${t.exit_price ? '$' + t.exit_price.toLocaleString() : '-'}</td>
            <td class="${cls}">${t.pnl != null ? (isProfit ? '+' : '') + t.pnl.toFixed(2) : '-'}</td>
            <td class="${cls}">${t.return_pct != null ? (isProfit ? '+' : '') + t.return_pct.toFixed(2) + '%' : '-'}</td>
        </tr>`;
    }

    html += '</tbody></table></div>';
    document.getElementById(containerId).innerHTML = html;
}
