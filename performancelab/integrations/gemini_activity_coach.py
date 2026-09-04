"""
PerformanceLab

Google Gemini Training Coach provider.
"""

import json

from collections.abc import (
    Mapping,
)

from performancelab.coaching import (
    ActivityCoachNarrative,
    ActivityCoachProviderUnavailable,
)


GEMINI_ACTIVITY_COACH_MODEL = (
    "gemini-3.5-flash"
)


_ACTIVITY_COACH_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "measured_facts": {
            "type": "string",
        },
        "deterministic_signals": {
            "type": "string",
        },
        "prudent_interpretation": {
            "type": "string",
        },
        "recommendations": {
            "type": "string",
        },
        "data_limitations": {
            "type": "string",
        },
    },
    "required": [
        "measured_facts",
        "deterministic_signals",
        "prudent_interpretation",
        "recommendations",
        "data_limitations",
    ],
}

def _gemini_error_code(
    error,
) -> str:
    """
    Convert provider-specific failures into stable,
    non-sensitive application error codes.
    """

    status_code = getattr(
        error,
        "status_code",
        None,
    )

    if status_code is None:

        status_code = getattr(
            error,
            "code",
            None,
        )

    if callable(
        status_code
    ):

        try:

            status_code = (
                status_code()
            )

        except Exception:

            status_code = None

    try:

        numeric_status = int(
            status_code
        )

    except (
        TypeError,
        ValueError,
    ):

        numeric_status = None

    message = str(
        error
    ).casefold()

    if (
        numeric_status
        in {
            401,
            403,
        }
        or "unauthenticated" in message
        or "authentication" in message
        or "permission denied" in message
        or "api key not valid" in message
    ):

        return (
            "provider_authentication"
        )

    if (
        numeric_status == 429
        or "quota" in message
        or "resource exhausted" in message
        or "rate limit" in message
    ):

        return "provider_quota"

    if (
        "safety" in message
        or "blocked" in message
        or "prohibited" in message
    ):

        return "provider_safety"

    if (
        numeric_status == 400
        or "invalid argument" in message
        or "bad request" in message
    ):

        return "provider_request"

    return "provider_unavailable"

class GeminiActivityCoachProvider:
    """
    Generates structured coach text through Google Gemini.

    A client can be injected for tests. When omitted, the
    official SDK reads GEMINI_API_KEY from the environment.
    """

    provider_name = "google-gemini"

    def __init__(
        self,
        *,
        model_name: str = (
            GEMINI_ACTIVITY_COACH_MODEL
        ),
        client=None,
    ) -> None:

        self._model_name = model_name
        self._client = client

    @property
    def model_name(
        self,
    ) -> str:

        return self._model_name

    def _configured_client(
        self,
    ):

        if self._client is not None:
            return self._client

        try:
            from google import genai

            self._client = (
                genai.Client()
            )

        except Exception as error:
            raise (
                ActivityCoachProviderUnavailable(
                    "provider_configuration"
                )
            ) from error

        return self._client

    @staticmethod
    def _prompt(
        payload: Mapping[
            str,
            object,
        ],
    ) -> str:
        """
        Serializes the deterministic contract without adding facts.
        """

        return json.dumps(
            dict(
                payload
            ),
            ensure_ascii=False,
            sort_keys=True,
            separators=(
                ",",
                ":",
            ),
        )

    def generate(
        self,
        payload: Mapping[
            str,
            object,
        ],
    ) -> ActivityCoachNarrative:

        client = (
            self._configured_client()
        )

        try:
            response = (
                client.models.generate_content(
                    model=self.model_name,
                    contents=self._prompt(
                        payload
                    ),
                    config={
                        "http_options": {
                            "timeout": 60000,
                            "retry_options": {"attempts": 1},
                        },
                        "response_mime_type": (
                            "application/json"
                        ),
                        "response_json_schema": (
                            _ACTIVITY_COACH_RESPONSE_SCHEMA
                        ),
                    },
                )
            )

        except Exception as error:
            raise (
                ActivityCoachProviderUnavailable(
                    _gemini_error_code(
                        error
                    )
                )
            ) from error

        response_text = getattr(
            response,
            "text",
            None,
        )

        if not response_text:

            prompt_feedback = getattr(
                response,
                "prompt_feedback",
                None,
            )

            block_reason = getattr(
                prompt_feedback,
                "block_reason",
                None,
            )

            if block_reason:

                raise (
                    ActivityCoachProviderUnavailable(
                        "provider_safety"
                    )
                )

            raise ValueError(
                "Gemini returned no coach response"
            )

        response_data = json.loads(
            response_text
        )

        return ActivityCoachNarrative(
            measured_facts=str(
                response_data[
                    "measured_facts"
                ]
            ),
            deterministic_signals=str(
                response_data[
                    "deterministic_signals"
                ]
            ),
            prudent_interpretation=str(
                response_data[
                    "prudent_interpretation"
                ]
            ),
            recommendations=str(
                response_data[
                    "recommendations"
                ]
            ),
            data_limitations=str(
                response_data[
                    "data_limitations"
                ]
            ),
            provider=self.provider_name,
            model=self.model_name,
        )
