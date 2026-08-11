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
                ActivityCoachProviderUnavailable()
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
                ActivityCoachProviderUnavailable()
            ) from error

        response_text = getattr(
            response,
            "text",
            None,
        )

        if not response_text:
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