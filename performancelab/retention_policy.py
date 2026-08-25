"""
PerformanceLab

Explicit retention periods for the private alpha.
"""

from collections.abc import (
    Mapping,
)
from dataclasses import (
    dataclass,
)


def _retention_days(
    value,
    *,
    field_name: str,
    allow_zero: bool = False,
) -> int:
    """
    Validate one explicit retention duration in days.
    """

    if (
        not isinstance(
            value,
            int,
        )
        or isinstance(
            value,
            bool,
        )
    ):

        raise TypeError(
            f"{field_name} must be an integer."
        )

    minimum = (
        0
        if allow_zero
        else 1
    )

    if value < minimum:

        requirement = (
            "zero or greater"
            if allow_zero
            else "greater than zero"
        )

        raise ValueError(
            f"{field_name} must be {requirement}."
        )

    return value

RETENTION_SETTING_NAMES = {
    "inactive_account_days": (
        "RETENTION_INACTIVE_ACCOUNT_DAYS"
    ),
    "inactivity_notice_days": (
        "RETENTION_INACTIVITY_NOTICE_DAYS"
    ),
    "training_coach_usage_days": (
        "RETENTION_TRAINING_COACH_USAGE_DAYS"
    ),
    "consent_evidence_days": (
        "RETENTION_CONSENT_EVIDENCE_DAYS"
    ),
    "unused_invitation_days": (
        "RETENTION_UNUSED_INVITATION_DAYS"
    ),
    "expired_invitation_days": (
        "RETENTION_EXPIRED_INVITATION_DAYS"
    ),
    "application_log_days": (
        "RETENTION_APPLICATION_LOG_DAYS"
    ),
    "error_alert_days": (
        "RETENTION_ERROR_ALERT_DAYS"
    ),
    "backup_days": (
        "RETENTION_BACKUP_DAYS"
    ),
    "support_request_days": (
        "RETENTION_SUPPORT_REQUEST_DAYS"
    ),
    "post_alpha_days": (
        "RETENTION_POST_ALPHA_DAYS"
    ),
}


def _mapping_integer(
    value,
    *,
    setting_name: str,
) -> int:
    """
    Convert one environment-style value to an integer.
    """

    if (
        isinstance(
            value,
            int,
        )
        and not isinstance(
            value,
            bool,
        )
    ):

        return value

    if not isinstance(
        value,
        str,
    ):

        raise TypeError(
            f"{setting_name} must be an integer."
        )

    try:

        return int(
            value.strip()
        )

    except ValueError as error:

        raise ValueError(
            f"{setting_name} must be an integer."
        ) from error

@dataclass(
    frozen=True
)
class AlphaRetentionPolicy:
    """
    Explicit private alpha retention periods.

    This model intentionally provides no defaults. Every
    duration must be chosen and documented before the alpha
    environment is activated.
    """

    inactive_account_days: int
    inactivity_notice_days: int
    training_coach_usage_days: int
    consent_evidence_days: int
    unused_invitation_days: int
    expired_invitation_days: int
    application_log_days: int
    error_alert_days: int
    backup_days: int
    support_request_days: int
    post_alpha_days: int

    def __post_init__(
        self,
    ) -> None:

        positive_fields = (
            "inactive_account_days",
            "inactivity_notice_days",
            "training_coach_usage_days",
            "unused_invitation_days",
            "expired_invitation_days",
            "application_log_days",
            "error_alert_days",
            "backup_days",
            "support_request_days",
            "post_alpha_days",
        )

        for field_name in positive_fields:

            object.__setattr__(
                self,
                field_name,
                _retention_days(
                    getattr(
                        self,
                        field_name,
                    ),
                    field_name=field_name,
                ),
            )

        object.__setattr__(
            self,
            "consent_evidence_days",
            _retention_days(
                self.consent_evidence_days,
                field_name=(
                    "consent_evidence_days"
                ),
                allow_zero=True,
            ),
        )

        if (
            self.inactivity_notice_days
            >= self.inactive_account_days
        ):

            raise ValueError(
                "inactivity_notice_days must be shorter "
                "than inactive_account_days."
            )

    @classmethod
    def from_mapping(
        cls,
        values: Mapping[
            str,
            object,
        ],
    ):
        """
        Build a policy from explicit environment settings.
        """

        if not isinstance(
            values,
            Mapping,
        ):

            raise TypeError(
                "Retention settings must be a mapping."
            )

        missing_settings = tuple(
            setting_name
            for setting_name
            in RETENTION_SETTING_NAMES.values()
            if (
                setting_name not in values
                or values[
                    setting_name
                ] is None
                or (
                    isinstance(
                        values[
                            setting_name
                        ],
                        str,
                    )
                    and not (
                        values[
                            setting_name
                        ].strip()
                    )
                )
            )
        )

        if missing_settings:

            raise RuntimeError(
                "Missing private alpha retention "
                "settings: "
                + ", ".join(
                    missing_settings
                )
                + "."
            )

        return cls(
            **{
                field_name: _mapping_integer(
                    values[
                        setting_name
                    ],
                    setting_name=(
                        setting_name
                    ),
                )
                for (
                    field_name,
                    setting_name,
                )
                in (
                    RETENTION_SETTING_NAMES
                    .items()
                )
            }
        )

    def as_dict(
        self,
    ) -> dict[
        str,
        int,
    ]:
        """
        Return a serializable retention schedule.
        """

        return {
            "inactive_account_days": (
                self.inactive_account_days
            ),
            "inactivity_notice_days": (
                self.inactivity_notice_days
            ),
            "training_coach_usage_days": (
                self.training_coach_usage_days
            ),
            "consent_evidence_days": (
                self.consent_evidence_days
            ),
            "unused_invitation_days": (
                self.unused_invitation_days
            ),
            "expired_invitation_days": (
                self.expired_invitation_days
            ),
            "application_log_days": (
                self.application_log_days
            ),
            "error_alert_days": (
                self.error_alert_days
            ),
            "backup_days": (
                self.backup_days
            ),
            "support_request_days": (
                self.support_request_days
            ),
            "post_alpha_days": (
                self.post_alpha_days
            ),
        }