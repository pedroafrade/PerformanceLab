"""Contract checks for the private-alpha invitation administration script."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_listing_script_executes_job_and_reads_its_logs():
    source = (
        ROOT
        / "scripts"
        / "list_google_alpha_users.ps1"
    ).read_text(encoding="utf-8")

    assert "run jobs execute" in source
    assert "--args=--list" in source
    assert "jobs executions logs read" in source
    assert "--order=asc" in source


def test_invitation_script_accepts_any_valid_email_address():
    source = (ROOT / "scripts" / "invite_google_alpha_user.ps1").read_text()
    assert "Provide a valid Google account email address." not in source
    assert "Provide a valid email address." in source
