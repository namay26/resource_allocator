let allSkipped = [];
let filteredSkipped = [];

async function loadSkippedData() {
    try {
        const response = await fetch('/api/skipped');
        const data = await response.json();
        
        allSkipped = data.filter(item => item.activity);
        filteredSkipped = allSkipped;
        
        renderSkippedSummary();
        populateReasonFilter();
        renderSkippedList();
    } catch (error) {
        console.error('Error loading skipped data:', error);
        document.getElementById('skippedList').innerHTML = 
            '<p style="color: red;">Error loading data. Please run the scheduler first.</p>';
    }
}

function renderSkippedSummary() {
    const summary = document.getElementById('skippedSummary');
    
    const reasonCounts = {};
    allSkipped.forEach(item => {
        const reason = item.reason || 'Unknown';
        reasonCounts[reason] = (reasonCounts[reason] || 0) + 1;
    });
    
    const topReasons = Object.entries(reasonCounts)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5);
    
    summary.innerHTML = `
        <div class="summary-cards">
            <div class="summary-card">
                <h3>Total Skipped</h3>
                <div class="value">${allSkipped.length}</div>
            </div>
            ${topReasons.map(([reason, count]) => `
                <div class="summary-card">
                    <h3>${reason.substring(0, 30)}...</h3>
                    <div class="value">${count}</div>
                </div>
            `).join('')}
        </div>
    `;
}

function populateReasonFilter() {
    const reasons = [...new Set(allSkipped.map(a => a.reason).filter(Boolean))];
    const reasonFilter = document.getElementById('reasonFilter');
    
    reasons.forEach(reason => {
        const option = document.createElement('option');
        option.value = reason;
        option.textContent = reason.substring(0, 50) + (reason.length > 50 ? '...' : '');
        reasonFilter.appendChild(option);
    });
}

function renderSkippedList() {
    const list = document.getElementById('skippedList');
    
    const byDate = {};
    filteredSkipped.forEach(item => {
        const date = item.date || 'No date';
        if (!byDate[date]) {
            byDate[date] = [];
        }
        byDate[date].push(item);
    });
    
    const sortedDates = Object.keys(byDate).sort().reverse();
    
    list.innerHTML = sortedDates.map(date => {
        const items = byDate[date];
        
        return `
            <div style="margin-bottom: 2rem;">
                <h3 style="margin-bottom: 1rem; color: #667eea;">${date}</h3>
                ${items.map(item => `
                    <div class="skipped-item">
                        <div class="skipped-header">
                            <span class="skipped-activity">❌ ${item.activity}</span>
                        </div>
                        <div class="skipped-reason">${item.reason || 'No reason provided'}</div>
                        ${item.adjustment ? `<div class="skipped-adjustment">${item.adjustment}</div>` : ''}
                    </div>
                `).join('')}
            </div>
        `;
    }).join('');
}

document.getElementById('searchInput').addEventListener('input', (e) => {
    const search = e.target.value.toLowerCase();
    filteredSkipped = allSkipped.filter(item => 
        (item.activity || '').toLowerCase().includes(search) ||
        (item.reason || '').toLowerCase().includes(search)
    );
    renderSkippedList();
});

document.getElementById('reasonFilter').addEventListener('change', (e) => {
    const reason = e.target.value;
    filteredSkipped = reason ? 
        allSkipped.filter(item => item.reason === reason) : 
        allSkipped;
    renderSkippedList();
});

loadSkippedData();
