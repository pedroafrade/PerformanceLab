"""
PerformanceLab

Project dependency configuration tests.
"""

from pathlib import Path
import tomllib


PROJECT_ROOT = Path(__file__).parents[1]
PYPROJECT_PATH = PROJECT_ROOT / "pyproject.toml"
REQUIREMENTS_PATH = PROJECT_ROOT / "requirements.txt"
POLICY_PATH = (
    PROJECT_ROOT
    / "docs"
    / "DEPENDENCY_POLICY.md"
)


def project_configuration() -> dict:

    with PYPROJECT_PATH.open("rb") as source:

        return tomllib.load(source)


def dependency_name(requirement: str) -> str:

    name = requirement.split("[", 1)[0]

    for separator in ("<", ">", "=", "!", "~"):

        name = name.split(separator, 1)[0]

    return name.strip().lower()


def test_pyproject_contains_all_runtime_dependencies():

    configuration = project_configuration()

    requirements = configuration["project"]["dependencies"]

    names = {
        dependency_name(requirement)
        for requirement in requirements
    }

    assert names == {
        "alembic",
        "fitdecode",
        "google-genai",
        "gpxpy",
        "matplotlib",
        "numpy",
        "pandas",
        "plotly",
        "psycopg",
        "scipy",
        "sqlalchemy",
        "streamlit",
    }


def test_runtime_dependencies_have_version_bounds():

    configuration = project_configuration()

    requirements = configuration["project"]["dependencies"]

    for requirement in requirements:

        assert ">=" in requirement
        assert "<" in requirement


def test_supported_python_versions_are_bounded():

    configuration = project_configuration()

    assert (
        configuration["project"]["requires-python"]
        == ">=3.11,<3.15"
    )


def test_pytest_is_a_test_dependency():

    configuration = project_configuration()

    test_dependencies = (
        configuration["project"]
        ["optional-dependencies"]
        ["test"]
    )

    assert test_dependencies == [
        "pytest>=8.3,<10",
    ]


def test_requirements_file_is_not_duplicated():

    assert not REQUIREMENTS_PATH.exists()


def test_dependency_policy_records_installation_commands():

    text = POLICY_PATH.read_text(encoding="utf-8")

    assert "pyproject.toml" in text
    assert 'python -m pip install -e .' in text
    assert 'python -m pip install -e ".[test]"' in text
    assert "ambiente limpo" in text