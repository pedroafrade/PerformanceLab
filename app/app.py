"""
PerformanceLab

Streamlit application.
"""

import os

from datetime import (
    date,
)
from pathlib import Path

import streamlit as st

from components import (
    show_activities_page,
    show_athlete_panel,
    show_calendar_page,
    show_dashboard,
    show_development_page,
    show_plan_page,
    show_selected_workout_route,
    show_settings_page,
    show_sidebar,
    show_today_page,
    show_training_coach_consent_dialog,
    show_workout_editor,
)

from performancelab import (
    Athlete,
)
from performancelab.application import (
    DeleteWorkouts,
    GenerateTrainingPlan,
    ImportActivities,
    LoadActiveAthlete,
    GenerateActivityCoachInterpretation,
    ManageTrainingCoachConsent,
    ProvisionInvitedUser,
    UpdateWorkout,
)
from performancelab.authorization import (
    AthleteAuthorizationService,
)
from performancelab.coaching import (
    ActivityCoachCoordinator,
    ActivityCoachGenerationService,
    ActivityCoachResolutionStatus,
)
from performancelab.integrations import (
    GeminiActivityCoachProvider,
)
from performancelab.identity import User
from performancelab.oidc_identity import (
    external_identity_from_claims,
)
from performancelab.runtime_configuration import (
    RuntimeConfiguration,
)
from performancelab.storage.repository_factory import (
    build_repository_bundle,
)


# ======================================================
# Page configuration
# ======================================================

st.set_page_config(
    page_title="PerformanceLab",
    page_icon="📈",
    layout="wide",
)

APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent

runtime_values = dict(
    os.environ
)

for configuration_key in (
    "PERFORMANCELAB_ENV",
    "DATABASE_URL",
    "TRAINING_COACH_USER_DAILY_LIMIT",
    "TRAINING_COACH_GLOBAL_DAILY_LIMIT",
):

    if configuration_key in st.secrets:

        runtime_values[
            configuration_key
        ] = st.secrets[
            configuration_key
        ]

runtime_configuration = (
    RuntimeConfiguration.from_mapping(
        runtime_values
    )
)

repository_bundle = (
    build_repository_bundle(
        runtime_configuration,
        data_directory=(
            PROJECT_ROOT
            / "data"
        ),
    )
)

athlete_repository = (
    repository_bundle
    .athlete_repository
)
user_repository = (
    repository_bundle
    .user_repository
)
external_identity_repository = (
    repository_bundle
    .external_identity_repository
)
alpha_invitation_repository = (
    repository_bundle
    .alpha_invitation_repository
)
athlete_access_repository = (
    repository_bundle
    .athlete_access_repository
)
training_coach_consent_repository = (
    repository_bundle
    .training_coach_consent_repository
)
training_coach_usage_repository = (
    repository_bundle
    .training_coach_usage_repository
)
athlete_authorization = (
    AthleteAuthorizationService(
        athlete_access_repository
    )
)
training_coach_consent_manager = (
    ManageTrainingCoachConsent(
        repository=(
            training_coach_consent_repository
        )
    )
)
training_coach_generator = (
    GenerateActivityCoachInterpretation(
        coordinator=(
            ActivityCoachCoordinator(
                generation_service=(
                    ActivityCoachGenerationService(
                        GeminiActivityCoachProvider()
                    )
                )
            )
        ),
        usage_repository=(
            training_coach_usage_repository
        ),
        usage_limits=(
            runtime_configuration
            .training_coach_usage_limits
        ),
    )
)

# ======================================================
# Session state
# ======================================================
    
def regenerate_weekly_plan() -> None:
    """
    Generate and persist a complete training plan.
    """

    athlete = st.session_state.athlete

    try:

        result = GenerateTrainingPlan(
            repository=athlete_repository
        ).execute(
            athlete.athlete_id,
            today=date.today(),
        )

    except Exception as error:

        st.session_state.plan_error = (
            str(error)
        )

        return

    st.session_state.athlete = (
        result.athlete
    )

    st.session_state.persisted_notice = (
        "Training plan generated."
    )

def import_completed_activities(
    workouts,
):
    """
    Import and persist parsed completed activities.
    """

    athlete = (
        st.session_state.athlete
    )

    result = ImportActivities(
        repository=athlete_repository
    ).execute(
        athlete.athlete_id,
        workouts,
    )

    st.session_state.athlete = (
        result.athlete
    )

    return result

def update_completed_workout(
    workout_id,
    update,
):
    """
    Update and persist one completed workout.
    """

    athlete = (
        st.session_state.athlete
    )

    result = UpdateWorkout(
        repository=athlete_repository
    ).execute(
        athlete.athlete_id,
        workout_id,
        update,
    )

    st.session_state.athlete = (
        result.athlete
    )

    return result

def delete_completed_workouts(
    workout_ids,
):
    """
    Delete and persist completed workouts.
    """

    athlete = (
        st.session_state.athlete
    )

    result = DeleteWorkouts(
        repository=athlete_repository
    ).execute(
        athlete.athlete_id,
        workout_ids,
    )

    st.session_state.athlete = (
        result.athlete
    )

    return result

def resolve_training_coach(
    *,
    athlete,
    workout_id,
    payload,
    regenerate,
):
    """
    Generate and persist a limited Training Coach result.
    """

    current_user = (
        st.session_state.current_user
    )

    if not (
        training_coach_consent_manager
        .is_permitted(
            user_id=current_user.user_id
        )
    ):

        raise PermissionError(
            "Training Coach consent is required."
        )

    with repository_bundle.transaction():

        result = (
            training_coach_generator
            .execute(
                user_id=(
                    current_user.user_id
                ),
                athlete=athlete,
                workout_id=workout_id,
                payload=payload,
                regenerate=regenerate,
            )
        )

        if (
            result.status
            is ActivityCoachResolutionStatus
            .GENERATED
        ):

            athlete_repository.save(
                athlete
            )

    return result

def allow_training_coach() -> None:
    """
    Persist consent for the authenticated user.
    """

    current_user = (
        st.session_state.current_user
    )

    with repository_bundle.transaction():

        training_coach_consent_manager.grant(
            user_id=current_user.user_id
        )

    st.session_state.persisted_notice = (
        "Training Coach enabled."
    )

def withdraw_training_coach() -> None:
    """
    Withdraw consent for the authenticated user.
    """

    current_user = (
        st.session_state.current_user
    )

    with repository_bundle.transaction():

        training_coach_consent_manager.withdraw(
            user_id=current_user.user_id
        )

    st.session_state[
        "training_coach_prompt_dismissed"
    ] = True

    st.session_state.persisted_notice = (
        "Training Coach permission withdrawn."
    )

def show_login_screen() -> None:
    """
    Display the PerformanceLab OIDC login screen.
    """

    left, centre, right = st.columns(
        [2, 3, 2]
    )

    with centre:

        st.markdown(
            "## PerformanceLab"
        )

        st.caption(
            "Sign in to continue."
        )

        st.write("")

        st.button(
            "Sign in with Google",
            type="primary",
            use_container_width=True,
            on_click=st.login,
        )

def logout() -> None:
    """
    End the current OIDC user session.
    """

    st.session_state.pop(
        "athlete",
        None,
    )

    st.session_state.pop(
        "current_user",
        None,
    )

    st.session_state.pop(
        "training_coach_prompt_dismissed",
        None,
    )

    st.logout()

def initialize_session_state() -> None:
    """
    Initialize the Streamlit application state.
    """

    # --------------------------------------------------
    # Interface state
    # --------------------------------------------------

    if "notice" not in st.session_state:
        st.session_state.notice = None

    if "persisted_notice" not in st.session_state:
        st.session_state.persisted_notice = None

    if "plan_error" not in st.session_state:
        st.session_state.plan_error = None

    if "confirm_delete" not in st.session_state:
        st.session_state.confirm_delete = False

    if "edit_workout" not in st.session_state:
        st.session_state.edit_workout = False

    if "page" not in st.session_state:
        st.session_state.page = "dashboard"

# ======================================================
# Application
# ======================================================

initialize_session_state()

if not st.user.is_logged_in:

    show_login_screen()

    st.stop()


if "current_user" not in st.session_state:

    try:

        external_identity = (
            external_identity_from_claims(
                st.user.to_dict()
            )
        )

        provision_result = (
            ProvisionInvitedUser(
                user_repository=(
                    user_repository
                ),
                identity_repository=(
                    external_identity_repository
                ),
                invitation_repository=(
                    alpha_invitation_repository
                ),
                access_repository=(
                    athlete_access_repository
                ),
                athlete_repository=(
                    athlete_repository
                ),
                transaction_factory=(
                    repository_bundle
                    .transaction
                ),
            )
            .execute(
                external_identity
            )
        )

        st.session_state.current_user = (
            provision_result.user
        )

    except PermissionError as error:

        st.error(
            str(error)
        )

        st.caption(
            "Access to this private alpha "
            "requires an invitation."
        )

        st.button(
            "Sign out",
            on_click=st.logout,
        )

        st.stop()

    except (
        TypeError,
        ValueError,
        KeyError,
        RuntimeError,
    ) as error:

        st.error(
            "Não foi possível validar "
            "a identidade autenticada."
        )

        st.code(
            str(error)
        )

        st.button(
            "Sign out",
            on_click=st.logout,
        )

        st.stop()


current_user: User = (
    st.session_state.current_user
)

if "athlete" not in st.session_state:

    try:
        load_result = (
            LoadActiveAthlete(
                repository=(
                    athlete_repository
                ),
                authorization=(
                    athlete_authorization
                ),
            )
            .execute(
                current_user
            )
        )

        st.session_state.athlete = (
            load_result.athlete
        )

    except PermissionError:

        st.error(
            "Esta conta não está autorizada "
            "a aceder a este perfil de atleta."
        )

        st.button(
            "Sign out",
            on_click=st.logout,
        )

        st.stop()

    except (
        FileNotFoundError,
        KeyError,
    ):
        st.error(
            "Não foi possível encontrar o perfil de atleta."
        )
        st.stop()

    except LookupError:
        st.warning(
            "Ainda não existem atletas disponíveis."
        )
        st.stop()

    except ValueError:
        st.error(
            "Esta conta de atleta não tem um perfil associado."
        )
        st.stop()

    except Exception as error:
        st.error(
            "Não foi possível carregar o perfil de atleta."
        )

        st.exception(error)
        st.stop()

athlete: Athlete = st.session_state.athlete

training_coach_permitted = (
    training_coach_consent_manager
    .is_permitted(
        user_id=current_user.user_id
    )
)

if (
    not training_coach_permitted
    and not st.session_state.get(
        "training_coach_prompt_dismissed",
        False,
    )
):

    show_training_coach_consent_dialog(
        on_allow=allow_training_coach
    )

should_save_athlete = (
    st.session_state.notice
    is not None
)

athlete = show_sidebar(
    athlete,
    on_logout=logout,
    on_import_activities=(
        import_completed_activities
    ),
    on_generate_plan=regenerate_weekly_plan,
)

page = st.session_state.page

if st.session_state.plan_error:

    st.error(
        "Não foi possível gerar o plano semanal."
    )

    st.code(
        st.session_state.plan_error
    )

    st.session_state.plan_error = None

if st.session_state.notice:

    st.toast(
        st.session_state.notice,
    )

    st.session_state.notice = None

if st.session_state.persisted_notice:

    st.toast(
        st.session_state.persisted_notice,
    )

    st.session_state.persisted_notice = None

if page == "dashboard":

    selected_workout = show_dashboard(
        athlete,
    )

    show_workout_editor(
        selected_workout,
        on_update_workout=(
            update_completed_workout
        ),
        on_delete_workouts=(
            delete_completed_workouts
        ),
    )

    show_selected_workout_route(
        selected_workout,
    )

elif page == "today":

    show_today_page(
        athlete
    )


elif page == "training":

    show_plan_page(
        athlete,
        on_generate_plan=(
            regenerate_weekly_plan
        ),
    )
elif page == "activities":

    activities_changed = (
        show_activities_page(
            athlete,
            on_update_workout=(
                update_completed_workout
            ),
            on_delete_workouts=(
                delete_completed_workouts
            ),
            training_coach_permitted=(
                training_coach_consent_manager
                .is_permitted(
                    user_id=(
                        current_user.user_id
                    )
                )
            ),
            on_allow_training_coach=(
                allow_training_coach
            ),
            on_resolve_training_coach=(
                resolve_training_coach
            ),
        )
    )

    if activities_changed:

        athlete_repository.save(
            athlete
        )

    if st.session_state.pop(
        "activity_coach_refresh_requested",
        False,
    ):

        st.rerun()
elif page == "athlete":

    athlete = show_athlete_panel(
        athlete,
    )
elif page == "calendar":

    show_calendar_page(
        athlete
    )
elif page == "development":

    show_development_page(
        athlete
    )
elif page == "settings":

    athlete = show_settings_page(
        athlete,
        training_coach_permitted=(
            training_coach_permitted
        ),
        on_allow_training_coach=(
            allow_training_coach
        ),
        on_withdraw_training_coach=(
            withdraw_training_coach
        ),
    )

else:

    TITLES = {
        "training": "Treinos",
        "goals": "Objetivos",
        "events": "Eventos",
        "analytics": "Análises",
        "statistics": "Estatísticas",
        "equipment": "Equipamento",
        "settings": "Configurações",
    }

    st.title(
        TITLES.get(page, page.title())
    )

    st.info(
        "🚧 Página em desenvolvimento."
    )

st.session_state.athlete = athlete

if should_save_athlete:

    athlete_repository.save(
        athlete,
    )

if (
    page == "athlete"
    and st.session_state.page == "dashboard"
):
    st.rerun()