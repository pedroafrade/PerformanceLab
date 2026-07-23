"""
Tests for CoachReviewer.
"""

from performancelab.coaching.availability import (
    AthleteAvailability,
    Weekday,
)
from performancelab.coaching.constraints import (
    TrainingConstraints,
)
from performancelab.coaching.draft_slot import (
    DraftTrainingSlot,
)
from performancelab.coaching.preferences import (
    AthletePreferences,
)
from performancelab.coaching.reviewer import CoachReviewer
from performancelab.coaching.session_purpose import (
    SessionPurpose,
)
from performancelab.coaching.strategy import StrategyPlan


def valid_slots() -> tuple[DraftTrainingSlot, ...]:

    return (
        DraftTrainingSlot(
            weekday=Weekday.MONDAY,
            purpose=SessionPurpose.EASY,
            duration_minutes=45,
        ),
        DraftTrainingSlot(
            weekday=Weekday.TUESDAY,
            purpose=SessionPurpose.INTENSITY,
            duration_minutes=60,
        ),
        DraftTrainingSlot.rest(
            Weekday.WEDNESDAY,
        ),
        DraftTrainingSlot(
            weekday=Weekday.THURSDAY,
            purpose=SessionPurpose.EASY,
            duration_minutes=45,
        ),
        DraftTrainingSlot.rest(
            Weekday.FRIDAY,
        ),
        DraftTrainingSlot(
            weekday=Weekday.SATURDAY,
            purpose=SessionPurpose.LONG,
            duration_minutes=90,
        ),
        DraftTrainingSlot(
            weekday=Weekday.SUNDAY,
            purpose=SessionPurpose.RECOVERY,
            duration_minutes=30,
        ),
    )


def finding_codes(review) -> set[str]:

    return {
        finding.code
        for finding in review.findings
    }


def test_valid_structure_receives_perfect_review(
    strategy_plan: StrategyPlan,
    full_availability: AthleteAvailability,
) -> None:

    preferences = AthletePreferences(
        preferred_long_day=Weekday.SATURDAY,
        preferred_rest_days={
            Weekday.WEDNESDAY,
            Weekday.FRIDAY,
        },
        preferred_intensity_days={
            Weekday.TUESDAY,
        },
    )

    constraints = TrainingConstraints(
        max_weekly_minutes=360,
        max_session_minutes=120,
        max_weekday_minutes=90,
        max_weekend_minutes=120,
        max_consecutive_training_days=3,
        max_intensity_sessions=2,
        max_long_sessions=1,
        max_sessions_per_day=1,
        minimum_recovery_days=2,
        allow_double_sessions=False,
    )

    review = CoachReviewer().review(
        slots=valid_slots(),
        strategy_plan=strategy_plan,
        availability=full_availability,
        preferences=preferences,
        constraints=constraints,
    )

    assert review.valid is True
    assert review.score == 100

    assert review.consistency_score == 100
    assert review.recovery_score == 100
    assert review.availability_score == 100
    assert review.score == 100

    assert review.findings == ()

    assert "respects" in review.summary.lower()


def test_detects_missing_weekday(
    strategy_plan: StrategyPlan,
    full_availability: AthleteAvailability,
    default_preferences: AthletePreferences,
    default_constraints: TrainingConstraints,
) -> None:

    slots = tuple(
        slot
        for slot in valid_slots()
        if slot.weekday is not Weekday.FRIDAY
    )

    review = CoachReviewer().review(
        slots=slots,
        strategy_plan=strategy_plan,
        availability=full_availability,
        preferences=default_preferences,
        constraints=default_constraints,
    )

    assert "missing_weekday" in finding_codes(review)
    assert review.valid is False
    assert review.consistency_score < 100


def test_detects_duplicate_weekday(
    strategy_plan: StrategyPlan,
    full_availability: AthleteAvailability,
    default_preferences: AthletePreferences,
    default_constraints: TrainingConstraints,
) -> None:

    slots = valid_slots() + (
        DraftTrainingSlot.rest(
            Weekday.MONDAY,
        ),
    )

    review = CoachReviewer().review(
        slots=slots,
        strategy_plan=strategy_plan,
        availability=full_availability,
        preferences=default_preferences,
        constraints=default_constraints,
    )

    assert "duplicate_weekday" in finding_codes(review)
    assert review.valid is False


def test_detects_training_when_unavailable(
    strategy_plan: StrategyPlan,
    default_preferences: AthletePreferences,
    default_constraints: TrainingConstraints,
) -> None:

    availability = AthleteAvailability.from_minutes(
        monday=0,
        tuesday=60,
        wednesday=60,
        thursday=60,
        friday=60,
        saturday=120,
        sunday=60,
    )

    review = CoachReviewer().review(
        slots=valid_slots(),
        strategy_plan=strategy_plan,
        availability=availability,
        preferences=default_preferences,
        constraints=default_constraints,
    )

    assert (
        "training_when_unavailable"
        in finding_codes(review)
    )

    assert review.availability_score < 100
    assert review.valid is False


def test_detects_duration_exceeding_availability(
    strategy_plan: StrategyPlan,
    default_preferences: AthletePreferences,
    default_constraints: TrainingConstraints,
) -> None:

    availability = AthleteAvailability.from_minutes(
        monday=30,
        tuesday=60,
        wednesday=60,
        thursday=60,
        friday=60,
        saturday=120,
        sunday=60,
    )

    review = CoachReviewer().review(
        slots=valid_slots(),
        strategy_plan=strategy_plan,
        availability=availability,
        preferences=default_preferences,
        constraints=default_constraints,
    )

    assert (
        "duration_exceeds_availability"
        in finding_codes(review)
    )

    assert review.availability_score < 100


def test_detects_training_on_blocked_day(
    strategy_plan: StrategyPlan,
    full_availability: AthleteAvailability,
    default_preferences: AthletePreferences,
) -> None:

    constraints = TrainingConstraints(
        blocked_days={
            Weekday.MONDAY,
        },
        max_weekly_minutes=420,
        max_session_minutes=120,
        max_weekday_minutes=90,
        max_weekend_minutes=120,
        max_consecutive_training_days=7,
        max_intensity_sessions=2,
        max_long_sessions=1,
        max_sessions_per_day=1,
        minimum_recovery_days=0,
        allow_double_sessions=False,
    )

    review = CoachReviewer().review(
        slots=valid_slots(),
        strategy_plan=strategy_plan,
        availability=full_availability,
        preferences=default_preferences,
        constraints=constraints,
    )

    assert (
        "training_on_blocked_day"
        in finding_codes(review)
    )

    assert review.score < 100
    assert review.valid is False


def test_detects_intensity_on_prohibited_day(
    strategy_plan: StrategyPlan,
    full_availability: AthleteAvailability,
    default_preferences: AthletePreferences,
) -> None:

    constraints = TrainingConstraints(
        no_intensity_days={
            Weekday.TUESDAY,
        },
        max_weekly_minutes=420,
        max_session_minutes=120,
        max_weekday_minutes=90,
        max_weekend_minutes=120,
        max_consecutive_training_days=7,
        max_intensity_sessions=2,
        max_long_sessions=1,
        max_sessions_per_day=1,
        minimum_recovery_days=0,
        allow_double_sessions=False,
    )

    review = CoachReviewer().review(
        slots=valid_slots(),
        strategy_plan=strategy_plan,
        availability=full_availability,
        preferences=default_preferences,
        constraints=constraints,
    )

    assert (
        "intensity_not_allowed"
        in finding_codes(review)
    )

    assert review.recovery_score < 100


def test_detects_duration_exceeding_daily_constraint(
    strategy_plan: StrategyPlan,
    full_availability: AthleteAvailability,
    default_preferences: AthletePreferences,
) -> None:

    constraints = TrainingConstraints(
        max_weekly_minutes=420,
        max_session_minutes=40,
        max_weekday_minutes=40,
        max_weekend_minutes=80,
        max_consecutive_training_days=7,
        max_intensity_sessions=2,
        max_long_sessions=1,
        max_sessions_per_day=1,
        minimum_recovery_days=0,
        allow_double_sessions=False,
    )

    review = CoachReviewer().review(
        slots=valid_slots(),
        strategy_plan=strategy_plan,
        availability=full_availability,
        preferences=default_preferences,
        constraints=constraints,
    )

    assert (
        "duration_exceeds_constraint"
        in finding_codes(review)
    )

    assert review.score < 100


def test_detects_weekly_duration_limit(
    strategy_plan: StrategyPlan,
    full_availability: AthleteAvailability,
    default_preferences: AthletePreferences,
) -> None:

    constraints = TrainingConstraints(
        max_weekly_minutes=200,
        max_session_minutes=120,
        max_weekday_minutes=90,
        max_weekend_minutes=120,
        max_consecutive_training_days=7,
        max_intensity_sessions=2,
        max_long_sessions=1,
        max_sessions_per_day=1,
        minimum_recovery_days=0,
        allow_double_sessions=False,
    )

    review = CoachReviewer().review(
        slots=valid_slots(),
        strategy_plan=strategy_plan,
        availability=full_availability,
        preferences=default_preferences,
        constraints=constraints,
    )

    assert (
        "weekly_duration_exceeded"
        in finding_codes(review)
    )

    assert review.score < 100


def test_detects_too_many_intensity_sessions(
    strategy_plan: StrategyPlan,
    full_availability: AthleteAvailability,
    default_preferences: AthletePreferences,
) -> None:

    slots = list(valid_slots())

    slots[3] = DraftTrainingSlot(
        weekday=Weekday.THURSDAY,
        purpose=SessionPurpose.INTENSITY,
        duration_minutes=45,
    )

    constraints = TrainingConstraints(
        max_weekly_minutes=420,
        max_session_minutes=120,
        max_weekday_minutes=90,
        max_weekend_minutes=120,
        max_consecutive_training_days=7,
        max_intensity_sessions=1,
        max_long_sessions=1,
        max_sessions_per_day=1,
        minimum_recovery_days=0,
        allow_double_sessions=False,
    )

    review = CoachReviewer().review(
        slots=tuple(slots),
        strategy_plan=strategy_plan,
        availability=full_availability,
        preferences=default_preferences,
        constraints=constraints,
    )

    assert (
        "too_many_intensity_sessions"
        in finding_codes(review)
    )


def test_detects_too_many_long_sessions(
    strategy_plan: StrategyPlan,
    full_availability: AthleteAvailability,
    default_preferences: AthletePreferences,
) -> None:

    slots = list(valid_slots())

    slots[3] = DraftTrainingSlot(
        weekday=Weekday.THURSDAY,
        purpose=SessionPurpose.LONG,
        duration_minutes=45,
    )

    constraints = TrainingConstraints(
        max_weekly_minutes=420,
        max_session_minutes=120,
        max_weekday_minutes=90,
        max_weekend_minutes=120,
        max_consecutive_training_days=7,
        max_intensity_sessions=2,
        max_long_sessions=1,
        max_sessions_per_day=1,
        minimum_recovery_days=0,
        allow_double_sessions=False,
    )

    review = CoachReviewer().review(
        slots=tuple(slots),
        strategy_plan=strategy_plan,
        availability=full_availability,
        preferences=default_preferences,
        constraints=constraints,
    )

    assert (
        "too_many_long_sessions"
        in finding_codes(review)
    )


def test_detects_consecutive_training_day_limit(
    strategy_plan: StrategyPlan,
    full_availability: AthleteAvailability,
    default_preferences: AthletePreferences,
) -> None:

    slots = tuple(
        DraftTrainingSlot(
            weekday=weekday,
            purpose=SessionPurpose.EASY,
            duration_minutes=30,
        )
        for weekday in Weekday
    )

    constraints = TrainingConstraints(
        max_weekly_minutes=420,
        max_session_minutes=120,
        max_weekday_minutes=90,
        max_weekend_minutes=120,
        max_consecutive_training_days=3,
        max_intensity_sessions=2,
        max_long_sessions=1,
        max_sessions_per_day=1,
        minimum_recovery_days=0,
        allow_double_sessions=False,
    )

    review = CoachReviewer().review(
        slots=slots,
        strategy_plan=strategy_plan,
        availability=full_availability,
        preferences=default_preferences,
        constraints=constraints,
    )

    assert (
        "consecutive_days_exceeded"
        in finding_codes(review)
    )

    assert review.recovery_score < 100


def test_detects_insufficient_recovery_days(
    strategy_plan: StrategyPlan,
    full_availability: AthleteAvailability,
    default_preferences: AthletePreferences,
) -> None:

    slots = tuple(
        DraftTrainingSlot(
            weekday=weekday,
            purpose=SessionPurpose.EASY,
            duration_minutes=30,
        )
        for weekday in Weekday
    )

    constraints = TrainingConstraints(
        max_weekly_minutes=420,
        max_session_minutes=120,
        max_weekday_minutes=90,
        max_weekend_minutes=120,
        max_consecutive_training_days=7,
        max_intensity_sessions=2,
        max_long_sessions=1,
        max_sessions_per_day=1,
        minimum_recovery_days=2,
        allow_double_sessions=False,
    )

    review = CoachReviewer().review(
        slots=slots,
        strategy_plan=strategy_plan,
        availability=full_availability,
        preferences=default_preferences,
        constraints=constraints,
    )

    assert (
        "insufficient_recovery_days"
        in finding_codes(review)
    )

    assert review.recovery_score < 100


def test_long_day_preference_is_informational(
    strategy_plan: StrategyPlan,
    full_availability: AthleteAvailability,
    default_constraints: TrainingConstraints,
) -> None:

    preferences = AthletePreferences(
        preferred_long_day=Weekday.SUNDAY,
    )

    review = CoachReviewer().review(
        slots=valid_slots(),
        strategy_plan=strategy_plan,
        availability=full_availability,
        preferences=preferences,
        constraints=default_constraints,
    )

    assert (
        "long_day_preference_not_met"
        in finding_codes(review)
    )

    assert review.valid is True


def test_preferred_rest_day_is_informational(
    strategy_plan: StrategyPlan,
    full_availability: AthleteAvailability,
    default_constraints: TrainingConstraints,
) -> None:

    preferences = AthletePreferences(
        preferred_rest_days={
            Weekday.MONDAY,
        },
    )

    review = CoachReviewer().review(
        slots=valid_slots(),
        strategy_plan=strategy_plan,
        availability=full_availability,
        preferences=preferences,
        constraints=default_constraints,
    )

    assert (
        "rest_preference_not_met"
        in finding_codes(review)
    )

    assert review.valid is True


def test_review_summary_reports_findings(
    strategy_plan: StrategyPlan,
    full_availability: AthleteAvailability,
    default_preferences: AthletePreferences,
) -> None:

    constraints = TrainingConstraints(
        blocked_days={
            Weekday.MONDAY,
        },
        max_weekly_minutes=200,
        max_session_minutes=120,
        max_weekday_minutes=90,
        max_weekend_minutes=120,
        max_consecutive_training_days=2,
        max_intensity_sessions=0,
        max_long_sessions=0,
        max_sessions_per_day=1,
        minimum_recovery_days=3,
        allow_double_sessions=False,
    )

    review = CoachReviewer().review(
        slots=valid_slots(),
        strategy_plan=strategy_plan,
        availability=full_availability,
        preferences=default_preferences,
        constraints=constraints,
    )

    assert "errors" in review.summary
    assert "warnings" in review.summary
    assert "informational observations" in review.summary