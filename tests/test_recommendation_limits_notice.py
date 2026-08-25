"""
Tests for recommendation limits shown before participation.
"""

import ast

from pathlib import (
    Path,
)


PROJECT_ROOT = (
    Path(__file__).parent.parent
)


def source_text(
    relative_path: str,
) -> str:

    return (
        PROJECT_ROOT
        / relative_path
    ).read_text(
        encoding="utf-8"
    )


def python_visible_text(
    relative_path: str,
) -> str:
    """
    Collect complete string constants from a Python file.
    """

    tree = ast.parse(
        source_text(
            relative_path
        )
    )

    return "\n".join(
        node.value
        for node in ast.walk(
            tree
        )
        if (
            isinstance(
                node,
                ast.Constant,
            )
            and isinstance(
                node.value,
                str,
            )
        )
    )


def test_alpha_notice_discloses_recommendation_limits():

    text = python_visible_text(
        "app/components/"
        "alpha_participation_consent.py"
    )

    assert (
        "recommendations may change "
        "and may contain errors"
        in text
    )

    assert (
        "Training recommendations support "
        "training decisions and are not medical advice"
        in text
    )


def test_training_coach_repeats_its_specific_limit():

    text = python_visible_text(
        "app/components/"
        "training_coach_consent.py"
    )

    assert (
        "supports training decisions "
        "and is not medical advice"
        in text
    )


def test_privacy_policy_documents_automated_limits():

    text = source_text(
        "docs/PRIVACY_POLICY_ALPHA_DRAFT.md"
    )

    required_limits = (
        "não substituem avaliação humana",
        "não constituem aconselhamento médico",
        "podem conter erros, omissões "
        "ou interpretações inadequadas",
    )

    for limit in required_limits:

        assert limit in text