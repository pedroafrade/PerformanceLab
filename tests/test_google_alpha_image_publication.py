"""Safety checks for publishing the private-alpha container image."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "publish_google_alpha_image.ps1"
BUILD = ROOT / "infra" / "google-alpha" / "cloudbuild.yaml"
GCLOUDIGNORE = ROOT / ".gcloudignore"


def source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_cloud_build_labels_and_publishes_the_exact_commit():
    build = source(BUILD)

    assert '"VCS_REF=${_VCS_REF}"' in build
    assert '"${_IMAGE}"' in build
    assert "images:" in build
    assert "docker push" not in build


def test_publication_requires_clean_synchronised_main():
    script = source(SCRIPT)

    assert 'branch -ne "main"' in script
    assert "git status --porcelain --untracked-files=all" in script
    assert '@("fetch", "--quiet", "origin", "main")' in script
    assert "$commit -ne $remoteCommit" in script
    assert '"--region=$Region"' in script


def test_publication_returns_and_validates_an_immutable_reference():
    script = source(SCRIPT)

    assert '"--format=value(image_summary.digest)"' in script
    assert '"^sha256:[0-9a-f]{64}$"' in script
    assert "$env:DEPLOYMENT_IMAGE_REFERENCE = $immutableReference" in script
    assert "scripts/check_alpha_image_reference.py" in script
    assert "Immutable image reference:" in script


def test_cloud_submission_excludes_local_and_sensitive_content():
    ignore = source(GCLOUDIGNORE)

    assert "#!include:.gitignore" in ignore
    assert ".git" in ignore
    assert "tests/" in ignore
    assert "docs/" in ignore
