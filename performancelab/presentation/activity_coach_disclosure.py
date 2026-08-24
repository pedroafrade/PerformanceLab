"""
PerformanceLab

User-facing disclosure for Training Coach generation.
"""

from dataclasses import (
    dataclass,
)


@dataclass(
    frozen=True
)
class ActivityCoachDisclosureData:
    """
    Immutable information shown before the first generation.
    """

    heading: str
    purpose: str
    provider: str

    data_categories: tuple[
        str,
        ...,
    ]

    original_file_sent: bool
    interpretation_retained: bool
    limitation: str

    @property
    def data_summary(
        self,
    ) -> str:
        """
        Return the readable list of data categories.
        """

        return "; ".join(
            self.data_categories
        )


def build_activity_coach_disclosure(
) -> ActivityCoachDisclosureData:
    """
    Describe the current factual Training Coach data flow.
    """

    return ActivityCoachDisclosureData(
        heading="Before you generate",
        purpose=(
            "PerformanceLab sends a structured summary "
            "to Google Gemini to generate a training "
            "interpretation for this activity."
        ),
        provider="Google Gemini",
        data_categories=(
            (
                "activity facts such as sport, date, "
                "duration, distance, elevation and load"
            ),
            (
                "available heart-rate, power, cadence "
                "and environmental summaries"
            ),
            (
                "your RPE and any Additional information "
                "recorded for the activity"
            ),
            (
                "recent training, plan phase and the "
                "next relevant event"
            ),
            (
                "threshold references and current recovery "
                "or load only when relevant to the latest "
                "activity"
            ),
        ),
        original_file_sent=False,
        interpretation_retained=True,
        limitation=(
            "The result supports training decisions and "
            "is not medical advice."
        ),
    )