"""
PerformanceLab

Streamlit application.
"""

from datetime import date, datetime, time, timedelta
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
    show_workout_editor,
)

from performancelab import (
    Athlete,
    create_workout,
)
from performancelab.application import (
    DeleteWorkouts,
    GenerateTrainingPlan,
    ImportActivities,
    LoadActiveAthlete,
    ProvisionInvitedUser,
    UpdateWorkout,
)

from performancelab.identity import User
from performancelab.oidc_identity import (
    external_identity_from_claims,
)
from performancelab.storage.json_alpha_invitation_repository import (
    JsonAlphaInvitationRepository,
)
from performancelab.storage.json_athlete_access_repository import (
    JsonAthleteAccessRepository,
)
from performancelab.storage.json_athlete_repository import (
    JsonAthleteRepository,
)
from performancelab.storage.json_external_identity_repository import (
    JsonExternalIdentityRepository,
)
from performancelab.storage.json_user_repository import (
    JsonUserRepository,
)

from performancelab.training.config import AthleteAvailability


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

ATHLETE_DATA_DIR = (
    PROJECT_ROOT
    / "data"
    / "athletes"
)

USER_DATA_DIR = (
    PROJECT_ROOT
    / "data"
    / "users"
)

EXTERNAL_IDENTITY_DATA_DIR = (
    PROJECT_ROOT
    / "data"
    / "external_identities"
)

ALPHA_INVITATION_DATA_DIR = (
    PROJECT_ROOT
    / "data"
    / "alpha_invitations"
)

ATHLETE_ACCESS_DATA_DIR = (
    PROJECT_ROOT
    / "data"
    / "athlete_access"
)

athlete_repository = JsonAthleteRepository(
    ATHLETE_DATA_DIR
)

user_repository = JsonUserRepository(
    USER_DATA_DIR
)
external_identity_repository = (
    JsonExternalIdentityRepository(
        EXTERNAL_IDENTITY_DATA_DIR
    )
)

alpha_invitation_repository = (
    JsonAlphaInvitationRepository(
        ALPHA_INVITATION_DATA_DIR
    )
)

athlete_access_repository = (
    JsonAthleteAccessRepository(
        ATHLETE_ACCESS_DATA_DIR
    )
)

# ======================================================
# Demonstration athlete
# ======================================================

def create_demo_athlete() -> Athlete:

    athlete = Athlete(
        name="Pedro",
        weight=70,
        ftp=280,
        max_hr=190,
        resting_hr=50,
    )

    athlete.availability = AthleteAvailability.from_minutes(
        monday=60,
        wednesday=60,
        saturday=120,
    )

    demo_workouts = [
        create_workout(
            sport="Running",
            workout_date=date.today() - timedelta(days=13),
            distance=8,
            duration=timedelta(minutes=45),
            elevation_gain=120,
            rpe=5,
            title="Easy Run",
        ),
        create_workout(
            sport="Cycling",
            workout_date=date.today() - timedelta(days=11),
            distance=42,
            duration=timedelta(hours=1, minutes=30),
            elevation_gain=450,
            rpe=6,
            title="Endurance Ride",
        ),
        create_workout(
            sport="Running",
            workout_date=date.today() - timedelta(days=9),
            distance=12,
            duration=timedelta(hours=1, minutes=5),
            elevation_gain=210,
            rpe=7,
            title="Tempo Run",
        ),
        create_workout(
            sport="Swimming",
            workout_date=date.today() - timedelta(days=7),
            distance=2.5,
            duration=timedelta(minutes=50),
            elevation_gain=0,
            rpe=5,
            title="Pool Session",
        ),
        create_workout(
            sport="Cycling",
            workout_date=date.today() - timedelta(days=5),
            distance=55,
            duration=timedelta(hours=2),
            elevation_gain=700,
            rpe=7,
            title="Long Ride",
        ),
        create_workout(
            sport="Running",
            workout_date=date.today() - timedelta(days=3),
            distance=10,
            duration=timedelta(minutes=52),
            elevation_gain=160,
            rpe=6,
            title="Steady Run",
        ),
        create_workout(
            sport="Running",
            workout_date=date.today(),
            distance=16,
            duration=timedelta(hours=1, minutes=25),
            elevation_gain=320,
            rpe=8,
            title="Long Run",
        ),
    ]

    for workout in demo_workouts:
        athlete.history.add(workout)

    today = date.today()
    monday = today - timedelta(days=today.weekday())

    athlete.training_plan.schedule(
    scheduled_at=datetime.combine(
            monday,
            time(hour=18),
        ),
        sport="Running",
        title="Easy Run",
        duration=timedelta(minutes=45),
        description="Easy aerobic run",
    )

    athlete.training_plan.schedule(
        scheduled_at=datetime.combine(
            monday + timedelta(days=2),
            time(hour=18),
        ),
        sport="Running",
        title="Intervals",
        duration=timedelta(minutes=60),
        description="6 × 800 m",
    )

    athlete.training_plan.schedule(
        scheduled_at=datetime.combine(
            monday + timedelta(days=5),
            time(hour=8),
        ),
        sport="Running",
        title="Long Run",
        duration=timedelta(minutes=90),
        description="Long endurance run",
    )

    return athlete


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

    st.logout()

def initialize_session_state() -> None:
    """
    Initialize the Streamlit application state.
    """

    # --------------------------------------------------
    # Development user
    # --------------------------------------------------

    if not user_repository.list():

        existing_athletes = athlete_repository.list()

        if existing_athletes:
            demo_athlete = existing_athletes[0]

        else:
            demo_athlete = create_demo_athlete()

            athlete_repository.save(
                demo_athlete
            )

        athlete_user = User(
            email="demo@performancelab.local",
            role="athlete",
            athlete_id=demo_athlete.athlete_id,
        )

        user_repository.save(
            athlete_user
        )

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
                )
            )
            .execute(
                current_user
            )
        )

        st.session_state.athlete = (
            load_result.athlete
        )

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
        )
    )

    if activities_changed:

        athlete_repository.save(
            athlete
        )
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
        athlete
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