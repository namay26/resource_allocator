let allActivities = [];
let currentView = 'week';

async function checkDataAndLoad() {
    try {
        const response = await fetch('/api/scheduled');
        if (response.status === 404 || response.status === 500) {
            showSchedulerButton();
            return;
        }
        const data = await response.json();
        if (!data || data.length === 0) {
            showSchedulerButton();
            return;
        }
        hideSchedulerButton();
        await loadScheduledData();
    } catch (error) {
        console.error('Error checking data:', error);
        showSchedulerButton();
    }
}

function showSchedulerButton() {
    const container = document.querySelector('.container');
    const existingButton = document.getElementById('schedulerButton');
    if (existingButton) return;
    
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
}

function hideSchedulerButton() {
    const button = document.getElementById('schedulerButton');
    if (button) {
        button.remove();
    }
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
                hideSchedulerButton();
                loadScheduledData();
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

async function loadScheduledData() {
}

checkDataAndLoad();