from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_activity_gemini_request_has_one_attempt_and_sixty_second_timeout():
    source = (
        ROOT
        / "performancelab"
        / "integrations"
        / "gemini_activity_coach.py"
    ).read_text(encoding="utf-8")

    assert '"timeout": 60000' in source
    assert '"retry_options": {"attempts": 1}' in source


def test_postgresql_runtime_uses_shared_quota_but_local_runtime_does_not():
    source = (ROOT / "app" / "app.py").read_text(encoding="utf-8")

    assert "TrainingCoachQuotaStore(repository_bundle.engine)" in source
    assert "if repository_bundle.uses_postgresql else None" in source
