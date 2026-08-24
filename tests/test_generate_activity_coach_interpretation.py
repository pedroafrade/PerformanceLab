from datetime import (
    datetime,
    timezone,
)

from performancelab import (
    Athlete,
)
from performancelab.application import (
    GenerateActivityCoachInterpretation,
)
from performancelab.coaching import (
    ActivityCoachCoordinator,
    ActivityCoachGenerationService,
    ActivityCoachNarrative,
    ActivityCoachProviderUnavailable,
    ActivityCoachResolutionStatus,
)
from performancelab.storage.in_memory_training_coach_usage_repository import (
    InMemoryTrainingCoachUsageRepository,
)
from performancelab.training_coach_usage_limits import (
    TrainingCoachUsageLimits,
)


class Provider:

    provider_name = "fake"
    model_name = "fake-model"

    def __init__(
        self,
        *,
        unavailable=False,
    ):

        self.call_count = 0
        self.unavailable = unavailable

    def generate(
        self,
        payload,
    ):

        self.call_count += 1

        if self.unavailable:

            raise (
                ActivityCoachProviderUnavailable()
            )

        return ActivityCoachNarrative(
            measured_facts="Facts.",
            deterministic_signals=(
                "Signals."
            ),
            prudent_interpretation=(
                "Interpretation."
            ),
            recommendations=(
                "Recommendation."
            ),
            data_limitations=(
                "Limitations."
            ),
            provider=self.provider_name,
            model=self.model_name,
        )


def fixed_time():

    return datetime(
        2026,
        8,
        24,
        18,
        0,
        tzinfo=timezone.utc,
    )


def payload():

    return {
        "contract_version": (
            "activity-coach-v1"
        ),
    }


def create_use_case(
    *,
    provider,
    repository,
    user_limit=2,
    global_limit=10,
):

    coordinator = ActivityCoachCoordinator(
        generation_service=(
            ActivityCoachGenerationService(
                provider
            )
        ),
        now=fixed_time,
    )

    return GenerateActivityCoachInterpretation(
        coordinator=coordinator,
        usage_repository=repository,
        usage_limits=(
            TrainingCoachUsageLimits(
                user_daily_limit=(
                    user_limit
                ),
                global_daily_limit=(
                    global_limit
                ),
            )
        ),
        clock=fixed_time,
    )


def test_generates_below_daily_limit():

    provider = Provider()

    repository = (
        InMemoryTrainingCoachUsageRepository()
    )

    result = create_use_case(
        provider=provider,
        repository=repository,
    ).execute(
        user_id="user-1",
        athlete=Athlete(
            name="Pedro"
        ),
        workout_id="workout-1",
        payload=payload(),
    )

    assert (
        result.status
        is ActivityCoachResolutionStatus
        .GENERATED
    )

    assert provider.call_count == 1

    counts = repository.counts_for_utc_day(
        user_id="user-1",
        utc_day=fixed_time().date(),
    )

    assert counts.user_count == 1
    assert counts.global_count == 1


def test_blocks_generation_at_user_limit():

    provider = Provider()

    repository = (
        InMemoryTrainingCoachUsageRepository()
    )

    use_case = create_use_case(
        provider=provider,
        repository=repository,
        user_limit=1,
    )

    use_case.execute(
        user_id="user-1",
        athlete=Athlete(
            name="Pedro"
        ),
        workout_id="workout-1",
        payload=payload(),
    )

    result = use_case.execute(
        user_id="user-1",
        athlete=Athlete(
            name="Pedro"
        ),
        workout_id="workout-2",
        payload=payload(),
    )

    assert (
        result.status
        is ActivityCoachResolutionStatus
        .LIMIT_REACHED
    )

    assert (
        result.error_code
        == "user_daily_limit"
    )

    assert provider.call_count == 1


def test_failed_generation_does_not_consume_limit():

    unavailable_provider = Provider(
        unavailable=True
    )

    repository = (
        InMemoryTrainingCoachUsageRepository()
    )

    failed_result = create_use_case(
        provider=unavailable_provider,
        repository=repository,
        user_limit=1,
    ).execute(
        user_id="user-1",
        athlete=Athlete(
            name="Pedro"
        ),
        workout_id="workout-1",
        payload=payload(),
    )

    assert (
        failed_result.status
        is ActivityCoachResolutionStatus
        .UNAVAILABLE
    )

    counts = repository.counts_for_utc_day(
        user_id="user-1",
        utc_day=fixed_time().date(),
    )

    assert counts.user_count == 0
    assert counts.global_count == 0

    working_provider = Provider()

    successful_result = create_use_case(
        provider=working_provider,
        repository=repository,
        user_limit=1,
    ).execute(
        user_id="user-1",
        athlete=Athlete(
            name="Pedro"
        ),
        workout_id="workout-2",
        payload=payload(),
    )

    assert (
        successful_result.status
        is ActivityCoachResolutionStatus
        .GENERATED
    )