"""
PerformanceLab

Athlete settings page.
"""

import streamlit as st

from .athlete_panel import (
    show_athlete_panel,
)
from .training_coach_consent import (
    show_training_coach_consent_settings,
)


PARTICIPANT_DELETION_PHRASE = (
    "DELETE MY DATA"
)


def participant_deletion_confirmed(
    confirmation_text: str,
    *,
    acknowledged: bool,
) -> bool:
    """
    Require both an acknowledgement and an exact phrase.
    """

    if not isinstance(
        confirmation_text,
        str,
    ):

        return False

    return (
        acknowledged
        and confirmation_text.strip()
        == PARTICIPANT_DELETION_PHRASE
    )

def privacy_contact_mailto(
    email: str,
) -> str:
    """
    Return a mail link for a validated privacy contact.
    """

    if (
        not isinstance(
            email,
            str,
        )
        or not email.strip()
        or "@"
        not in email
    ):

        raise ValueError(
            "A valid privacy contact email is required."
        )

    return (
        "mailto:"
        + email.strip().lower()
    )

def support_contact_mailto(
    email: str,
) -> str:
    """
    Return a mail link for a validated support contact.
    """

    if (
        not isinstance(
            email,
            str,
        )
        or not email.strip()
        or "@"
        not in email
    ):

        raise ValueError(
            "A valid support contact email is required."
        )

    return (
        "mailto:"
        + email.strip().lower()
    )

def _settings_page_header() -> None:
    """
    Display the standard settings page header.
    """

    st.markdown(
        """
        <style>
        div[data-testid="stMainBlockContainer"] {
            padding-top: 3.65rem;
            padding-bottom: 0 !important;
        }

        section[data-testid="stMain"] > div {
            padding-bottom: 0 !important;
        }

        div[data-testid="stMainBlockContainer"]
        > div:last-child {
            margin-bottom: 0 !important;
            padding-bottom: 0 !important;
        }

        .settings-page-header {
            margin: 0 0 0.45rem 0;
            padding: 0;
        }

        .settings-page-title {
            margin: 0;
            font-size: 2.25rem;
            font-weight: 750;
            line-height: 1.05;
        }

        .settings-page-subtitle {
            margin-top: 0.32rem;
            font-size: 0.76rem;
            line-height: 1.15;
            opacity: 0.58;
        }
        </style>

        <div class="settings-page-header">
            <div class="settings-page-title">
                Settings
            </div>
            <div class="settings-page-subtitle">
                Manage your profile, Training Coach
                permission and private alpha data.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_settings_page(
    athlete,
    *,
    training_coach_permitted: bool = False,
    on_allow_training_coach=None,
    on_withdraw_training_coach=None,
    participant_export_json: str | None = None,
    privacy_contact_email: str | None = None,
    support_contact_email: str | None = None,
    on_delete_participant_data=None,
    participant_deletion_error: str | None = None,
):
    """
    Display athlete settings and participant data controls.
    """

    _settings_page_header()

    st.info(
        "Changes to physiological values, heart-rate "
        "zones and availability can influence future "
        "training plans and recommendations."
    )

    st.divider()

    show_training_coach_consent_settings(
        permitted=(
            training_coach_permitted
        ),
        on_allow=(
            on_allow_training_coach
        ),
        on_withdraw=(
            on_withdraw_training_coach
        ),
    )

    st.divider()

    st.subheader(
        "Your data"
    )

    st.caption(
        "Download a readable JSON export containing "
        "your account, consent records, Training Coach "
        "usage metadata and complete athlete profile."
    )

    if (
        participant_export_json
        is not None
    ):

        st.download_button(
            "Download my data",
            data=participant_export_json,
            file_name=(
                "performancelab-data-export.json"
            ),
            mime="application/json",
            use_container_width=True,
        )

    else:

        st.warning(
            "Your data export is temporarily unavailable."
        )

    st.divider()

    st.subheader(
        "Your privacy rights"
    )

    st.caption(
        "You can request access, correction, export, "
        "deletion, restriction, objection or withdrawal "
        "of consent. We will respond without undue delay "
        "and no later than one month after receiving a "
        "verified request."
    )

    if privacy_contact_email:

        contact_url = privacy_contact_mailto(
            privacy_contact_email
        )

        st.markdown(
            "Privacy contact: "
            f"[{privacy_contact_email}]"
            f"({contact_url})"
        )

    else:

        st.warning(
            "The privacy contact is not configured "
            "in this local environment."
        )

    st.divider()

    st.subheader(
        "Support"
    )

    st.caption(
        "For help with access, invitations, application "
        "errors or use of the private alpha, contact the "
        "PerformanceLab support address."
    )

    if support_contact_email:

        support_url = support_contact_mailto(
            support_contact_email
        )

        st.markdown(
            "Support contact: "
            f"[{support_contact_email}]"
            f"({support_url})"
        )

    else:

        st.warning(
            "The support contact is not configured "
            "in this local environment."
        )

    st.divider()

    st.subheader(
        "Delete account and data"
    )

    st.warning(
        "This permanently deletes your account, athlete "
        "profile, activities, routes, plans, interpretations, "
        "consents and active operational records. This action "
        "cannot be undone."
    )

    if participant_deletion_error:

        st.error(
            participant_deletion_error
        )

    with st.expander(
        "Permanent deletion",
        expanded=False,
    ):

        acknowledged = st.checkbox(
            "I understand that my active PerformanceLab "
            "account and athlete data will be permanently "
            "deleted.",
            key=(
                "participant_deletion_acknowledged"
            ),
        )

        confirmation_text = st.text_input(
            "Type DELETE MY DATA to confirm",
            key=(
                "participant_deletion_confirmation"
            ),
        )

        deletion_confirmed = (
            participant_deletion_confirmed(
                confirmation_text,
                acknowledged=acknowledged,
            )
        )

        st.button(
            "Permanently delete my data",
            type="primary",
            disabled=(
                not deletion_confirmed
                or on_delete_participant_data
                is None
            ),
            on_click=(
                on_delete_participant_data
            ),
            use_container_width=True,
        )

    st.divider()

    st.subheader(
        "Athlete profile"
    )

    st.caption(
        "These values are inputs to the PerformanceLab "
        "domain and planning system."
    )

    return show_athlete_panel(
        athlete,
        show_heading=False,
    )