"""Safety checks for the private-alpha database bootstrap helper."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "configure_google_alpha_database.ps1"
README = ROOT / "infra" / "google-alpha" / "README.md"


def source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_database_bootstrap_keeps_credentials_out_of_files_and_arguments():
    script = source(SCRIPT)

    assert 'Read-Host "Database password" -AsSecureString' in script
    assert 'Read-Host "Repeat the database password" -AsSecureString' in script
    assert "Invoke-RestMethod" in script
    assert "--password" not in script
    assert "Set-Content" not in script
    assert "Out-File" not in script
    assert '"${usersUri}?name=$escapedUser"' in script
    assert '"$usersUri?name=$escapedUser"' not in script


def test_database_bootstrap_targets_the_expected_private_alpha_resources():
    script = source(SCRIPT)

    assert 'ProjectId = "performancelab-private-alpha"' in script
    assert 'InstanceId = "performancelab-alpha"' in script
    assert 'DatabaseName = "performancelab"' in script
    assert 'DatabaseUser = "performancelab_app"' in script
    assert 'SecretId = "performancelab-alpha-database-url"' in script
    assert '"postgresql+psycopg://' in script
    assert '"/cloudsql/$ConnectionName"' in script


def test_database_bootstrap_requires_explicit_rotation_and_documents_usage():
    script = source(SCRIPT)
    readme = source(README)

    assert "[switch]$RotateExisting" in script
    assert "$userExists -and -not $RotateExisting" in script
    assert "configure_google_alpha_database.ps1" in readme
    assert "Não utilize `-RotateExisting`" in readme
