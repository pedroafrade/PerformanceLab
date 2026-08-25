from datetime import datetime

from performancelab import (
    ActivityCoachInterpretation,
    ActivityCoachInterpretationBook,
    activity_coach_context_hash,
)
from performancelab.coaching import (
    ActivityCoachNarrative,
)


def create_narrative(
    *,
    recommendations="Recover prudently.",
):

    return ActivityCoachNarrative(
        measured_facts=(
            "Measured facts."
        ),
        deterministic_signals=(
            "Deterministic signals."
        ),
        prudent_interpretation=(
            "Prudent interpretation."
        ),
        recommendations=(
            recommendations
        ),
        data_limitations=(
            "Missing sleep data."
        ),
        provider="google-gemini",
        model="gemini-3.5-flash",
    )


def create_interpretation(
    *,
    context_hash="context-a",
    recommendations="Recover prudently.",
    generated_at=None,
):

    return ActivityCoachInterpretation(
        workout_id="workout-1",
        contract_version=(
            "activity-coach-v1"
        ),
        context_hash=context_hash,
        generated_at=(
            generated_at
            if generated_at is not None
            else datetime(
                2026,
                8,
                11,
                14,
                0,
            )
        ),
        narrative=create_narrative(
            recommendations=(
                recommendations
            )
        ),
    )

def test_context_hash_is_deterministic():

    first = activity_coach_context_hash(
        {
            "version": 1,
            "activity": {
                "load": 450.0,
            },
        }
    )

    second = activity_coach_context_hash(
        {
            "activity": {
                "load": 450.0,
            },
            "version": 1,
        }
    )

    assert first == second
    assert len(first) == 64


def test_finds_matching_interpretation():

    record = create_interpretation()

    book = (
        ActivityCoachInterpretationBook(
            records=(
                record,
            )
        )
    )

    found = book.find(
        workout_id="workout-1",
        contract_version=(
            "activity-coach-v1"
        ),
        context_hash="context-a",
    )

    assert found == record


def test_does_not_reuse_different_context():

    book = (
        ActivityCoachInterpretationBook(
            records=(
                create_interpretation(),
            )
        )
    )

    found = book.find(
        workout_id="workout-1",
        contract_version=(
            "activity-coach-v1"
        ),
        context_hash="context-b",
    )

    assert found is None


def test_replaces_same_interpretation_identity():

    book = (
        ActivityCoachInterpretationBook()
    )

    book.add(
        create_interpretation()
    )
    book.add(
        create_interpretation(
            recommendations=(
                "Updated recommendation."
            )
        )
    )

    assert len(book) == 1

    stored = book.find(
        workout_id="workout-1",
        contract_version=(
            "activity-coach-v1"
        ),
        context_hash="context-a",
    )

    assert stored is not None
    assert (
        stored.narrative.recommendations
        == "Updated recommendation."
    )


def test_replaces_older_context_for_same_workout():

    book = (
        ActivityCoachInterpretationBook()
    )

    book.add(
        create_interpretation(
            context_hash="context-a"
        )
    )

    newer = create_interpretation(
        context_hash="context-b",
        recommendations=(
            "Use the current context."
        ),
    )

    book.add(
        newer
    )

    assert len(book) == 1

    assert (
        book.find(
            workout_id="workout-1",
            contract_version=(
                "activity-coach-v1"
            ),
            context_hash="context-a",
        )
        is None
    )

    assert (
        book.find(
            workout_id="workout-1",
            contract_version=(
                "activity-coach-v1"
            ),
            context_hash="context-b",
        )
        == newer
    )


def test_finds_latest_interpretation_for_workout():

    older = create_interpretation(
        context_hash="context-old",
        generated_at=datetime(
            2026,
            8,
            10,
            12,
            0,
        ),
    )

    newer = create_interpretation(
        context_hash="context-new",
        generated_at=datetime(
            2026,
            8,
            12,
            12,
            0,
        ),
    )

    book = (
        ActivityCoachInterpretationBook(
            records=(
                older,
                newer,
            )
        )
    )

    assert (
        book.latest_for_workout(
            workout_id="workout-1"
        )
        == newer
    )


def test_latest_interpretation_returns_none_for_unknown_workout():

    book = (
        ActivityCoachInterpretationBook(
            records=(
                create_interpretation(),
            )
        )
    )

    assert (
        book.latest_for_workout(
            workout_id="unknown-workout"
        )
        is None
    )



def test_prunes_legacy_context_versions_on_load():

    older = create_interpretation(
        context_hash="context-old",
        generated_at=datetime(
            2026,
            8,
            10,
            12,
            0,
        ),
    )

    newer = create_interpretation(
        context_hash="context-new",
        generated_at=datetime(
            2026,
            8,
            12,
            12,
            0,
        ),
    )

    book = (
        ActivityCoachInterpretationBook(
            records=(
                newer,
                older,
            )
        )
    )

    assert len(book) == 1

    assert (
        book.latest_for_workout(
            workout_id="workout-1"
        )
        == newer
    )


def test_removes_interpretation_for_workout():

    book = (
        ActivityCoachInterpretationBook(
            records=(
                create_interpretation(),
            )
        )
    )

    removed_count = (
        book.remove_for_workouts(
            (
                "workout-1",
            )
        )
    )

    assert removed_count == 1
    assert len(book) == 0


def test_keeps_unrelated_interpretation():

    first = create_interpretation()

    second = (
        ActivityCoachInterpretation(
            workout_id="workout-2",
            contract_version=(
                "activity-coach-v1"
            ),
            context_hash="context-2",
            generated_at=datetime(
                2026,
                8,
                12,
                14,
                0,
            ),
            narrative=create_narrative(),
        )
    )

    book = (
        ActivityCoachInterpretationBook(
            records=(
                first,
                second,
            )
        )
    )

    removed_count = (
        book.remove_for_workouts(
            (
                "workout-1",
            )
        )
    )

    assert removed_count == 1
    assert len(book) == 1

    assert (
        book.latest_for_workout(
            workout_id="workout-2"
        )
        == second
    )