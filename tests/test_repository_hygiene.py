"""
PerformanceLab

Repository hygiene tests.
"""

from pathlib import (
    Path,
)


PROJECT_ROOT = (
    Path(__file__).parents[1]
)

GITIGNORE_PATH = (
    PROJECT_ROOT
    / ".gitignore"
)


def gitignore_entries():

    return {
        line.strip()
        for line in (
            GITIGNORE_PATH
            .read_text(
                encoding="utf-8"
            )
            .splitlines()
        )
        if line.strip()
        and not line.startswith("#")
    }


def test_gitignore_protects_local_data():

    entries = gitignore_entries()

    assert "data/" in entries


def test_gitignore_protects_secrets():

    entries = gitignore_entries()

    required_entries = {
        ".env",
        ".env.*",
        "!.env.example",
        ".streamlit/secrets.toml",
        "*.pem",
        "*.key",
        "credentials*.json",
        "service-account*.json",
    }

    assert required_entries <= entries


def test_gitignore_protects_test_artifacts():

    entries = gitignore_entries()

    required_entries = {
        ".coverage",
        ".coverage.*",
        "coverage.xml",
        "htmlcov/",
        ".pytest_cache/",
    }

    assert required_entries <= entries


def test_gitignore_protects_backups():

    entries = gitignore_entries()

    required_entries = {
        "backups/",
        "*.backup",
        "*.dump",
        "*.bak",
        "*_backup.sql",
    }

    assert required_entries <= entries


def test_gitignore_protects_exports_and_patches():

    entries = gitignore_entries()

    required_entries = {
        "exports/",
        "PLANO_DE_TREINO.txt",
        "project_tree.txt",
        "*.patch",
        "patches/",
        "docs/HANDOUT_*.md",
    }

    assert required_entries <= entries