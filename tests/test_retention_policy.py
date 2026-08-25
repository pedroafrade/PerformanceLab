"""
Tests for explicit private alpha retention periods.
"""

import pytest

from performancelab.retention_policy import (
    AlphaRetentionPolicy,
)


def retention_policy(
    **changes,
) -> AlphaRetentionPolicy:

    values = {
        "inactive_account_days": 90,
        "inactivity_notice_days": 14,
        "training_coach_usage_days": 30,
        "consent_evidence_days": 0,
        "unused_invitation_days": 14,
        "expired_invitation_days": 7,
        "application_log_days": 14,
        "error_alert_days": 30,
        "backup_days": 14,
        "support_request_days": 30,
        "post_alpha_days": 30,
    }

    values.update(
        changes
    )

    return AlphaRetentionPolicy(
        **values
    )


def test_requires_every_retention_period_explicitly():

    with pytest.raises(
        TypeError
    ):

        AlphaRetentionPolicy()


def test_accepts_an_explicit_retention_schedule():

    policy = retention_policy()

    assert (
        policy.inactive_account_days
        == 90
    )

    assert (
        policy.consent_evidence_days
        == 0
    )

    assert (
        policy.as_dict()[
            "backup_days"
        ]
        == 14
    )


@pytest.mark.parametrize(
    "field_name",
    (
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
    ),
)
def test_positive_periods_cannot_be_zero(
    field_name,
):

    with pytest.raises(
        ValueError,
        match="greater than zero",
    ):

        retention_policy(
            **{
                field_name: 0
            }
        )


def test_consent_evidence_can_be_deleted_immediately():

    policy = retention_policy(
        consent_evidence_days=0
    )

    assert (
        policy.consent_evidence_days
        == 0
    )


def test_retention_periods_reject_booleans():

    with pytest.raises(
        TypeError,
        match="integer",
    ):

        retention_policy(
            backup_days=True
        )


def test_notice_period_must_be_shorter_than_inactivity_period():

    with pytest.raises(
        ValueError,
        match="must be shorter",
    ):

        retention_policy(
            inactive_account_days=30,
            inactivity_notice_days=30,
        )