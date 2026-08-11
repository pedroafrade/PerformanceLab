import json

import pytest

from google.genai import types

from performancelab.coaching import (
    ActivityCoachProviderUnavailable,
)
from performancelab.integrations import (
    GEMINI_ACTIVITY_COACH_MODEL,
    GeminiActivityCoachProvider,
)


class FakeGeminiResponse:

    def __init__(
        self,
        text,
    ) -> None:

        self.text = text


class FakeGeminiModels:

    def __init__(
        self,
        *,
        response_text=None,
        error=None,
    ) -> None:

        self.response_text = (
            response_text
        )
        self.error = error
        self.request = None

    def generate_content(
        self,
        **request,
    ):

        self.request = request

        if self.error is not None:
            raise self.error

        return FakeGeminiResponse(
            self.response_text
        )


class FakeGeminiClient:

    def __init__(
        self,
        models,
    ) -> None:

        self.models = models


def valid_response_text():

    return json.dumps(
        {
            "measured_facts": (
                "The completed load was measured."
            ),
            "deterministic_signals": (
                "Load was above plan."
            ),
            "prudent_interpretation": (
                "The session was more demanding "
                "than planned."
            ),
            "recommendations": (
                "Consider the next session "
                "conservatively."
            ),
            "data_limitations": (
                "Sleep quality was not recorded."
            ),
        }
    )


def test_generates_structured_narrative():

    models = FakeGeminiModels(
        response_text=(
            valid_response_text()
        )
    )

    provider = (
        GeminiActivityCoachProvider(
            client=FakeGeminiClient(
                models
            )
        )
    )

    narrative = provider.generate(
        {
            "contract_version": (
                "activity-coach-v1"
            ),
        }
    )

    assert narrative.provider == (
        "google-gemini"
    )
    assert narrative.model == (
        GEMINI_ACTIVITY_COACH_MODEL
    )
    assert narrative.measured_facts == (
        "The completed load was measured."
    )
    assert narrative.data_limitations == (
        "Sleep quality was not recorded."
    )


def test_sends_deterministic_json_payload():

    models = FakeGeminiModels(
        response_text=(
            valid_response_text()
        )
    )

    provider = (
        GeminiActivityCoachProvider(
            client=FakeGeminiClient(
                models
            )
        )
    )

    provider.generate(
        {
            "rules": [
                "Use only provided data."
            ],
            "contract_version": (
                "activity-coach-v1"
            ),
        }
    )

    request = models.request

    assert request["model"] == (
        GEMINI_ACTIVITY_COACH_MODEL
    )

    sent_payload = json.loads(
        request["contents"]
    )

    assert sent_payload[
        "contract_version"
    ] == "activity-coach-v1"

    config = request[
        "config"
    ]

    types.GenerateContentConfig(
        **config
    )

    assert config[
        "response_mime_type"
    ] == "application/json"

    assert config[
        "response_json_schema"
    ][
        "required"
    ] == [
        "measured_facts",
        "deterministic_signals",
        "prudent_interpretation",
        "recommendations",
        "data_limitations",
    ]


def test_converts_api_failure_to_unavailable():

    models = FakeGeminiModels(
        error=RuntimeError(
            "Quota exceeded"
        )
    )

    provider = (
        GeminiActivityCoachProvider(
            client=FakeGeminiClient(
                models
            )
        )
    )

    with pytest.raises(
        ActivityCoachProviderUnavailable
    ):
        provider.generate(
            {}
        )


def test_rejects_empty_response():

    models = FakeGeminiModels(
        response_text=None
    )

    provider = (
        GeminiActivityCoachProvider(
            client=FakeGeminiClient(
                models
            )
        )
    )

    with pytest.raises(
        ValueError
    ):
        provider.generate(
            {}
        )


def test_rejects_invalid_json_response():

    models = FakeGeminiModels(
        response_text=(
            "not valid json"
        )
    )

    provider = (
        GeminiActivityCoachProvider(
            client=FakeGeminiClient(
                models
            )
        )
    )

    with pytest.raises(
        json.JSONDecodeError
    ):
        provider.generate(
            {}
        )