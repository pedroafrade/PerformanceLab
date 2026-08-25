"""
PerformanceLab

README setup documentation tests.
"""

from pathlib import (
    Path,
)


README_PATH = (
    Path(__file__).parents[1]
    / "README.md"
)


def readme_text():

    text = README_PATH.read_text(
        encoding="utf-8"
    )

    return " ".join(
        text.split()
    )


def test_readme_uses_pyproject_as_dependency_source():

    text = readme_text()

    assert "`pyproject.toml`" in text
    assert (
        'python -m pip install -e ".[test]"'
        in text
    )
    assert "requirements.txt" not in text


def test_readme_records_supported_python_versions():

    text = readme_text()

    for version in (
        "3.11",
        "3.12",
        "3.13",
        "3.14",
    ):

        assert version in text


def test_readme_separates_local_and_alpha_storage():

    text = readme_text()

    assert (
        "JSON exclusivamente para desenvolvimento local"
        in text
    )
    assert (
        "PostgreSQL obrigatório nos ambientes "
        "de teste e alpha"
        in text
    )
    assert (
        'PERFORMANCELAB_ENV = "local"'
        in text
    )


def test_readme_records_current_security_boundaries():

    text = readme_text()

    required_boundaries = (
        "autenticação externa por OIDC",
        "convites individuais",
        "autorização e isolamento",
        "Segredos e valores reais",
    )

    for boundary in required_boundaries:

        assert boundary in text


def test_readme_uses_short_pytest_commands():

    text = readme_text()

    assert (
        "pytest -q tests/test_application_health.py"
        in text
    )
    assert "pytest -q" in text


def test_readme_preserves_external_blockers():

    text = readme_text()

    blockers = (
        "revisão jurídica externa",
        "alojamento privado da aplicação",
        "backups automáticos",
        "restauro real testado",
        "testes internos no deployment",
    )

    for blocker in blockers:

        assert blocker in text