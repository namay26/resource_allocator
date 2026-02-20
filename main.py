import os
import json
import sys
from data.generate_data import save_all_data
from scheduler import ResourceAllocator


def main():
    print("=" * 60)
    print("ELYX HEALTH RESOURCE ALLOCATOR")
    print("=" * 60)
    print("\nStarting web server...")
    print("Open your browser and navigate to: http://localhost:5000")
    print("\nClick 'Run Scheduler' button to generate your health plan.")
    print("Press Ctrl+C to stop the server\n")
    
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
    except ImportError:
        print("\nError: Flask is not installed. Install it with: pip install flask")


if __name__ == "__main__":
    main()