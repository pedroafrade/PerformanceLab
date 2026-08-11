from performancelab.coaching import (
    ActivityCoachGenerationService,
    ActivityCoachGenerationStatus,
    ActivityCoachNarrative,
    ActivityCoachProviderUnavailable,
)


class FakeActivityCoachProvider:

    provider_name = "fake"
    model_name = "fake-model"

    def __init__(
        self,
        *,
        failure: str | None = None,
    ) -> None:

        self.failure = failure
        self.received_payload = None

    def generate(
        self,
        payload,
    ) -> ActivityCoachNarrative:

        self.received_payload = payload

        if self.failure == "unavailable":
            raise (
                ActivityCoachProviderUnavailable()
            )

        if self.failure == "failed":
            raise RuntimeError(
                "Unexpected provider failure"
            )

        return ActivityCoachNarrative(
            measured_facts=(
                "Measured activity facts."
            ),
            deterministic_signals=(
                "Deterministic domain signals."
            ),
            prudent_interpretation=(
                "Prudent interpretation."
            ),
            recommendations=(
                "Prudent recommendations."
            ),
            data_limitations=(
                "Unavailable data is declared."
            ),
            provider=self.provider_name,
            model=self.model_name,
        )


def test_generates_with_fake_provider():

    provider = (
        FakeActivityCoachProvider()
    )

    service = (
        ActivityCoachGenerationService(
            provider
        )
    )

    payload = {
        "contract_version": (
            "activity-coach-v1"
        ),
    }

    result = service.generate(
        payload
    )

    assert (
        result.status
        is ActivityCoachGenerationStatus
        .GENERATED
    )
    assert result.narrative is not None
    assert (
        result.narrative.provider
        == "fake"
    )
    assert (
        result.narrative.model
        == "fake-model"
    )
    assert (
        provider.received_payload
        == payload
    )


def test_returns_unavailable_without_provider():

    service = (
        ActivityCoachGenerationService(
            None
        )
    )

    result = service.generate(
        {}
    )

    assert (
        result.status
        is ActivityCoachGenerationStatus
        .UNAVAILABLE
    )
    assert result.narrative is None
    assert (
        result.error_code
        == "provider_not_configured"
    )


def test_converts_provider_unavailability():

    provider = FakeActivityCoachProvider(
        failure="unavailable"
    )

    service = (
        ActivityCoachGenerationService(
            provider
        )
    )

    result = service.generate(
        {}
    )

    assert (
        result.status
        is ActivityCoachGenerationStatus
        .UNAVAILABLE
    )
    assert result.narrative is None
    assert (
        result.error_code
        == "provider_unavailable"
    )


def test_converts_unexpected_provider_failure():

    provider = FakeActivityCoachProvider(
        failure="failed"
    )

    service = (
        ActivityCoachGenerationService(
            provider
        )
    )

    result = service.generate(
        {}
    )

    assert (
        result.status
        is ActivityCoachGenerationStatus
        .FAILED
    )
    assert result.narrative is None
    assert (
        result.error_code
        == "generation_failed"
    )


def test_generation_result_is_immutable():

    service = (
        ActivityCoachGenerationService(
            None
        )
    )

    result = service.generate(
        {}
    )

    try:
        result.error_code = "changed"

    except AttributeError:
        pass

    else:
        raise AssertionError(
            "Generation result must be immutable"
        )