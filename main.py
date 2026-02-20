import os
import json
import sys
from data.generate_data import save_all_data
from scheduler import ResourceAllocator


def main():
    print("=" * 60)
    print("ELYX HEALTH RESOURCE ALLOCATOR")
    print("=" * 60)

    print("\n[1/4] Generating test data...")
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    save_all_data(data_dir)

    print("\n[2/4] Running resource allocator scheduler...")
    allocator = ResourceAllocator(data_dir)
    scheduled_plan, skipped = allocator.schedule()

    print("\n[3/4] Saving scheduled plan...")
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)

    with open(os.path.join(output_dir, "scheduled_plan.json"), "w") as f:
        json.dump(scheduled_plan, f, indent=2)

    with open(os.path.join(output_dir, "skipped_activities.json"), "w") as f:
        json.dump(skipped, f, indent=2)

    print("\n[4/4] Generating calendar output...")
    calendar_text = allocator.format_calendar(scheduled_plan, skipped)

    calendar_path = os.path.join(output_dir, "personalized_plan.txt")
    with open(calendar_path, "w", encoding="utf-8") as f:
        f.write(calendar_text)

    cal_lines = calendar_text.split("\n")
    print("\n" + "\n".join(cal_lines[:150]))
    if len(cal_lines) > 150:
        print(f"\n... ({len(cal_lines) - 150} more lines)")

    print(f"\n{'=' * 60}")
    print(f"RESULTS:")
    print(f"  Activities scheduled: {len(scheduled_plan)}")
    print(f"  Activities skipped:   {len(skipped)}")
    print(f"  Calendar saved to:    {calendar_path}")
    print(f"  Full plan JSON:       {os.path.join(output_dir, 'scheduled_plan.json')}")
    print(f"{'=' * 60}")

    # Ask if user wants to start web server
    print("\n" + "=" * 60)
    print("WEB SERVER")
    print("=" * 60)
    response = input("\nWould you like to start the web server to view the calendar? (y/n): ").lower()

    if response == 'y':
        print("\nStarting web server...")
        print("Open your browser and navigate to: http://localhost:5000")
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