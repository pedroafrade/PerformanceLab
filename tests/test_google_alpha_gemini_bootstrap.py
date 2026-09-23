"""Safety checks for the private-alpha Gemini key helper."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "configure_google_alpha_gemini.ps1"


def source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_gemini_helper_keeps_api_key_out_of_files_and_arguments():
    script = source(SCRIPT)

    assert 'Read-Host "Gemini API key" -AsSecureString' in script
    assert 'Read-Host "Repeat the Gemini API key" -AsSecureString' in script
    assert "Invoke-RestMethod" in script
    assert "Set-Content" not in script
    assert "Out-File" not in script
    assert "--data-file" not in script


def test_gemini_helper_targets_expected_secret_and_handles_empty_vault():
    script = source(SCRIPT)

    assert 'ProjectId = "performancelab-private-alpha"' in script
    assert 'SecretId = "performancelab-alpha-gemini-api-key"' in script
    assert "$enabledVersions = @()" in script
    assert '$versions.PSObject.Properties["versions"]' in script
    assert '$_.state -eq "ENABLED"' in script


def test_gemini_helper_requires_explicit_rotation_and_is_documented():
    script = source(SCRIPT)

    assert "[switch]$RotateExisting" in script
    assert "$enabledVersions.Count -gt 0 -and -not $RotateExisting" in script
