let allSkipped = [];
let filteredSkipped = [];

async function checkDataAndLoad() {
    try {
        const response = await fetch('/api/skipped');
        if (response.status === 404 || response.status === 500) {
            showSchedulerButton();
            return;
        }
        const data = await response.json();
        if (!data || data.length === 0) {
            showSchedulerButton();
            return;
        }
        await loadSkippedData();
    } catch (error) {
        console.error('Error checking data:', error);
        showSchedulerButton();
    }
}

function showSchedulerButton() {
    const container = document.querySelector('.container');
    const buttonContainer = document.createElement('div');
    buttonContainer.id = 'schedulerButton';
    buttonContainer.style.textAlign = 'center';
    buttonContainer.style.padding = '3rem';
    buttonContainer.innerHTML = `
        <div style="background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); max-width: 500px; margin: 0 auto;">
            <h2 style="color: #667eea; margin-bottom: 1rem;">Welcome to ELYX Health Planner</h2>
            <p style="color: #666; margin-bottom: 2rem;">No schedule found. Click the button below to generate your personalized health plan.</p>
            <button onclick="runScheduler()" id="runSchedulerBtn" style="background: #667eea; color: white; padding: 1rem 2rem; border: none; border-radius: 4px; font-size: 1rem; cursor: pointer; font-weight: 600;">
                🏥 Run Scheduler
            </button>
            <div id="schedulerStatus" style="margin-top: 1rem; color: #666;"></div>
        </div>
    `;
    container.insertBefore(buttonContainer, container.firstChild);

    document.querySelector('.filters').style.display = 'none';
}

async function runScheduler() {
    const btn = document.getElementById('runSchedulerBtn');
    const status = document.getElementById('schedulerStatus');
    
    btn.disabled = true;
    btn.textContent = '⏳ Running scheduler...';
    status.textContent = 'This may take a few moments...';
    status.style.color = '#667eea';
    
    try {
        const response = await fetch('/api/run-scheduler', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const result = await response.json();
        
        if (result.success) {
            status.textContent = `✅ Success! Scheduled ${result.scheduled} activities, ${result.skipped} skipped.`;
            status.style.color = '#48bb78';
            
            setTimeout(() => {
                location.reload();
            }, 1500);
        } else {
            throw new Error(result.error || 'Unknown error');
        }
    } catch (error) {
        console.error('Error running scheduler:', error);
        status.textContent = `❌ Error: ${error.message}`;
        status.style.color = '#f56565';
        btn.disabled = false;
        btn.textContent = '🔄 Try Again';
    }
}

async function loadSkippedData() {
    try {
        const response = await fetch('/api/skipped');
        const data = await response.json();
        
        allSkipped = data.filter(item => item.activity);
        filteredSkipped = allSkipped;

        document.querySelector('.filters').style.display = 'flex';
        
        renderSkippedSummary();
        populateReasonFilter();
        renderSkippedList();
    } catch (error) {
        console.error('Error loading skipped data:', error);
        document.getElementById('skippedList').innerHTML = 
            '<p style="color: red;">Error loading data.</p>';
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

checkDataAndLoad();
