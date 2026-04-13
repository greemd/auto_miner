// Plotly chart helpers for Auto Alpha Miner Dashboard

const chartColors = [
    '#2196F3', '#FF5722', '#4CAF50', '#9C27B0', '#FF9800',
    '#00BCD4', '#E91E63', '#8BC34A', '#3F51B5', '#CDDC39'
];

const defaultLayout = {
    margin: { t: 30, r: 30, b: 40, l: 60 },
    paper_bgcolor: 'transparent',
    plot_bgcolor: 'transparent',
    font: { size: 12 },
    xaxis: { gridcolor: '#eee' },
    yaxis: { gridcolor: '#eee' },
    hovermode: 'x unified',
};

function renderEquityChart(containerId, data) {
    const traces = [{
        x: data.equity_curve.dates,
        y: data.equity_curve.values,
        type: 'scatter',
        mode: 'lines',
        name: 'Equity',
        line: { color: '#2196F3', width: 2 },
    }];

    const layout = {
        ...defaultLayout,
        title: `${data.strategy} | ${data.symbol}`,
        yaxis: { ...defaultLayout.yaxis, title: 'Equity' },
    };

    Plotly.newPlot(containerId, traces, layout, { responsive: true });
}

function renderDrawdownChart(containerId, data) {
    const traces = [{
        x: data.drawdown.dates,
        y: data.drawdown.values.map(v => v * 100),
        type: 'scatter',
        mode: 'lines',
        fill: 'tozeroy',
        name: 'Drawdown',
        line: { color: '#E91E63', width: 1 },
        fillcolor: 'rgba(233, 30, 99, 0.15)',
    }];

    const layout = {
        ...defaultLayout,
        yaxis: { ...defaultLayout.yaxis, title: 'Drawdown (%)', ticksuffix: '%' },
        height: 200,
    };

    Plotly.newPlot(containerId, traces, layout, { responsive: true });
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
        ...defaultLayout,
        title: `Strategy Comparison | ${results[0]?.symbol || ''}`,
        yaxis: { ...defaultLayout.yaxis, title: 'Equity' },
    };

    Plotly.newPlot(containerId, traces, layout, { responsive: true });
}

function renderHeatmap(containerId, data) {
    // data = { strategies: [...], symbols: [...], values: [[...], ...] }
    const trace = {
        x: data.symbols,
        y: data.strategies,
        z: data.values,
        type: 'heatmap',
        colorscale: 'RdYlGn',
        text: data.values.map(row => row.map(v => v !== null ? v.toFixed(2) : 'N/A')),
        texttemplate: '%{text}',
        hovertemplate: '%{y} | %{x}<br>Sharpe: %{z:.2f}<extra></extra>',
    };

    const layout = {
        ...defaultLayout,
        title: 'Sharpe Ratio Heatmap',
        height: Math.max(300, data.strategies.length * 40 + 100),
    };

    Plotly.newPlot(containerId, [trace], layout, { responsive: true });
}

function renderMetrics(containerId, metrics) {
    const items = [
        { label: 'Total Return', value: metrics.total_return + '%' },
        { label: 'CAGR', value: metrics.cagr + '%' },
        { label: 'Max Drawdown', value: metrics.max_drawdown + '%' },
        { label: 'Sharpe Ratio', value: metrics.sharpe_ratio },
        { label: 'Win Rate', value: metrics.win_rate + '%' },
        { label: 'Profit Factor', value: metrics.profit_factor },
        { label: 'Trades', value: metrics.trade_count },
    ];

    const html = items.map(item =>
        `<div class="metric-item">
            <div class="value">${item.value}</div>
            <div class="label">${item.label}</div>
        </div>`
    ).join('');

    document.getElementById(containerId).innerHTML = `<div class="metrics-grid">${html}</div>`;
}

function renderTradesTable(containerId, trades) {
    if (!trades || trades.length === 0) {
        document.getElementById(containerId).innerHTML = '<p>No trades</p>';
        return;
    }

    let html = `<table role="grid">
        <thead><tr>
            <th>Entry</th><th>Exit</th><th>Entry Price</th><th>Exit Price</th><th>P&L</th><th>Return</th>
        </tr></thead><tbody>`;

    for (const t of trades) {
        const pnlColor = (t.pnl || 0) >= 0 ? '#2e7d32' : '#c62828';
        html += `<tr>
            <td>${t.entry_date?.split('T')[0] || '-'}</td>
            <td>${t.exit_date?.split('T')[0] || '-'}</td>
            <td>${t.entry_price}</td>
            <td>${t.exit_price || '-'}</td>
            <td style="color:${pnlColor}">${t.pnl != null ? t.pnl.toFixed(2) : '-'}</td>
            <td style="color:${pnlColor}">${t.return_pct != null ? t.return_pct.toFixed(2) + '%' : '-'}</td>
        </tr>`;
    }

    html += '</tbody></table>';
    document.getElementById(containerId).innerHTML = html;
}
