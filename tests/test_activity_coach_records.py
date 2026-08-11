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
):

    return ActivityCoachInterpretation(
        workout_id="workout-1",
        contract_version=(
            "activity-coach-v1"
        ),
        context_hash=context_hash,
        generated_at=datetime(
            2026,
            8,
            11,
            14,
            0,
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


def test_keeps_different_context_versions():

    book = (
        ActivityCoachInterpretationBook()
    )

    book.add(
        create_interpretation(
            context_hash="context-a"
        )
    )
    book.add(
        create_interpretation(
            context_hash="context-b"
        )
    )

    assert len(book) == 2