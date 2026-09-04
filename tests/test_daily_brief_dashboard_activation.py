from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_app_gates_automatic_resolution_before_provider_path():
    source = (ROOT / "app/app.py").read_text(encoding="utf-8")
    gate = source.index("daily_brief_attempt_key is not None")
    resolution = source.index("DailyBriefCoordinator(", gate)
    segment = source[gate:resolution]
    assert "training_coach_permitted" in segment
    assert "daily_brief_runtime_settings.permits(current_user.user_id)" in segment
    assert "daily_brief_generation_service is not None" in segment
    assert "repository_bundle.engine is not None" in segment


def test_missing_timezone_does_not_call_coordinator():
    source = (ROOT / "app/app.py").read_text(encoding="utf-8")
    preference = source.index("timezone_preference =")
    guard = source.index("daily_brief_attempt_key is not None", preference)
    coordinator = source.index("DailyBriefCoordinator(", guard)
    assert preference < guard < coordinator


def test_dashboard_keeps_local_guidance_fallback():
    source = (
        ROOT / "app/components/dashboard/dashboard_view.py"
    ).read_text(encoding="utf-8")
    assert 'getattr(daily_brief_resolution, "narrative", None)' in source
    assert "TodayPresenter(athlete)" in source
    assert "This guidance does not change your training plan." in source
