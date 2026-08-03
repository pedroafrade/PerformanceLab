"""
Tests for text normalization.
"""

import pytest

from performancelab.text import (
    repair_mojibake,
)


def test_repairs_portuguese_mojibake():

    assert repair_mojibake(
        "T75_RecuperaÃ§Ã£o"
    ) == "T75_Recuperação"


def test_repairs_repeated_mojibake():

    assert repair_mojibake(
        "RecuperaÃƒÂ§ÃƒÂ£o"
    ) == "Recuperação"


def test_preserves_correct_portuguese_text():

    assert repair_mojibake(
        "Recuperação fácil"
    ) == "Recuperação fácil"


def test_preserves_plain_text():

    assert repair_mojibake(
        "Morning Run"
    ) == "Morning Run"


def test_requires_string():

    with pytest.raises(
        TypeError
    ):
        repair_mojibake(
            None
        )