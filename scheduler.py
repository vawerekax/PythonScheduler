#!/usr/bin/env python3
import csv
import argparse
import itertools
import matplotlib.pyplot as plt
import os
from datetime import datetime, time

DAYS = ["MON", "TUE", "WED", "THU", "FRI"]
DAY_INDEX = {day: i for i, day in enumerate(DAYS)}

def parse_time(time_str):
    """Converts a HH:MM string into a time object."""
    return datetime.strptime(time_str, "%H:%M").time()

def parse_session(session_str):
    """
    Parses a session string in the format "DAY HH:MM-HH:MM".
    Returns a dictionary with day, start, and end if the string is non-empty;
    otherwise, returns None.
    """
    session_str = session_str.strip()
    if not session_str:
        return None
    try:
        parts = session_str.split()
        # Expecting something like: ["TUE", "13:00-15:00"]
        if len(parts) != 2:
            raise ValueError("Session format error, expected a day and a time range.")
        day = parts[0].upper()
        start_str, end_str = parts[1].split("-")
        return {"day": day, "start": parse_time(start_str), "end": parse_time(end_str)}
    except Exception as e:
        raise ValueError(f"Error parsing session '{session_str}': {e}")

def load_classes(csv_file):
    """
    Loads classes from a CSV file with columns: name,date1,date2,location.
    Each row becomes a dictionary with name, location, and a list containing
    one session group (which includes 1 or 2 sessions to be taken together).
    """
    classes = []
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, fieldnames=["name", "date1", "date2", "location", "credits"])
        for row in reader:
            if row["name"].strip().lower() == "name":
                continue

            name = row["name"].strip()
            location = row["location"].strip()
            credits = int(row["credits"].strip())

            session1 = parse_session(row["date1"])
            session2 = parse_session(row["date2"])

            sessions = []
            if session1:
                sessions.append(session1)
            if session2:
                sessions.append(session2)

            classes.append({
                "name": name,
                "location": location,
                "credits": credits,
                "sessions": sessions
            })
    return classes


def time_to_minutes(t):
    """Converts a time object to minutes since midnight."""
    return t.hour * 60 + t.minute

def overlap_minutes(session1, session2):
    """
    Given two session dictionaries (with 'start' and 'end'),
    returns the overlap duration in minutes if they are on the same day.
    """
    start1 = time_to_minutes(session1["start"])
    end1 = time_to_minutes(session1["end"])
    start2 = time_to_minutes(session2["start"])
    end2 = time_to_minutes(session2["end"])
    latest_start = max(start1, start2)
    earliest_end = min(end1, end2)
    return max(0, earliest_end - latest_start)

def is_valid_schedule(schedule, blocked_days, allowed_overlap=30, min_travel_gap=30):
    """
    Checks if a generated schedule is valid:
      - No sessions on blocked days.
      - Overlaps on the same day are within allowed limits.
      - Classes in different locations on the same day must be at least `min_travel_gap` apart.
    """
    sessions_by_day = {}
    for sess in schedule:
        day = sess["day"]
        if day in blocked_days:
            return False
        sessions_by_day.setdefault(day, []).append(sess)

    for day, sessions in sessions_by_day.items():
        # Check every pair of sessions on the same day
        for i in range(len(sessions)):
            for j in range(i + 1, len(sessions)):
                s1 = sessions[i]
                s2 = sessions[j]

                # Check time overlap
                overlap = overlap_minutes(s1, s2)
                if overlap > allowed_overlap:
                    return False

                # If locations are different, check travel time
                if s1["location"] != s2["location"]:
                    # Check time gap
                    end1 = time_to_minutes(s1["end"])
                    start2 = time_to_minutes(s2["start"])
                    end2 = time_to_minutes(s2["end"])
                    start1 = time_to_minutes(s1["start"])

                    # We check both directions since we don't know the session order
                    gap1 = start2 - end1
                    gap2 = start1 - end2

                    if (0 <= gap1 < min_travel_gap) or (0 <= gap2 < min_travel_gap):
                        return False

        # Check for the travel gap between more than 2 sessions in a day.
        for i in range(len(sessions)):
            for j in range(i + 1, len(sessions)):
                s1 = sessions[i]
                s2 = sessions[j]

                # Ensure that the time gap between all sessions is large enough if they are in different locations.
                if s1["location"] != s2["location"]:
                    end1 = time_to_minutes(s1["end"])
                    start2 = time_to_minutes(s2["start"])

                    gap = start2 - end1
                    if gap < min_travel_gap:
                        return False

    return True



def generate_schedules(classes, num_classes, blocked_days, include_classes):
    """
    Generates all valid schedules where classes with 2 dates include both.
    Each schedule is a combination of class session groups (1 or 2 sessions each).
    """
    valid_schedules = []
    for class_combo in itertools.combinations(classes, num_classes):
        class_names = [cls["name"] for cls in class_combo]

        # Skip this combo if it doesn't include all the required classes
        if not all(req in class_names for req in include_classes):
            continue

        total_credits = sum(cls["credits"] for cls in class_combo)
        if total_credits < 20:
            continue  # skip combinations that don't meet the credit requirement

        # Flatten all sessions (each class contributes all sessions in its group)
        schedule = []
        for cls in class_combo:
            for sess in cls["sessions"]:
                sess_data = sess.copy()
                sess_data["class_name"] = cls["name"]
                sess_data["location"] = cls["location"]
                schedule.append(sess_data)

        if is_valid_schedule(schedule, blocked_days):
            valid_schedules.append(schedule)
    return valid_schedules

def draw_schedule(schedule, index, output_folder="schedules"):
    """
    Draws and saves a visual schedule as an image using matplotlib.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_title(f"Schedule {index + 1}", fontsize=16)
    ax.set_xlim(0, 5)
    ax.set_ylim(8, 20)  # School day from 8AM to 8PM

    ax.set_xticks(range(5))
    ax.set_xticklabels(DAYS)
    ax.set_yticks(range(8, 21))
    ax.set_yticklabels([f"{h}:00" for h in range(8, 21)])
    ax.grid(True)

    for sess in schedule:
        day_idx = DAY_INDEX.get(sess["day"], -1)
        if day_idx == -1:
            continue
        start = sess["start"].hour + sess["start"].minute / 60
        end = sess["end"].hour + sess["end"].minute / 60
        duration = end - start

        rect = plt.Rectangle(
            (day_idx, start), 1, duration,
            color="skyblue", edgecolor="black", linewidth=1.5, alpha=0.8
        )
        ax.add_patch(rect)
        ax.text(
            day_idx + 0.5, start + duration / 2,
            f"{sess['class_name']}\n@{sess['location']}",
            ha="center", va="center", fontsize=8, wrap=True
        )

    ax.invert_yaxis()
    plt.tight_layout()
    plt.savefig(f"{output_folder}/schedule_{index + 1}.png")
    plt.close()

def main():
    parser = argparse.ArgumentParser(
        description="Generate all possible class schedules from a CSV file."
    )
    parser.add_argument("csv_file", help="Path to CSV file containing classes")
    parser.add_argument(
        "num_classes",
        type=int,
        help="Number of classes to include in each generated schedule",
    )
    parser.add_argument(
        "--block",
        nargs="*",
        default=[],
        help="List of days to block (e.g., MON TUE). Days should be abbreviated (e.g., MON, TUE, etc.)",
    )
    parser.add_argument(
        "--include",
        nargs="*",
        default=[],
        help="List of class names to forcibly include in all generated schedules"
    )
    args = parser.parse_args()

    # Blocked days should be stored in uppercase for consistency.
    blocked_days = [day.upper() for day in args.block]

    # Load classes from CSV.
    try:
        classes = load_classes(args.csv_file)
    except Exception as e:
        print(f"Error loading CSV file: {e}")
        return

    # Generate schedules using the given classes, number of classes to choose, and blocked days.
    schedules = generate_schedules(classes, args.num_classes, blocked_days, args.include)
    print(f"Found {len(schedules)} valid schedule(s).\n")

    # Optionally, print the generated schedules.
    for idx, sched in enumerate(schedules, start=1):
        print(f"Schedule {idx}:")
        for sess in sched:
            start = sess['start'].strftime("%H:%M")
            end = sess['end'].strftime("%H:%M")
            print(f"  {sess['class_name']} at {sess['location']} on {sess['day']} from {start} to {end}")
        print("")
        draw_schedule(sched, idx - 1)  # <- Add this to generate images


if __name__ == "__main__":
    main()
