from datetime import (
    datetime,
    timezone,
)

from performancelab import (
    Athlete,
)
from performancelab.coaching import (
    ActivityCoachCoordinator,
    ActivityCoachGenerationService,
    ActivityCoachNarrative,
    ActivityCoachProviderUnavailable,
    ActivityCoachResolutionStatus,
)


class CountingProvider:

    provider_name = "fake"
    model_name = "fake-model"

    def __init__(
        self,
        *,
        unavailable: bool = False,
    ) -> None:

        self.call_count = 0
        self.unavailable = unavailable

    def generate(
        self,
        payload,
    ) -> ActivityCoachNarrative:

        self.call_count += 1

        if self.unavailable:
            raise (
                ActivityCoachProviderUnavailable()
            )

        return ActivityCoachNarrative(
            measured_facts=(
                "Measured facts."
            ),
            deterministic_signals=(
                "Deterministic signals."
            ),
            prudent_interpretation=(
                "Interpretation."
            ),
            recommendations=(
                f"Recommendation "
                f"{self.call_count}."
            ),
            data_limitations=(
                "Missing data declared."
            ),
            provider=self.provider_name,
            model=self.model_name,
        )


def fixed_now():

    return datetime(
        2026,
        8,
        11,
        15,
        0,
        tzinfo=timezone.utc,
    )


def create_coordinator(
    provider,
):

    return ActivityCoachCoordinator(
        generation_service=(
            ActivityCoachGenerationService(
                provider
            )
        ),
        now=fixed_now,
    )


def create_payload(
    *,
    load=450.0,
):

    return {
        "contract_version": (
            "activity-coach-v1"
        ),
        "assessment": {
            "completed_load": load,
        },
    }


def test_generates_and_stores_interpretation():

    athlete = Athlete(
        name="Pedro"
    )
    provider = CountingProvider()

    result = create_coordinator(
        provider
    ).resolve(
        athlete=athlete,
        workout_id="workout-1",
        payload=create_payload(),
    )

    assert (
        result.status
        is ActivityCoachResolutionStatus
        .GENERATED
    )
    assert result.interpretation is not None
    assert provider.call_count == 1
    assert len(
        athlete.activity_coach_interpretations
    ) == 1
    assert (
        result.interpretation.generated_at
        == fixed_now()
    )


def test_reuses_matching_stored_interpretation():

    athlete = Athlete(
        name="Pedro"
    )
    provider = CountingProvider()
    coordinator = create_coordinator(
        provider
    )
    payload = create_payload()

    first = coordinator.resolve(
        athlete=athlete,
        workout_id="workout-1",
        payload=payload,
    )

    second = coordinator.resolve(
        athlete=athlete,
        workout_id="workout-1",
        payload=payload,
    )

    assert (
        first.status
        is ActivityCoachResolutionStatus
        .GENERATED
    )
    assert (
        second.status
        is ActivityCoachResolutionStatus
        .STORED
    )
    assert (
        second.interpretation
        == first.interpretation
    )
    assert provider.call_count == 1


def test_changed_context_generates_new_version():

    athlete = Athlete(
        name="Pedro"
    )
    provider = CountingProvider()
    coordinator = create_coordinator(
        provider
    )

    coordinator.resolve(
        athlete=athlete,
        workout_id="workout-1",
        payload=create_payload(
            load=450.0
        ),
    )

    result = coordinator.resolve(
        athlete=athlete,
        workout_id="workout-1",
        payload=create_payload(
            load=500.0
        ),
    )

    assert (
        result.status
        is ActivityCoachResolutionStatus
        .GENERATED
    )
    assert provider.call_count == 2
    assert len(
        athlete.activity_coach_interpretations
    ) == 2


def test_regenerates_only_when_explicitly_requested():

    athlete = Athlete(
        name="Pedro"
    )
    provider = CountingProvider()
    coordinator = create_coordinator(
        provider
    )
    payload = create_payload()

    coordinator.resolve(
        athlete=athlete,
        workout_id="workout-1",
        payload=payload,
    )

    regenerated = coordinator.resolve(
        athlete=athlete,
        workout_id="workout-1",
        payload=payload,
        regenerate=True,
    )

    assert (
        regenerated.status
        is ActivityCoachResolutionStatus
        .GENERATED
    )
    assert provider.call_count == 2
    assert len(
        athlete.activity_coach_interpretations
    ) == 1
    assert (
        regenerated
        .interpretation
        .narrative
        .recommendations
        == "Recommendation 2."
    )


def test_does_not_store_unavailable_generation():

    athlete = Athlete(
        name="Pedro"
    )
    provider = CountingProvider(
        unavailable=True
    )

    result = create_coordinator(
        provider
    ).resolve(
        athlete=athlete,
        workout_id="workout-1",
        payload=create_payload(),
    )

    assert (
        result.status
        is ActivityCoachResolutionStatus
        .UNAVAILABLE
    )
    assert (
        result.error_code
        == "provider_unavailable"
    )
    assert len(
        athlete.activity_coach_interpretations
    ) == 0


def test_rejects_missing_contract_version():

    athlete = Athlete(
        name="Pedro"
    )
    provider = CountingProvider()

    result = create_coordinator(
        provider
    ).resolve(
        athlete=athlete,
        workout_id="workout-1",
        payload={
            "assessment": {},
        },
    )

    assert (
        result.status
        is ActivityCoachResolutionStatus
        .FAILED
    )
    assert (
        result.error_code
        == "invalid_contract_version"
    )
    assert provider.call_count == 0