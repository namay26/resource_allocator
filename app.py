from flask import Flask, render_template, jsonify
import json
import os

app = Flask(__name__)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")

@app.route('/')
def index():
    """Main calendar view"""
    return render_template('calendar.html')

@app.route('/skipped')
def skipped():
    """Skipped activities view"""
    return render_template('skipped.html')

@app.route('/api/scheduled')
def get_scheduled():
    """API endpoint for scheduled activities"""
    try:
        with open(os.path.join(OUTPUT_DIR, 'scheduled_plan.json'), 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except FileNotFoundError:
        return jsonify([]), 404

@app.route('/api/skipped')
def get_skipped():
    """API endpoint for skipped activities"""
    try:
        with open(os.path.join(OUTPUT_DIR, 'skipped_activities.json'), 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except FileNotFoundError:
        return jsonify([]), 404

@app.route('/api/summary')
def get_summary():
    """API endpoint for summary statistics"""
    try:
        with open(os.path.join(OUTPUT_DIR, 'scheduled_plan.json'), 'r') as f:
            scheduled = json.load(f)
        with open(os.path.join(OUTPUT_DIR, 'skipped_activities.json'), 'r') as f:
            skipped = json.load(f)
        
        type_counts = {}
        for activity in scheduled:
            activity_type = activity.get('activity_type', 'Unknown')
            type_counts[activity_type] = type_counts.get(activity_type, 0) + 1
        
        return jsonify({
            'total_scheduled': len(scheduled),
            'total_skipped': len(skipped),
            'type_breakdown': type_counts
        })
    except FileNotFoundError:
        return jsonify({'error': 'Data not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
