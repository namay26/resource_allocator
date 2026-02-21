# ELYX Health Planner

A resource allocation and scheduling system for personalized health plans that manages activities, resources, and constraints over time.

## System Assumptions

Currently, this project does not implement user-specific state management. The generated schedule is stored in the server’s project directory, so if one user triggers scheduling, the resulting schedule becomes visible to all users accessing the application.

### 1. Time and Scheduling

- **Scheduling Period**: Fixed 3-month period (July 1 - September 30, 2025)
- **Time Granularity**: Activities scheduled in minute-level precision
- **Time Format**: 24-hour format (HH:MM)
- **Availability Windows**: Represented as lists of (start_time, end_time) tuples per date
- **No Overnight Activities**: All activities must start and end on the same day
- **Sequential Scheduling**: Activities are scheduled in order of their ID (priority)
- **No Buffer Time**: No automatic buffer/transition time added between activities
- **Slot Finding**: Closest available slot to preferred time is selected

### 2. Activity Frequency

- **Period Types**: 
  - "week" - activities scheduled per week
  - "month" - activities scheduled per month
  - "daily" - activities scheduled every day
- **Times Per Period**: Number of occurrences within the period
- **Distribution**: Activities evenly distributed across the period
- **No Carryover**: Missed activities don't accumulate to next period

### 3. Resource Constraints

#### Client Availability
- **Primary Constraint**: Client must be available for all activities
- **No Assumptions**: System doesn't assume client can extend their availability
- **Travel Override**: Client availability may be restricted during travel

#### Facilitators/Specialists/Allied Health
- **Optional Resources**: Not all activities require these resources
- **Exclusive Booking**: Person can only facilitate one activity at a time
- **No Multi-Day Bookings**: Availability checked per individual date
- **Remote Fallback**: If resource unavailable, activity may be marked as remote if `remote_possible: true`

#### Equipment
- **Shared Resources**: Equipment can be used by different activities if time slots don't overlap
- **Location-Bound**: Equipment availability tied to specific locations
- **No Maintenance Windows**: System doesn't account for equipment downtime

### 4. Travel Considerations

- **Travel Plans**: Defined with start date, end date, and destination
- **Travel Lookup**: Each date mapped to a single travel plan (no overlapping trips)
- **Location Feasibility**:
  - Activities marked `remote_possible: true` can be done while traveling
  - "Any" location activities are always feasible
  - Gym/Pool activities possible if destination `has_gym`/`has_pool` is true
  - Kitchen activities not possible if destination has no kitchen
  - Clinic/Studio/Lab activities require `remote_possible: true` while traveling
- **Backup Activities**: Listed alternatives when primary activity not feasible during travel
- **No Travel Time**: System doesn't account for transit time to/from destination

### 5. Activity Properties

#### Required Fields
- `id`: Unique identifier (integer)
- `name`: Activity name (string)
- `type`: Category (Fitness routine, Food consumption, Medication consumption, Therapy, Consultation)
- `period`: "week" or "month"
- `times_per_period`: Number (integer)
- `duration_min`: Duration in minutes (integer)
- `preferred_time`: Preferred start time in HH:MM format

#### Optional Fields
- `frequency`: Override for daily activities
- `location`: Where activity takes place
- `facilitator`: Person facilitating the activity
- `specialist`: Medical specialist involved
- `allied_health`: Allied health professional involved
- `equipment`: List of required equipment
- `remote_possible`: Boolean flag for remote feasibility
- `backup_activities`: List of alternative activities
- `skip_adjustments`: Note about what to do when activity is skipped
- `prep`: Preparation instructions
- `details`: Activity details
- `metrics`: List of metrics to track

### 6. Scheduling Logic

#### Priority Rules
1. **Activity ID Order**: Lower ID = higher priority
2. **Date Order**: Earlier dates processed first within each activity
3. **No Preemption**: Once scheduled, activities cannot be bumped by lower priority activities

#### Slot Selection
1. **Exact Match**: If preferred time fits perfectly, use it
2. **Closest Fit**: Find available slot closest to preferred time
3. **Window Boundaries**: Consider both start and end of available windows
4. **Minimum Duration**: Slot must accommodate full activity duration

#### Conflict Resolution
- **Resource Unavailable**: Skip activity and log reason
- **No Available Slot**: Skip activity and log reason

### 7. Limitations

- **No Optimization**: Greedy scheduling by priority, not optimal
- **No Rescheduling**: Skipped activities not automatically rescheduled


## Installation

```bash
pip install flask
```

## Usage

### Quick Start (Web Interface)

1. Start the web server:
```bash
python main.py
```

2. Open browser to `http://localhost:5000`

3. Click the **"Run Scheduler"** button on first load

4. View your personalized health plan in the calendar

## File Structure

```
elyx/
├── data/                          # Input data (JSON)
│   └── generate_data.py           # Test data generator
├── output/                        # Scheduled results (JSON + TXT)
│   ├── scheduled_plan.json
│   ├── skipped_activities.json
│   └── personalized_plan.txt
├── static/                        # CSS and JavaScript
│   ├── style.css
│   ├── script.js                  # Calendar page logic
│   └── skipped.js                 # Skipped activities page logic
├── templates/                     # HTML templates
│   ├── calendar.html
│   └── skipped.html
├── scheduler.py                   # Core scheduling logic
├── app.py                         # Flask web server
├── main.py                        # Application entry point
└── README.md                      # This file
```

## API Endpoints

- `GET /` - Main calendar view
- `GET /skipped` - Skipped activities view
- `GET /api/scheduled` - Returns scheduled activities JSON
- `GET /api/skipped` - Returns skipped activities JSON
- `GET /api/summary` - Returns summary statistics
- `POST /api/run-scheduler` - Triggers data generation and scheduling

## Workflow

1. **First Load**: User opens web interface
2. **Check Data**: Frontend checks if scheduled data exists
3. **Show Button**: If no data, displays "Run Scheduler" button
4. **Generate Data**: Button click triggers `/api/run-scheduler`
5. **Run Scheduler**: Backend generates test data and runs scheduling algorithm
6. **Save Results**: Outputs saved to `output/` directory
7. **Display Results**: Calendar and skipped activities pages load data
8. **Re-run**: User can re-run scheduler at any time (regenerates all data)
