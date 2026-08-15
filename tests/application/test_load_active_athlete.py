from datetime import (
    date,
)

import pytest

from performancelab.application import (
    LoadActiveAthlete,
)
from performancelab.athlete import (
    Athlete,
)
from performancelab.athlete_access import (
    AthleteAccessGrant,
)
from performancelab.authorization import (
    AthleteAuthorizationService,
)
from performancelab.identity import (
    User,
)
from performancelab.storage.in_memory_athlete_repository import (
    InMemoryAthleteRepository,
)
from performancelab.storage.json_athlete_access_repository import (
    JsonAthleteAccessRepository,
)
from performancelab.training.planning import (
    TrainingPlan,
)


class RecordingAthleteRepository(
    InMemoryAthleteRepository
):

    def __init__(
        self,
        athletes=(),
    ) -> None:

        self.save_calls = 0

        super().__init__(
            athletes
        )

        self.save_calls = 0

    def save(
        self,
        athlete,
    ) -> None:

        self.save_calls += 1

        super().save(
            athlete
        )


class FakeReconciler:

    def __init__(
        self,
        *,
        replacement_plan=None,
    ) -> None:

        self.replacement_plan = (
            replacement_plan
        )

        self.call = None

    def reconcile_closed_days(
        self,
        *,
        plan,
        history,
        training_state,
        today=None,
    ):

        self.call = {
            "plan": plan,
            "history": history,
            "training_state": (
                training_state
            ),
            "today": today,
        }

        if (
            self.replacement_plan
            is not None
        ):
            return self.replacement_plan

        return plan


def athlete_user(
    athlete,
    *,
    email="pedro@example.com",
):

    return User(
        email=email,
        role="athlete",
        athlete_id=(
            athlete.athlete_id
        ),
    )


def owner_grant(
    user,
    athlete,
):

    return AthleteAccessGrant(
        user_id=user.user_id,
        athlete_id=athlete.athlete_id,
        permission="owner",
    )


def build_loader(
    tmp_path,
    repository,
    *,
    grants=(),
    reconciler=None,
):

    access_repository = (
        JsonAthleteAccessRepository(
            tmp_path
            / "athlete_access"
        )
    )

    for grant in grants:

        access_repository.save(
            grant
        )

    return LoadActiveAthlete(
        repository=repository,
        authorization=(
            AthleteAuthorizationService(
                access_repository
            )
        ),
        reconciler=reconciler,
    )


def test_loads_only_athlete_associated_with_user(
    tmp_path,
):

    pedro = Athlete(
        name="Pedro"
    )

    maria = Athlete(
        name="Maria"
    )

    user = athlete_user(
        maria,
        email="maria@example.com",
    )

    repository = (
        RecordingAthleteRepository(
            (
                pedro,
                maria,
            )
        )
    )

    result = build_loader(
        tmp_path,
        repository,
        grants=(
            owner_grant(
                user,
                maria,
            ),
        ),
        reconciler=FakeReconciler(),
    ).execute(
        user,
        today=date(
            2026,
            8,
            15,
        ),
    )

    assert (
        result.athlete.athlete_id
        == maria.athlete_id
    )

    assert (
        result.athlete.name
        == "Maria"
    )


def test_passes_loaded_domain_state_to_reconciler(
    tmp_path,
):

    athlete = Athlete(
        name="Pedro"
    )

    user = athlete_user(
        athlete
    )

    repository = (
        RecordingAthleteRepository(
            (
                athlete,
            )
        )
    )

    reconciler = FakeReconciler()

    reference_day = date(
        2026,
        8,
        15,
    )

    result = build_loader(
        tmp_path,
        repository,
        grants=(
            owner_grant(
                user,
                athlete,
            ),
        ),
        reconciler=reconciler,
    ).execute(
        user,
        today=reference_day,
    )

    assert (
        reconciler.call["plan"]
        is result.athlete.training_plan
    )

    assert (
        reconciler.call["history"]
        is result.athlete.history
    )

    assert (
        reconciler.call["today"]
        == reference_day
    )

    assert (
        reconciler.call[
            "training_state"
        ]
        is not None
    )


def test_does_not_save_when_plan_is_unchanged(
    tmp_path,
):

    athlete = Athlete(
        name="Pedro"
    )

    user = athlete_user(
        athlete
    )

    repository = (
        RecordingAthleteRepository(
            (
                athlete,
            )
        )
    )

    result = build_loader(
        tmp_path,
        repository,
        grants=(
            owner_grant(
                user,
                athlete,
            ),
        ),
        reconciler=FakeReconciler(),
    ).execute(
        user
    )

    assert result.plan_changed is False
    assert repository.save_calls == 0


def test_saves_when_reconciliation_replaces_plan(
    tmp_path,
):

    athlete = Athlete(
        name="Pedro"
    )

    user = athlete_user(
        athlete
    )

    replacement_plan = (
        TrainingPlan()
    )

    repository = (
        RecordingAthleteRepository(
            (
                athlete,
            )
        )
    )

    result = build_loader(
        tmp_path,
        repository,
        grants=(
            owner_grant(
                user,
                athlete,
            ),
        ),
        reconciler=FakeReconciler(
            replacement_plan=(
                replacement_plan
            )
        ),
    ).execute(
        user
    )

    stored = repository.get(
        athlete.athlete_id
    )

    assert result.plan_changed is True
    assert repository.save_calls == 1

    assert (
        result.athlete.training_plan
        is replacement_plan
    )

    assert (
        stored.training_plan
        is not replacement_plan
    )


def test_missing_athlete_raises_after_authorization(
    tmp_path,
):

    missing_athlete = Athlete(
        name="Missing"
    )

    user = athlete_user(
        missing_athlete
    )

    repository = (
        RecordingAthleteRepository()
    )

    with pytest.raises(
        FileNotFoundError,
        match="does not exist",
    ):
        build_loader(
            tmp_path,
            repository,
            grants=(
                owner_grant(
                    user,
                    missing_athlete,
                ),
            ),
            reconciler=FakeReconciler(),
        ).execute(
            user
        )


def test_missing_access_grant_is_rejected(
    tmp_path,
):

    athlete = Athlete(
        name="Pedro"
    )

    user = athlete_user(
        athlete
    )

    repository = (
        RecordingAthleteRepository(
            (
                athlete,
            )
        )
    )

    with pytest.raises(
        PermissionError,
        match="not authorized",
    ):
        build_loader(
            tmp_path,
            repository,
            reconciler=FakeReconciler(),
        ).execute(
            user
        )


def test_user_cannot_load_another_athlete(
    tmp_path,
):

    pedro = Athlete(
        name="Pedro"
    )

    maria = Athlete(
        name="Maria"
    )

    user = athlete_user(
        maria,
        email="maria@example.com",
    )

    repository = (
        RecordingAthleteRepository(
            (
                pedro,
                maria,
            )
        )
    )

    with pytest.raises(
        PermissionError,
        match="not authorized",
    ):
        build_loader(
            tmp_path,
            repository,
            grants=(
                AthleteAccessGrant(
                    user_id=user.user_id,
                    athlete_id=pedro.athlete_id,
                    permission="owner",
                ),
            ),
            reconciler=FakeReconciler(),
        ).execute(
            user
        )


def test_coach_grant_is_not_accepted_for_alpha_owner(
    tmp_path,
):

    athlete = Athlete(
        name="Pedro"
    )

    user = athlete_user(
        athlete
    )

    repository = (
        RecordingAthleteRepository(
            (
                athlete,
            )
        )
    )

    with pytest.raises(
        PermissionError,
        match="permission_not_allowed",
    ):
        build_loader(
            tmp_path,
            repository,
            grants=(
                AthleteAccessGrant(
                    user_id=user.user_id,
                    athlete_id=athlete.athlete_id,
                    permission="coach",
                ),
            ),
            reconciler=FakeReconciler(),
        ).execute(
            user
        )


def test_coach_account_cannot_load_any_athlete(
    tmp_path,
):

    pedro = Athlete(
        name="Pedro"
    )

    maria = Athlete(
        name="Maria"
    )

    coach = User(
        email="coach@example.com",
        role="coach",
    )

    repository = (
        RecordingAthleteRepository(
            (
                pedro,
                maria,
            )
        )
    )

    with pytest.raises(
        PermissionError,
        match="Only athlete accounts",
    ):
        build_loader(
            tmp_path,
            repository,
            grants=(
                AthleteAccessGrant(
                    user_id=coach.user_id,
                    athlete_id=pedro.athlete_id,
                    permission="coach",
                ),
            ),
            reconciler=FakeReconciler(),
        ).execute(
            coach
        )


def test_rejects_invalid_user(
    tmp_path,
):

    repository = (
        RecordingAthleteRepository()
    )

    with pytest.raises(
        TypeError,
        match="user must be a User",
    ):
        build_loader(
            tmp_path,
            repository,
            reconciler=FakeReconciler(),
        ).execute(
            None
        )