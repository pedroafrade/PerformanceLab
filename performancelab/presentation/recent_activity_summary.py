"""Read-only, inclusive 30-day totals shared by Development and Dashboard."""
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from math import isfinite


@dataclass(frozen=True)
class RecentActivitySummary:
    workouts: int
    training_days: int
    sports: int
    total_duration: timedelta
    running_distance: float | None
    cycling_distance: float | None
    running_missing: int
    cycling_missing: int


def recent_activity_summary(history, reference_day: date) -> RecentActivitySummary:
    start = reference_day - timedelta(days=29)
    days, sports = set(), set()
    sessions = 0
    duration = timedelta()
    totals = {"Running": 0.0, "Cycling": 0.0}
    valid = {"Running": 0, "Cycling": 0}
    missing = {"Running": 0, "Cycling": 0}
    for workout in history:
        day = workout.date
        if isinstance(day, datetime):
            day = day.date()
        if not isinstance(day, date) or not start <= day <= reference_day:
            continue
        sessions += 1
        days.add(day)
        sport = str(workout.sport or "Other").strip()
        sports.add(sport)
        if isinstance(workout.duration, timedelta) and workout.duration >= timedelta():
            duration += workout.duration
        normalized = sport.lower()
        group = ("Running" if any(s in normalized for s in ("run", "trail", "jog"))
                 else "Cycling" if any(s in normalized for s in ("cycl", "bike", "bicycle"))
                 else None)
        if group is None:
            continue
        try:
            distance = float(workout.distance)
        except (TypeError, ValueError):
            distance = float("nan")
        if not isfinite(distance) or distance < 0:
            missing[group] += 1
        else:
            valid[group] += 1
            totals[group] += distance
    def distance(group):
        return None if missing[group] and not valid[group] else totals[group]
    return RecentActivitySummary(sessions, len(days), len(sports), duration,
                                 distance("Running"), distance("Cycling"),
                                 missing["Running"], missing["Cycling"])
