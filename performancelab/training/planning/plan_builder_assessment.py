"""Central safety assessment for Plan Builder draft changes."""

from dataclasses import dataclass
from datetime import date, timedelta

from performancelab.training.load import planned_workout_load


@dataclass(frozen=True, slots=True)
class PlanBuilderAssessment:
    status: str
    messages: tuple[str, ...]
    recommendations: tuple[str, ...]
    changed_sessions: int
    load_difference: float
    weekly_load_changes: tuple[tuple[date, float, float, float | None], ...]

    @property
    def blocked(self) -> bool:
        return self.status == "blocked"


def _is_demanding(workout) -> bool:
    text = " ".join(
        str(value or "")
        for value in (
            workout.title,
            workout.intensity,
            workout.focus,
        )
    ).lower()
    return any(
        token in text
        for token in (
            "tempo",
            "threshold",
            "lt2",
            "hill",
            "interval",
            "vo2",
            "speed",
            "hard",
        )
    )


def _is_race(workout) -> bool:
    return str(workout.intensity or "").strip().lower() == "race effort"


def _load(workouts) -> float:
    return sum(float(planned_workout_load(item) or 0.0) for item in workouts)


def assess_plan_builder_change(
    *,
    baseline_workouts,
    revised_workouts,
    reference_day: date,
) -> PlanBuilderAssessment:
    """Classifies one complete draft as safe, warning or blocked."""
    baseline = tuple(baseline_workouts)
    revised = tuple(revised_workouts)
    baseline_by_id = {item.planned_workout_id: item for item in baseline}
    revised_by_id = {item.planned_workout_id: item for item in revised}
    changed_ids = {
        workout_id
        for workout_id in baseline_by_id.keys() | revised_by_id.keys()
        if baseline_by_id.get(workout_id) != revised_by_id.get(workout_id)
    }

    warnings = []
    blockers = []
    recommendations = []
    future = tuple(item for item in revised if item.day >= reference_day)
    demanding = tuple(sorted(
        (item for item in future if _is_demanding(item) and not _is_race(item)),
        key=lambda item: item.scheduled_at,
    ))
    for previous, following in zip(demanding, demanding[1:]):
        if (following.day - previous.day).days < 2:
            warnings.append(
                f"{previous.title} and {following.title} leave less than "
                "48 hours of recovery."
            )
            recommendations.append(
                "Move one demanding session or reduce its duration or intensity."
            )

    race_days = tuple(item.day for item in future if _is_race(item))
    for workout in demanding:
        if any(timedelta(0) < race_day - workout.day <= timedelta(days=1) for race_day in race_days):
            blockers.append(
                f"{workout.title} is too close to a race and would compromise taper."
            )
            recommendations.append(
                f"Move {workout.title} earlier or replace it with an easy session."
            )

    long_runs = tuple(
        item
        for item in future
        if "long" in str(item.title or "").lower()
        and not _is_race(item)
    )
    for long_run in long_runs:
        if any(
            item.planned_workout_id != long_run.planned_workout_id
            and abs((item.day - long_run.day).days) < 2
            for item in demanding
        ):
            warnings.append(
                f"{long_run.title} is less than 48 hours from a demanding session."
            )
            recommendations.append(
                "Keep at least one easy or rest day around the long session."
            )

    baseline_weeks = {}
    revised_weeks = {}
    for collection, totals in ((baseline, baseline_weeks), (revised, revised_weeks)):
        for workout in collection:
            if workout.day < reference_day or _is_race(workout):
                continue
            week = workout.day - timedelta(days=workout.day.weekday())
            totals[week] = totals.get(week, 0.0) + float(
                planned_workout_load(workout) or 0.0
            )
    weekly_load_changes = []
    for week in sorted(baseline_weeks.keys() | revised_weeks.keys()):
        revised_load = revised_weeks.get(week, 0.0)
        baseline_load = baseline_weeks.get(week, 0.0)
        growth = (
            (revised_load - baseline_load) / baseline_load
            if baseline_load > 0
            else None
        )
        if revised_load != baseline_load:
            weekly_load_changes.append(
                (week, baseline_load, revised_load, growth)
            )
        if baseline_load <= 0:
            continue
        if growth > 0.35:
            blockers.append(
                f"Weekly load from {week:%d %b} increases by more than 35%."
            )
            recommendations.append(
                "Move load to another compatible week or reduce duration or intensity."
            )
        elif growth > 0.20:
            warnings.append(
                f"Weekly load from {week:%d %b} increases by more than 20%."
            )
            recommendations.append(
                "Consider reducing the added load or increasing recovery in that week."
            )

    status = "blocked" if blockers else "warning" if warnings else "safe"
    return PlanBuilderAssessment(
        status=status,
        messages=tuple(dict.fromkeys((*blockers, *warnings))),
        recommendations=tuple(dict.fromkeys(recommendations)),
        changed_sessions=len(changed_ids),
        load_difference=_load(revised) - _load(baseline),
        weekly_load_changes=tuple(weekly_load_changes),
    )
