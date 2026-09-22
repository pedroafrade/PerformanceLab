"""Safety checks for the private-alpha Google login bootstrap helper."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "configure_google_alpha_oidc.ps1"
README = ROOT / "infra" / "google-alpha" / "README.md"


def source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_oidc_bootstrap_keeps_secrets_out_of_files_and_arguments():
    script = source(SCRIPT)

    assert 'Read-Host "Google OAuth client secret" -AsSecureString' in script
    assert 'Read-Host "Repeat the Google OAuth client secret" -AsSecureString' in script
    assert "RandomNumberGenerator]::Create()" in script
    assert "$randomGenerator.GetBytes($cookieBytes)" in script
    assert "$randomGenerator.Dispose()" in script
    assert "RandomNumberGenerator]::Fill" not in script
    assert "Invoke-RestMethod" in script
    assert "Set-Content" not in script
    assert "Out-File" not in script
    assert "--data-file" not in script


def test_oidc_bootstrap_targets_expected_alpha_resources_and_redirect():
    script = source(SCRIPT)

    assert 'ProjectId = "performancelab-private-alpha"' in script
    assert 'SecretId = "performancelab-alpha-oidc-toml"' in script
    assert '"$normalizedUrl/oauth2callback"' in script
    assert 'PERFORMANCELAB_ENV = "alpha"' in script
    assert "https://accounts.google.com/.well-known/openid-configuration" in script


def test_oidc_bootstrap_requires_explicit_rotation_and_documents_usage():
    script = source(SCRIPT)
    readme = source(README)

    assert "[switch]$RotateExisting" in script
    assert "$enabledVersions.Count -gt 0 -and -not $RotateExisting" in script
    assert "configure_google_alpha_oidc.ps1" in readme
    assert "Não utilize `-RotateExisting`" in readme


def test_oidc_bootstrap_treats_a_secret_without_versions_as_empty():
    script = source(SCRIPT)

    assert "$enabledVersions = @()" in script
    assert '$versions.PSObject.Properties["versions"]' in script
    assert "$null -ne $versionsProperty.Value" in script
    assert '$_.state -eq "ENABLED"' in script
    assert "$enabledVersions = @($versions.versions)" not in script
