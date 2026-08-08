"""Export the current PerformanceLab training plan to a text file."""

from collections import defaultdict
from datetime import date, datetime, timedelta
import json
from pathlib import Path


OUTPUT_PATH = Path("PLANO_DE_TREINO.txt")


def parse_day(value: str) -> date:
    return datetime.fromisoformat(value).date()


def monday(day: date) -> date:
    return day - timedelta(days=day.weekday())


athlete_files = sorted(
    Path("data/athletes").glob("*.json")
)

if not athlete_files:
    raise SystemExit(
        "No athlete file found in data/athletes."
    )

athlete_path = athlete_files[0]

with athlete_path.open(encoding="utf-8") as source:
    athlete_data = json.load(source)

plan = athlete_data.get("training_plan") or {}
workouts = plan.get("workouts") or []

lines = [
    "TRAINING PLAN",
    f"Start: {plan.get('start_date')}",
    f"End: {plan.get('end_date')}",
    f"Total workouts: {len(workouts)}",
    "",
]

weekly = defaultdict(
    lambda: {"sessions": 0, "minutes": 0}
)
training_days = []

for workout in workouts:
    scheduled_at = workout.get("scheduled_at")

    if not scheduled_at:
        continue

    workout_day = parse_day(scheduled_at)
    training_days.append(workout_day)

    duration_seconds = workout.get("duration") or 0
    duration_minutes = round(duration_seconds / 60)

    lines.append(
        " | ".join(
            (
                workout_day.isoformat(),
                str(workout.get("phase") or "—"),
                str(workout.get("sport") or "—"),
                str(workout.get("title") or "—"),
                f"{duration_minutes} min",
                str(workout.get("intensity") or "—"),
            )
        )
    )

    for step in workout.get("structure") or ():
        lines.append(f"  - {step}")

    objective = workout.get("objective")

    if objective:
        lines.append(f"  Objective: {objective}")

    lines.append("")

    week_start = monday(workout_day)
    weekly[week_start]["sessions"] += 1
    weekly[week_start]["minutes"] += duration_minutes

lines.extend(
    (
        "WEEKLY SUMMARY",
        "",
    )
)

for week_start in sorted(weekly):
    week_end = week_start + timedelta(days=6)
    values = weekly[week_start]

    lines.append(
        f"{week_start} – {week_end} | "
        f"{values['sessions']} workouts | "
        f"{values['minutes']} min"
    )

lines.extend(
    (
        "",
        "TRAINING SEQUENCES",
        "",
    )
)

unique_days = sorted(set(training_days))
sequences = []

if unique_days:
    sequence_start = unique_days[0]
    previous_day = unique_days[0]

    for workout_day in unique_days[1:]:
        if workout_day == previous_day + timedelta(days=1):
            previous_day = workout_day
            continue

        sequence_length = (
            previous_day - sequence_start
        ).days + 1

        if sequence_length > 2:
            sequences.append(
                (
                    sequence_start,
                    previous_day,
                    sequence_length,
                )
            )

        sequence_start = workout_day
        previous_day = workout_day

    sequence_length = (
        previous_day - sequence_start
    ).days + 1

    if sequence_length > 2:
        sequences.append(
            (
                sequence_start,
                previous_day,
                sequence_length,
            )
        )

if sequences:
    for start, end, length in sequences:
        lines.append(
            f"WARNING: {start} – {end} | "
            f"{length} consecutive days"
        )
else:
    lines.append(
        "No sequence longer than two days."
    )

OUTPUT_PATH.write_text(
    "\n".join(lines) + "\n",
    encoding="utf-8-sig",
)

print(
    f"Created: {OUTPUT_PATH.resolve()}"
)