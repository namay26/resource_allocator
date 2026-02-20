import json
import os
from datetime import datetime, timedelta, time
from collections import defaultdict


class ResourceAllocator:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.action_plan = self._load("action_plan.json")
        self.facilitator_schedules = self._load("facilitator_schedules.json")
        self.specialist_schedules = self._load("specialist_schedules.json")
        self.allied_health_schedules = self._load("allied_health_schedules.json")
        self.equipment_availability = self._load("equipment_availability.json")
        self.client_schedule = self._load("client_schedule.json")
        self.travel_plans = self._load("travel_plans.json")

        self.start_date = datetime(2025, 7, 1)
        self.end_date = datetime(2025, 9, 30)

        self.travel_lookup = {}
        for trip in self.travel_plans:
            d = datetime.strptime(trip["start"], "%Y-%m-%d")
            end = datetime.strptime(trip["end"], "%Y-%m-%d")
            while d <= end:
                self.travel_lookup[d.strftime("%Y-%m-%d")] = trip
                d += timedelta(days=1)

        self.scheduled = defaultdict(list)

    def _load(self, filename):
        path = os.path.join(self.data_dir, filename)
        with open(path, "r") as f:
            return json.load(f)

    def _time_to_minutes(self, t_str):
        """Convert 'HH:MM' to minutes since midnight."""
        h, m = map(int, t_str.split(":"))
        return h * 60 + m

    def _minutes_to_time(self, mins):
        """Convert minutes since midnight to 'HH:MM'."""
        h = mins // 60
        m = mins % 60
        return f"{h:02d}:{m:02d}"

    def _get_available_windows(self, date_str, windows_list):
        """Given a list of (start, end) string tuples, return as minute ranges."""
        result = []
        for start, end in windows_list:
            result.append((self._time_to_minutes(start), self._time_to_minutes(end)))
        return result

    def _intersect_windows(self, windows_a, windows_b):
        """Return intersection of two lists of (start_min, end_min) ranges."""
        result = []
        for a_start, a_end in windows_a:
            for b_start, b_end in windows_b:
                start = max(a_start, b_start)
                end = min(a_end, b_end)
                if start < end:
                    result.append((start, end))
        return result

    def _subtract_scheduled(self, date_str, windows):
        """Remove already-scheduled time blocks from available windows."""
        busy = sorted(self.scheduled[date_str], key=lambda x: x[0])
        result = []
        for w_start, w_end in windows:
            current = w_start
            for b_start, b_end, _ in busy:
                if b_end <= current:
                    continue
                if b_start >= w_end:
                    break
                if b_start > current:
                    result.append((current, b_start))
                current = max(current, b_end)
            if current < w_end:
                result.append((current, w_end))
        return result

    def _find_slot(self, date_str, duration_min, preferred_time_str, available_windows):
        """Find the best slot closest to preferred time within available windows."""
        preferred = self._time_to_minutes(preferred_time_str)

        free = self._subtract_scheduled(date_str, available_windows)

        best_slot = None
        best_distance = float('inf')

        for w_start, w_end in free:
            if w_end - w_start < duration_min:
                continue

            if preferred >= w_start and preferred + duration_min <= w_end:
                return preferred  

            slot_start = w_start
            dist = abs(slot_start - preferred)
            if dist < best_distance:
                best_distance = dist
                best_slot = slot_start

            slot_start = w_end - duration_min
            if slot_start >= w_start:
                dist = abs(slot_start - preferred)
                if dist < best_distance:
                    best_distance = dist
                    best_slot = slot_start

            clamped = max(w_start, min(preferred, w_end - duration_min))
            if clamped >= w_start and clamped + duration_min <= w_end:
                dist = abs(clamped - preferred)
                if dist < best_distance:
                    best_distance = dist
                    best_slot = clamped

        return best_slot

    def _is_traveling(self, date_str):
        return date_str in self.travel_lookup

    def _get_travel_info(self, date_str):
        return self.travel_lookup.get(date_str)

    def _activity_possible_while_traveling(self, activity, travel_info):
        """Check if activity can be done while traveling."""
        if activity.get("remote_possible"):
            return True

        location = activity.get("location", "")
        if "Any" in location:
            return True
        if "Home" in location and not travel_info.get("has_kitchen") and "Kitchen" in location:
            return False
        if "Gym" in location and travel_info.get("has_gym"):
            return True
        if "Pool" in location and travel_info.get("has_pool"):
            return True
        if location in ["Home", "Home / Kitchen"] and not travel_info.get("has_kitchen"):
            if "kitchen" in [e.lower() for e in activity.get("equipment", [])]:
                return False

        if "Clinic" in location or "Studio" in location or "Lab" in location:
            if activity.get("remote_possible"):
                return True
            return False

        return True

    def _check_resource_availability(self, activity, date_str):
        """Check all required resources and return combined available windows, or None."""
        client_windows = self.client_schedule.get(date_str, [])
        if not client_windows:
            return None
        available = self._get_available_windows(date_str, client_windows)

        facilitator = activity.get("facilitator")
        if facilitator:
            fac_windows = self.facilitator_schedules.get(facilitator, {}).get(date_str, [])
            if not fac_windows:
                return None
            fac_mins = self._get_available_windows(date_str, fac_windows)
            available = self._intersect_windows(available, fac_mins)
            if not available:
                return None

        specialist = activity.get("specialist")
        if specialist:
            spec_windows = self.specialist_schedules.get(specialist, {}).get(date_str, [])
            if not spec_windows:
                return None
            spec_mins = self._get_available_windows(date_str, spec_windows)
            available = self._intersect_windows(available, spec_mins)
            if not available:
                return None

        allied = activity.get("allied_health")
        if allied:
            ah_windows = self.allied_health_schedules.get(allied, {}).get(date_str, [])
            if not ah_windows:
                return None
            ah_mins = self._get_available_windows(date_str, ah_windows)
            available = self._intersect_windows(available, ah_mins)
            if not available:
                return None

        equipment_needed = activity.get("equipment", [])
        for eq in equipment_needed:
            eq_windows = self.equipment_availability.get(eq, {}).get(date_str, [])
            if not eq_windows:
                return None
            eq_mins = self._get_available_windows(date_str, eq_windows)
            available = self._intersect_windows(available, eq_mins)
            if not available:
                return None

        return available

    def _get_dates_for_period(self, activity):
        """Determine which dates this activity should be scheduled on."""
        period = activity.get("period", "week")
        times_per = activity.get("times_per_period", 1)
        frequency = activity.get("frequency", "weekly")

        all_dates = []
        d = self.start_date
        while d <= self.end_date:
            all_dates.append(d)
            d += timedelta(days=1)

        if frequency == "daily" or period == "week" and times_per == 7:
            return all_dates

        target_dates = []

        if period == "week":
            weeks = defaultdict(list)
            for d in all_dates:
                week_key = d.isocalendar()[1]
                weeks[week_key].append(d)

            for week_key in sorted(weeks.keys()):
                week_dates = weeks[week_key]
                if times_per >= len(week_dates):
                    target_dates.extend(week_dates)
                else:
                    step = len(week_dates) / times_per
                    for i in range(times_per):
                        idx = int(i * step)
                        if idx < len(week_dates):
                            target_dates.append(week_dates[idx])

        elif period == "month":
            months = defaultdict(list)
            for d in all_dates:
                months[d.month].append(d)

            for month in sorted(months.keys()):
                month_dates = months[month]
                if times_per >= len(month_dates):
                    target_dates.extend(month_dates)
                else:
                    step = len(month_dates) / times_per
                    for i in range(times_per):
                        idx = int(i * step)
                        if idx < len(month_dates):
                            target_dates.append(month_dates[idx])

        return target_dates

    def schedule(self):
        """Main scheduling loop. Process activities by priority (id order)."""
        sorted_activities = sorted(self.action_plan, key=lambda a: a["id"])

        scheduled_plan = []  
        skipped = []

        for activity in sorted_activities:
            target_dates = self._get_dates_for_period(activity)

            for target_date in target_dates:
                date_str = target_date.strftime("%Y-%m-%d")
                travel_info = self._get_travel_info(date_str)
                notes = ""

                if travel_info:
                    if not self._activity_possible_while_traveling(activity, travel_info):
                        backup = activity.get("backup_activities", [])
                        if backup and activity.get("remote_possible"):
                            notes = f"Traveling to {travel_info['destination']}. Use backup: {backup[0]}"
                        else:
                            skipped.append({
                                "date": date_str,
                                "activity": activity["name"],
                                "reason": f"Traveling to {travel_info['destination']} - not feasible",
                                "adjustment": activity.get("skip_adjustments", "")
                            })
                            continue

                available_windows = self._check_resource_availability(activity, date_str)

                if available_windows is None:
                    if activity.get("remote_possible") and (activity.get("facilitator") or activity.get("specialist") or activity.get("allied_health")):
                        client_windows = self.client_schedule.get(date_str, [])
                        if client_windows:
                            available_windows = self._get_available_windows(date_str, client_windows)
                            notes += " [Remote/async - provider unavailable]"
                        else:
                            skipped.append({
                                "date": date_str,
                                "activity": activity["name"],
                                "reason": "No client availability",
                                "adjustment": activity.get("skip_adjustments", "")
                            })
                            continue
                    else:
                        reason_parts = []
                        if activity.get("facilitator"):
                            fac_w = self.facilitator_schedules.get(activity["facilitator"], {}).get(date_str, [])
                            if not fac_w:
                                reason_parts.append(f"Facilitator {activity['facilitator']} unavailable")
                        if activity.get("specialist"):
                            spec_w = self.specialist_schedules.get(activity["specialist"], {}).get(date_str, [])
                            if not spec_w:
                                reason_parts.append(f"Specialist {activity['specialist']} unavailable")
                        if activity.get("allied_health"):
                            ah_w = self.allied_health_schedules.get(activity["allied_health"], {}).get(date_str, [])
                            if not ah_w:
                                reason_parts.append(f"Allied health {activity['allied_health']} unavailable")
                        for eq in activity.get("equipment", []):
                            eq_w = self.equipment_availability.get(eq, {}).get(date_str, [])
                            if not eq_w:
                                reason_parts.append(f"Equipment {eq} unavailable")

                        skipped.append({
                            "date": date_str,
                            "activity": activity["name"],
                            "reason": "; ".join(reason_parts) if reason_parts else "No overlapping availability",
                            "adjustment": activity.get("skip_adjustments", "")
                        })
                        continue

                preferred = activity.get("preferred_time", "09:00")
                duration = activity.get("duration_min", 30)
                slot_start = self._find_slot(date_str, duration, preferred, available_windows)

                if slot_start is None:
                    skipped.append({
                        "date": date_str,
                        "activity": activity["name"],
                        "reason": "No slot large enough found",
                        "adjustment": activity.get("skip_adjustments", "")
                    })
                    continue

                slot_end = slot_start + duration

                self.scheduled[date_str].append((slot_start, slot_end, activity["id"]))

                if travel_info:
                    notes = f"Traveling: {travel_info['destination']}. " + notes

                scheduled_plan.append({
                    "date": date_str,
                    "day_of_week": target_date.strftime("%A"),
                    "start_time": self._minutes_to_time(slot_start),
                    "end_time": self._minutes_to_time(slot_end),
                    "activity_id": activity["id"],
                    "activity_name": activity["name"],
                    "activity_type": activity["type"],
                    "duration_min": duration,
                    "location": activity.get("location", ""),
                    "facilitator": activity.get("facilitator"),
                    "specialist": activity.get("specialist"),
                    "allied_health": activity.get("allied_health"),
                    "equipment": activity.get("equipment", []),
                    "prep": activity.get("prep"),
                    "details": activity.get("details", ""),
                    "metrics": activity.get("metrics", []),
                    "notes": notes.strip()
                })

        return scheduled_plan, skipped

    def format_calendar(self, scheduled_plan, skipped):
        """Format the scheduled plan as a readable calendar string."""
        lines = []
        lines.append("=" * 100)
        lines.append("PERSONALIZED HEALTH PLAN - July to September 2025")
        lines.append("=" * 100)

        by_date = defaultdict(list)
        for entry in scheduled_plan:
            by_date[entry["date"]].append(entry)

        skip_by_date = defaultdict(list)
        for entry in skipped:
            skip_by_date[entry["date"]].append(entry)

        total_scheduled = len(scheduled_plan)
        total_skipped = len(skipped)
        lines.append(f"\nSUMMARY: {total_scheduled} activities scheduled, {total_skipped} skipped/rescheduled")
        lines.append("")

        type_counts = defaultdict(int)
        for entry in scheduled_plan:
            type_counts[entry["activity_type"]] += 1
        lines.append("ACTIVITY BREAKDOWN:")
        for atype, count in sorted(type_counts.items(), key=lambda x: -x[1]):
            lines.append(f"  {atype}: {count}")
        lines.append("")

        d = self.start_date
        current_week = None
        current_month = None

        while d <= self.end_date:
            ds = d.strftime("%Y-%m-%d")

            if d.month != current_month:
                current_month = d.month
                lines.append("")
                lines.append("=" * 100)
                lines.append(f"  {d.strftime('%B %Y').upper()}")
                lines.append("=" * 100)

            week_num = d.isocalendar()[1]
            if week_num != current_week:
                current_week = week_num
                lines.append("")
                lines.append(f"  ── Week {week_num} ──")

            day_events = sorted(by_date.get(ds, []), key=lambda x: x["start_time"])
            day_skips = skip_by_date.get(ds, [])

            travel = self._get_travel_info(ds)
            travel_tag = f"  ✈️  TRAVELING: {travel['destination']}" if travel else ""

            if day_events or day_skips:
                lines.append("")
                lines.append(f"  📅 {d.strftime('%A, %B %d')}{travel_tag}")
                lines.append(f"  {'─' * 80}")

                for ev in day_events:
                    icon = {
                        "Fitness routine": "🏋️",
                        "Food consumption": "🍽️",
                        "Medication consumption": "💊",
                        "Therapy": "🧘",
                        "Consultation": "👨‍⚕️",
                    }.get(ev["activity_type"], "📌")

                    people = []
                    if ev.get("facilitator"):
                        people.append(f"w/ {ev['facilitator']}")
                    if ev.get("specialist"):
                        people.append(f"w/ {ev['specialist']}")
                    if ev.get("allied_health"):
                        people.append(f"w/ {ev['allied_health']}")
                    people_str = f" ({', '.join(people)})" if people else ""

                    note_str = f" ⚠️ {ev['notes']}" if ev.get("notes") else ""

                    lines.append(
                        f"    {ev['start_time']}-{ev['end_time']}  {icon} {ev['activity_name']}"
                        f"  [{ev['duration_min']}min @ {ev['location']}]{people_str}{note_str}"
                    )

                if day_skips:
                    lines.append(f"    {'·' * 60}")
                    for sk in day_skips:
                        lines.append(
                            f"    ❌ SKIPPED: {sk['activity']} - {sk['reason']}"
                        )
                        if sk.get("adjustment"):
                            lines.append(f"       ↪ Adjustment: {sk['adjustment']}")

            d += timedelta(days=1)

        lines.append("")
        lines.append("=" * 100)
        lines.append("SKIPPED ACTIVITIES SUMMARY")
        lines.append("=" * 100)
        skip_counts = defaultdict(int)
        skip_reasons = defaultdict(list)
        for sk in skipped:
            skip_counts[sk["activity"]] += 1
            if sk["reason"] not in skip_reasons[sk["activity"]]:
                skip_reasons[sk["activity"]].append(sk["reason"])

        for act_name, count in sorted(skip_counts.items(), key=lambda x: -x[1])[:20]:
            lines.append(f"  {act_name}: skipped {count} times")
            for reason in skip_reasons[act_name][:3]:
                lines.append(f"    - {reason}")

        return "\n".join(lines)