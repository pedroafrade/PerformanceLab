"""Central safety assessment for Plan Builder draft changes."""

from dataclasses import dataclass, replace
from datetime import date, datetime, timedelta

from performancelab.training.load import planned_workout_load


@dataclass(frozen=True, slots=True)
class PlanBuilderIssue:
    severity: str
    rule: str
    message: str
    workout_ids: tuple[str, ...] = ()
    week: date | None = None


@dataclass(frozen=True, slots=True)
class PlanBuilderAlternative:
    workout_id: str
    target_day: date
    reason: str


@dataclass(frozen=True, slots=True)
class PlanBuilderAssessment:
    status: str
    messages: tuple[str, ...]
    recommendations: tuple[str, ...]
    changed_sessions: int
    load_difference: float
    weekly_load_changes: tuple[tuple[date, float, float, float | None], ...]
    issues: tuple[PlanBuilderIssue, ...]
    alternatives: tuple[PlanBuilderAlternative, ...]

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


def _weekly_loads(workouts, reference_day):
    totals = {}
    for workout in workouts:
        if workout.day < reference_day or _is_race(workout):
            continue
        week = workout.day - timedelta(days=workout.day.weekday())
        totals[week] = totals.get(week, 0.0) + float(
            planned_workout_load(workout) or 0.0
        )
    return totals


def _load_rule(baseline_load, revised_load):
    difference = revised_load - baseline_load
    if difference <= 0:
        return None
    if baseline_load <= 0:
        if difference >= 150.0:
            return "blocked"
        if difference >= 75.0:
            return "caution"
        return "information"
    growth = difference / baseline_load
    if growth > 0.35 and difference >= 100.0:
        return "blocked"
    if growth > 0.20 and difference >= 50.0:
        return "caution"
    return "information" if growth > 0.20 else None


def _safe_move_alternative(
    *, workout, revised, baseline_weeks, reference_day,
):
    occupied = {item.day for item in revised if item is not workout}
    for distance in range(1, 8):
        for direction in (-1, 1):
            candidate = workout.day + timedelta(days=distance * direction)
            if candidate < reference_day or candidate in occupied:
                continue
            if any(
                abs((item.day - candidate).days) < 2
                and (
                    _is_race(item)
                    or _is_demanding(item)
                    or "long" in str(item.title or "").lower()
                )
                for item in revised
                if item is not workout
            ):
                continue
            moved_workout = replace(
                workout,
                scheduled_at=datetime.combine(
                    candidate, workout.scheduled_at.time()
                ),
            )
            moved = tuple(
                moved_workout if item is workout else item
                for item in revised
            )
            candidate_weeks = _weekly_loads(moved, reference_day)
            if any(
                _load_rule(baseline_weeks.get(week, 0.0), load) == "blocked"
                for week, load in candidate_weeks.items()
            ):
                continue
            return PlanBuilderAlternative(
                workout_id=workout.planned_workout_id,
                target_day=candidate,
                reason="Restores recovery spacing and keeps weekly load within limits.",
            )
    return None


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
    information = []
    issues = []
    recommendations = []
    future = tuple(item for item in revised if item.day >= reference_day)
    demanding = tuple(sorted(
        (item for item in future if _is_demanding(item) and not _is_race(item)),
        key=lambda item: item.scheduled_at,
    ))
    for previous, following in zip(demanding, demanding[1:]):
        if (following.day - previous.day).days < 2:
            message = (
                f"{previous.title} and {following.title} leave less than "
                "48 hours of recovery."
            )
            warnings.append(message)
            issues.append(PlanBuilderIssue(
                severity="caution", rule="demanding_recovery",
                message=message,
                workout_ids=(previous.planned_workout_id, following.planned_workout_id),
            ))
            recommendations.append(
                "Move one demanding session or reduce its duration or intensity."
            )

    race_days = tuple(item.day for item in future if _is_race(item))
    for workout in demanding:
        if any(timedelta(0) < race_day - workout.day <= timedelta(days=1) for race_day in race_days):
            message = f"{workout.title} is too close to a race and would compromise taper."
            blockers.append(message)
            issues.append(PlanBuilderIssue(
                severity="blocked", rule="race_taper", message=message,
                workout_ids=(workout.planned_workout_id,),
            ))
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
            message = f"{long_run.title} is less than 48 hours from a demanding session."
            warnings.append(message)
            issues.append(PlanBuilderIssue(
                severity="caution", rule="long_run_recovery", message=message,
                workout_ids=(long_run.planned_workout_id,),
            ))
            recommendations.append(
                "Keep at least one easy or rest day around the long session."
            )

    baseline_weeks = _weekly_loads(baseline, reference_day)
    revised_weeks = _weekly_loads(revised, reference_day)
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
        severity = _load_rule(baseline_load, revised_load)
        growth_label = f"{growth:+.0%}" if growth is not None else "new load"
        if severity == "blocked":
            message = (
                f"Weekly load from {week:%d %b} increases from "
                f"{baseline_load:.0f} to {revised_load:.0f} AU "
                f"({growth_label}, {revised_load - baseline_load:+.0f} AU)."
            )
            blockers.append(message)
            issues.append(PlanBuilderIssue(
                severity="blocked", rule="weekly_load", message=message,
                week=week,
            ))
            recommendations.append(
                "Move load to another compatible week or reduce duration or intensity."
            )
        elif severity == "caution":
            message = (
                f"Weekly load from {week:%d %b} increases from "
                f"{baseline_load:.0f} to {revised_load:.0f} AU "
                f"({growth_label}, {revised_load - baseline_load:+.0f} AU)."
            )
            warnings.append(message)
            issues.append(PlanBuilderIssue(
                severity="caution", rule="weekly_load", message=message,
                week=week,
            ))
            recommendations.append(
                "Consider reducing the added load or increasing recovery in that week."
            )
        elif severity == "information":
            message = (
                f"Weekly load from {week:%d %b} changes by "
                f"{growth_label}, but only {revised_load - baseline_load:+.0f} AU."
            )
            information.append(message)
            issues.append(PlanBuilderIssue(
                severity="information", rule="weekly_load", message=message,
                week=week,
            ))

    status = "blocked" if blockers else "warning" if warnings else "safe"
    alternatives = []
    if blockers:
        for workout_id in changed_ids:
            workout = revised_by_id.get(workout_id)
            if workout is None or not _is_demanding(workout) or _is_race(workout):
                continue
            alternative = _safe_move_alternative(
                workout=workout,
                revised=revised,
                baseline_weeks=baseline_weeks,
                reference_day=reference_day,
            )
            if alternative is not None:
                alternatives.append(alternative)
    return PlanBuilderAssessment(
        status=status,
        messages=tuple(dict.fromkeys((*blockers, *warnings, *information))),
        recommendations=tuple(dict.fromkeys(recommendations)),
        changed_sessions=len(changed_ids),
        load_difference=_load(revised) - _load(baseline),
        weekly_load_changes=tuple(weekly_load_changes),
        issues=tuple(issues),
        alternatives=tuple(alternatives),
    )
