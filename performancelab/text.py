"""
PerformanceLab

Text normalization utilities.
"""


_MOJIBAKE_MARKERS = (
    "Ã",
    "Â",
    "â",
    "ðŸ",
    "ï»¿",
    "�",
)


def _mojibake_score(
    value: str,
) -> int:
    """
    Counts common signs of incorrectly decoded UTF-8 text.
    """

    return sum(
        value.count(marker)
        for marker in _MOJIBAKE_MARKERS
    )


def repair_mojibake(
    value: str,
) -> str:
    """
    Repairs common UTF-8 text decoded as Latin-1 or CP1252.

    Text is only replaced when the candidate contains fewer
    mojibake markers than the original.
    """

    if not isinstance(
        value,
        str,
    ):
        raise TypeError(
            "value must be a string."
        )

    result = value

    for _ in range(3):

        current_score = (
            _mojibake_score(
                result
            )
        )

        if current_score == 0:
            break

        candidates = []

        for encoding in (
            "latin-1",
            "cp1252",
        ):

            try:

                candidate = (
                    result
                    .encode(encoding)
                    .decode("utf-8")
                )

            except (
                UnicodeEncodeError,
                UnicodeDecodeError,
            ):
                continue

            candidates.append(
                candidate
            )

        if not candidates:
            break

        candidate = min(
            candidates,
            key=_mojibake_score,
        )

        if (
            _mojibake_score(
                candidate
            )
            >= current_score
        ):
            break

        result = candidate

    return result