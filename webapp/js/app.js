const tg = window.Telegram.WebApp;

// Initialize
tg.expand();
tg.MainButton.hide();

// State
let state = {
    positions: [],
    orders: [],
    balance: null,
    analysis: null
};

// Elements
const els = {
    username: document.getElementById('username'),
    totalEquity: document.getElementById('total-equity'),
    availableBalance: document.getElementById('available-balance'),
    marginUsage: document.getElementById('margin-usage'),
    positionsList: document.getElementById('positions-list'),
    ordersList: document.getElementById('orders-list'),
    aiSuggestions: document.getElementById('ai-suggestions'),
    tabs: document.querySelectorAll('.tab-btn'),
    tabContents: document.querySelectorAll('.tab-content')
};

// Set user info
if (tg.initDataUnsafe && tg.initDataUnsafe.user) {
    els.username.textContent = `👋 ${tg.initDataUnsafe.user.first_name}`;
} else {
    els.username.textContent = '👋 Trader';
}

// Tab switching
els.tabs.forEach(btn => {
    btn.addEventListener('click', () => {
        els.tabs.forEach(b => b.classList.remove('active'));
        els.tabContents.forEach(c => c.classList.remove('active'));

        btn.classList.add('active');
        document.getElementById(`${btn.dataset.tab}-tab`).classList.add('active');
    });
});

// Fetch Data
async function fetchData() {
    try {
        const response = await fetch('/api/data');
        const data = await response.json();

        state = data;
        render();
    } catch (error) {
        console.error('Failed to fetch data:', error);
        tg.showAlert('Failed to load data. Please try again.');
    }
}

// Render Functions
function render() {
    renderBalance();
    renderPositions();
    renderOrders();
    renderAnalysis();
}

function renderBalance() {
    if (!state.balance) return;

    const equity = parseFloat(state.balance.totalEquity);
    const available = parseFloat(state.balance.totalAvailableBalance);
    const margin = parseFloat(state.balance.totalMarginBalance);
    const initialMargin = parseFloat(state.balance.totalInitialMargin);

    let usage = 0;
    if (margin > 0) {
        usage = (initialMargin / margin) * 100;
    }

    els.totalEquity.textContent = `$${equity.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    els.availableBalance.textContent = `$${available.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    els.marginUsage.textContent = `${usage.toFixed(2)}%`;

    // Color code margin usage
    if (usage > 80) els.marginUsage.style.color = 'var(--danger-color)';
    else if (usage > 60) els.marginUsage.style.color = 'var(--warning-color)';
    else els.marginUsage.style.color = 'var(--success-color)';
}

function renderPositions() {
    if (!state.positions || state.positions.length === 0) {
        els.positionsList.innerHTML = '<div class="empty-state">No open positions</div>';
        return;
    }

    els.positionsList.innerHTML = state.positions.map(pos => {
        const pnl = parseFloat(pos.unrealisedPnl);
        const pnlClass = pnl >= 0 ? 'positive' : 'negative';
        const sideClass = pos.side === 'Buy' ? 'side-buy' : 'side-sell';

        return `
            <div class="card">
                <div class="card-header">
                    <div class="symbol">
                        ${pos.symbol}
                        <span class="side-badge ${sideClass}">${pos.side}</span>
                    </div>
                    <div class="pnl ${pnlClass}">
                        ${pnl >= 0 ? '+' : ''}$${pnl.toFixed(2)}
                    </div>
                </div>
                <div class="card-row">
                    <span class="label">Size</span>
                    <span>${pos.size}</span>
                </div>
                <div class="card-row">
                    <span class="label">Entry Price</span>
                    <span>$${parseFloat(pos.avgPrice).toFixed(4)}</span>
                </div>
                <div class="card-row">
                    <span class="label">Mark Price</span>
                    <span>$${parseFloat(pos.markPrice).toFixed(4)}</span>
                </div>
                <div class="card-row">
                    <span class="label">Leverage</span>
                    <span>${pos.leverage}x</span>
                </div>
                <div class="card-row">
                    <span class="label">Stop Loss</span>
                    <span>${parseFloat(pos.stopLoss) > 0 ? '$' + parseFloat(pos.stopLoss).toFixed(4) : '-'}</span>
                </div>
                <div class="card-row">
                    <span class="label">Take Profit</span>
                    <span>${parseFloat(pos.takeProfit) > 0 ? '$' + parseFloat(pos.takeProfit).toFixed(4) : '-'}</span>
                </div>
            </div>
        `;
    }).join('');
}

function renderOrders() {
    if (!state.orders || state.orders.length === 0) {
        els.ordersList.innerHTML = '<div class="empty-state">No open orders</div>';
        return;
    }

    els.ordersList.innerHTML = state.orders.map(order => {
        const sideClass = order.side === 'Buy' ? 'side-buy' : 'side-sell';

        return `
            <div class="card">
                <div class="card-header">
                    <div class="symbol">
                        ${order.symbol}
                        <span class="side-badge ${sideClass}">${order.side}</span>
                    </div>
                    <div>${order.orderType}</div>
                </div>
                <div class="card-row">
                    <span class="label">Price</span>
                    <span>$${parseFloat(order.price).toFixed(4)}</span>
                </div>
                <div class="card-row">
                    <span class="label">Qty</span>
                    <span>${order.qty}</span>
                </div>
            </div>
        `;
    }).join('');
}

function renderAnalysis() {
    if (!state.analysis) {
        els.aiSuggestions.innerHTML = '<div class="empty-state">Analysis not available</div>';
        return;
    }

    let html = '';

    if (state.analysis.urgent && state.analysis.urgent.length > 0) {
        html += `<h4>🔴 Urgent Action Needed</h4>`;
        html += state.analysis.urgent.map(s => `<div class="suggestion-item urgent">${s}</div>`).join('');
    }

    if (state.analysis.recommended && state.analysis.recommended.length > 0) {
        html += `<h4>🟡 Recommended</h4>`;
        html += state.analysis.recommended.map(s => `<div class="suggestion-item recommended">${s}</div>`).join('');
    }

    if (state.analysis.optional && state.analysis.optional.length > 0) {
        html += `<h4>🟢 Optional</h4>`;
        html += state.analysis.optional.map(s => `<div class="suggestion-item optional">${s}</div>`).join('');
    }

    els.aiSuggestions.innerHTML = html;
}

// Initial load
fetchData();

// Refresh every 10 seconds
setInterval(fetchData, 10000);
