let allActivities = [];
let filteredActivities = [];

const typeIcons = {
    'Fitness routine': '🏋️',
    'Food consumption': '🍽️',
    'Medication consumption': '💊',
    'Therapy': '🧘',
    'Consultation': '👨‍⚕️'
};

async function loadData() {
    try {
        const [summaryRes, activitiesRes] = await Promise.all([
            fetch('/api/summary'),
            fetch('/api/scheduled')
        ]);
        
        const summary = await summaryRes.json();
        const activities = await activitiesRes.json();
        
        allActivities = activities;
        filteredActivities = activities;
        
        renderSummary(summary);
        populateFilters();
        renderCalendar();
    } catch (error) {
        console.error('Error loading data:', error);
        document.getElementById('calendar').innerHTML = 
            '<p style="color: red;">Error loading data. Please run the scheduler first.</p>';
    }
}

function renderSummary(summary) {
    const summaryDiv = document.getElementById('summary');
    summaryDiv.innerHTML = `
        <div class="summary-card">
            <h3>Total Scheduled</h3>
            <div class="value">${summary.total_scheduled}</div>
        </div>
        <div class="summary-card">
            <h3>Activities Skipped</h3>
            <div class="value">${summary.total_skipped}</div>
        </div>
        ${Object.entries(summary.type_breakdown).slice(0, 3).map(([type, count]) => `
            <div class="summary-card">
                <h3>${type}</h3>
                <div class="value">${count}</div>
            </div>
        `).join('')}
    `;
}

function populateFilters() {
    const types = [...new Set(allActivities.map(a => a.activity_type))];
    const months = [...new Set(allActivities.map(a => a.date.substring(0, 7)))];
    
    const typeFilter = document.getElementById('typeFilter');
    types.forEach(type => {
        const option = document.createElement('option');
        option.value = type;
        option.textContent = type;
        typeFilter.appendChild(option);
    });
    
    const monthFilter = document.getElementById('monthFilter');
    months.forEach(month => {
        const option = document.createElement('option');
        option.value = month;
        option.textContent = new Date(month + '-01').toLocaleDateString('en-US', { year: 'numeric', month: 'long' });
        monthFilter.appendChild(option);
    });
}

function renderCalendar() {
    const calendar = document.getElementById('calendar');
    const byDate = {};
    
    filteredActivities.forEach(activity => {
        if (!byDate[activity.date]) {
            byDate[activity.date] = [];
        }
        byDate[activity.date].push(activity);
    });
    
    const sortedDates = Object.keys(byDate).sort();
    
    calendar.innerHTML = sortedDates.map(date => {
        const activities = byDate[date].sort((a, b) => 
            a.start_time.localeCompare(b.start_time)
        );
        
        const dateObj = new Date(date);
        const dayName = dateObj.toLocaleDateString('en-US', { weekday: 'long' });
        const formatted = dateObj.toLocaleDateString('en-US', { 
            year: 'numeric', month: 'long', day: 'numeric' 
        });
        
        return `
            <div class="day-card">
                <div class="day-header">
                    <h2>${dayName}, ${formatted}</h2>
                    <span class="badge">${activities.length} activities</span>
                </div>
                ${activities.map(activity => renderActivity(activity)).join('')}
            </div>
        `;
    }).join('');
}

function renderActivity(activity) {
    const icon = typeIcons[activity.activity_type] || '📌';
    const typeClass = `type-${activity.activity_type.toLowerCase().split(' ')[0]}`;
    
    return `
        <div class="activity">
            <div class="activity-header">
                <span class="activity-time">${activity.start_time} - ${activity.end_time}</span>
                <span class="activity-type ${typeClass}">${activity.activity_type}</span>
            </div>
            <div class="activity-name">${icon} ${activity.activity_name}</div>
            <div class="activity-details">
                ${activity.duration_min} min @ ${activity.location}
                ${activity.facilitator ? ` • with ${activity.facilitator}` : ''}
                ${activity.specialist ? ` • ${activity.specialist}` : ''}
            </div>
            ${activity.notes ? `<div class="activity-note">⚠️ ${activity.notes}</div>` : ''}
        </div>
    `;
}

document.getElementById('searchInput').addEventListener('input', (e) => {
    const search = e.target.value.toLowerCase();
    filteredActivities = allActivities.filter(a => 
        a.activity_name.toLowerCase().includes(search) ||
        a.location.toLowerCase().includes(search)
    );
    renderCalendar();
});

document.getElementById('typeFilter').addEventListener('change', (e) => {
    const type = e.target.value;
    filteredActivities = type ? 
        allActivities.filter(a => a.activity_type === type) : 
        allActivities;
    renderCalendar();
});

document.getElementById('monthFilter').addEventListener('change', (e) => {
    const month = e.target.value;
    filteredActivities = month ? 
        allActivities.filter(a => a.date.startsWith(month)) : 
        allActivities;
    renderCalendar();
});

loadData();
