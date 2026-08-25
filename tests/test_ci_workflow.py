"""
PerformanceLab

Continuous integration workflow tests.
"""

from pathlib import Path


PROJECT_ROOT = Path(__file__).parents[1]
WORKFLOW_PATH = (
    PROJECT_ROOT
    / ".github"
    / "workflows"
    / "ci.yml"
)


def workflow_text() -> str:

    return WORKFLOW_PATH.read_text(
        encoding="utf-8",
    )


def test_ci_runs_for_main_and_pull_requests():

    text = workflow_text()

    assert "push:" in text
    assert "branches:" in text
    assert "- main" in text
    assert "pull_request:" in text


def test_ci_uses_supported_python_versions():

    text = workflow_text()

    assert '- "3.11"' in text
    assert '- "3.14"' in text
    assert "actions/setup-python@v5" in text


def test_ci_installs_from_pyproject():

    text = workflow_text()

    assert (
        'python -m pip install -e ".[test]"'
        in text
    )

    assert (
        "cache-dependency-path: pyproject.toml"
        in text
    )

    assert "requirements.txt" not in text


def test_ci_runs_static_check_and_full_pytest():

    text = workflow_text()

    assert (
        "python -m compileall -q "
        "app performancelab migrations"
        in text
    )

    assert "run: pytest -q" in text


def test_ci_uses_read_only_repository_permission():

    text = workflow_text()

    assert "permissions:" in text
    assert "contents: read" in text

def test_ci_builds_container_without_publishing():

    text = workflow_text()

    assert "container:" in text
    assert "name: Docker image" in text
    assert (
        "docker build --tag "
        "performancelab-alpha:ci ."
        in text
    )
    assert "docker push" not in text
    assert "gcloud" not in text

def test_ci_verifies_container_health():

    text = workflow_text()

    assert (
        "--name performancelab-alpha-ci"
        in text
    )
    assert (
        "--env PERFORMANCELAB_ENV=local"
        in text
    )
    assert (
        "http://127.0.0.1:8080/"
        "_stcore/health"
        in text
    )
    assert "--retry-connrefused" in text
    assert "if: always()" in text
    assert (
        "docker rm --force "
        "performancelab-alpha-ci"
        in text
    )