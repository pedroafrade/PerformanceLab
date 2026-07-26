"""
PerformanceLab

Next workout dashboard card.
"""

from __future__ import annotations

from datetime import timedelta
from html import escape
from textwrap import dedent

import streamlit as st

from performancelab.presentation.dashboard_models import (
    NextWorkoutData,
)


def next_workout_card(
    workout: NextWorkoutData | None,
) -> None:
    """
    Displays the next planned workout and its executable steps.
    """

    if workout is None:
        st.caption(
            "No upcoming workout."
        )
        return

    steps = "".join(
        _workout_step(
            index=index,
            step=step,
        )
        for index, step in enumerate(
            workout.structure,
            start=1,
        )
    )

    objective = ""

    if workout.objective:
        objective = f"""
            <section class="next-workout-context">
                <div class="next-workout-label">
                    Objective
                </div>
                <div class="next-workout-objective">
                    {escape(workout.objective)}
                </div>
            </section>
        """

    html = dedent(
        f"""
        <style>
            .next-workout-card {{
                width: 100%;
            }}

            .next-workout-heading {{
                margin-bottom: 0.7rem;
            }}

            .next-workout-title {{
                font-size: 1rem;
                font-weight: 700;
                line-height: 1.25;
            }}

            .next-workout-meta {{
                margin-top: 0.18rem;
                color: rgba(49, 51, 63, 0.66);
                font-size: 0.74rem;
                line-height: 1.3;
            }}

            .next-workout-steps {{
                display: flex;
                flex-direction: column;
                gap: 0.45rem;
            }}

            .next-workout-step {{
                display: flex;
                align-items: flex-start;
                gap: 0.55rem;
                padding: 0.5rem 0.55rem;
                border-radius: 0.5rem;
                background: rgba(49, 51, 63, 0.035);
            }}

            .next-workout-step-number {{
                display: flex;
                flex: 0 0 1.35rem;
                width: 1.35rem;
                height: 1.35rem;
                align-items: center;
                justify-content: center;
                border: 1px solid rgba(49, 51, 63, 0.22);
                border-radius: 50%;
                font-size: 0.66rem;
                font-weight: 700;
                line-height: 1;
            }}

            .next-workout-step-text {{
                padding-top: 0.03rem;
                font-size: 0.78rem;
                line-height: 1.35;
            }}

            .next-workout-context {{
                margin-top: 0.75rem;
                padding-top: 0.65rem;
                border-top: 1px solid rgba(49, 51, 63, 0.14);
            }}

            .next-workout-label {{
                color: rgba(49, 51, 63, 0.62);
                font-size: 0.66rem;
                font-weight: 700;
                letter-spacing: 0.05em;
                text-transform: uppercase;
            }}

            .next-workout-objective {{
                margin-top: 0.22rem;
                font-size: 0.76rem;
                line-height: 1.4;
            }}
        </style>

        <div class="next-workout-card">
            <header class="next-workout-heading">
                <div class="next-workout-title">
                    {escape(workout.title or "Planned workout")}
                </div>
                <div class="next-workout-meta">
                    {escape(_metadata(workout))}
                </div>
            </header>

            <div class="next-workout-steps">
                {steps}
            </div>

            {objective}
        </div>
        """
    ).strip()

    st.html(
        html
    )

    if workout.description:
        _show_coaching_notes(
            workout.description
        )


def _show_coaching_notes(
    description: str,
) -> None:
    """
    Displays coaching notes in a floating popover.

    The popover overlays the dashboard and therefore does not
    change the position or height of the surrounding widgets.
    """

    with st.popover(
        "Coaching notes",
        use_container_width=True,
    ):
        st.markdown(
            """
            <style>
                div[data-testid="stPopoverBody"] {
                    width: min(28rem, calc(100vw - 3rem));
                    min-width: min(24rem, calc(100vw - 3rem));
                    max-width: 28rem;
                    max-height: min(58vh, 32rem);
                    overflow-y: auto;
                    padding: 0.7rem 0.8rem;
                }

                div[data-testid="stPopoverBody"] h3 {
                    margin: 0 0 0.5rem;
                    font-size: 0.92rem;
                    line-height: 1.2;
                }

                div[data-testid="stPopoverBody"]
                .coaching-notes-list {
                    display: flex;
                    flex-direction: column;
                    gap: 0.28rem;
                }

                div[data-testid="stPopoverBody"]
                .coaching-note {
                    padding: 0.38rem 0.5rem;
                    border-radius: 0.35rem;
                    background: rgba(49, 51, 63, 0.04);
                    font-size: 0.78rem;
                    line-height: 1.35;
                }

                @media (max-width: 700px) {
                    div[data-testid="stPopoverBody"] {
                        width: calc(100vw - 2rem);
                        min-width: 0;
                        max-width: calc(100vw - 2rem);
                    }
                }
            </style>
            """,
            unsafe_allow_html=True,
        )

        notes = "".join(
            (
                '<div class="coaching-note">'
                f"{escape(note)}"
                "</div>"
            )
            for note in _coaching_notes(
                description
            )
        )

        st.html(
            f"""
            <section class="coaching-notes-content">
                <h3>Coaching notes</h3>
                <div class="coaching-notes-list">
                    {notes}
                </div>
            </section>
            """
        )


def _coaching_notes(
    description: str,
) -> tuple[str, ...]:
    """
    Converts the coaching description into paragraph cards.

    Paragraphs separated by blank lines remain grouped in the
    same card. Single-line legacy descriptions fall back to
    sentence grouping.
    """

    if not isinstance(
        description,
        str,
    ):
        raise TypeError(
            "description must be a string"
        )

    cleaned = description.strip()

    if not cleaned:
        return ()

    paragraphs = tuple(
        _normalize_coaching_paragraph(
            paragraph
        )
        for paragraph in cleaned.split("\n\n")
        if paragraph.strip()
    )

    if len(paragraphs) > 1:
        return paragraphs

    return _group_coaching_sentences(
        cleaned
    )

def _normalize_coaching_paragraph(
    paragraph: str,
) -> str:
    """
    Removes unnecessary whitespace without destroying the
    paragraph structure.
    """

    return " ".join(
        paragraph.split()
    )

def _group_coaching_sentences(
    description: str,
    *,
    sentences_per_note: int = 2,
) -> tuple[str, ...]:
    """
    Groups legacy single-line descriptions into compact notes.
    """

    sentences = _coaching_sentences(
        description
    )

    notes: list[str] = []

    for index in range(
        0,
        len(sentences),
        sentences_per_note,
    ):
        note = " ".join(
            sentences[
                index:
                index + sentences_per_note
            ]
        ).strip()

        if note:
            notes.append(
                note
            )

    return tuple(
        notes
    )


def _coaching_sentences(
    description: str,
) -> tuple[str, ...]:
    """
    Splits text into sentences while retaining punctuation.
    """

    normalized = " ".join(
        description.split()
    )

    if not normalized:
        return ()

    sentences: list[str] = []
    current: list[str] = []

    for character in normalized:
        current.append(
            character
        )

        if character in ".!?":
            sentence = "".join(
                current
            ).strip()

            if sentence:
                sentences.append(
                    sentence
                )

            current = []

    remaining = "".join(
        current
    ).strip()

    if remaining:
        sentences.append(
            remaining
        )

    return tuple(
        sentences
    )

def _workout_step(
    *,
    index: int,
    step: str,
) -> str:
    return f"""
        <div class="next-workout-step">
            <div class="next-workout-step-number">
                {index}
            </div>
            <div class="next-workout-step-text">
                {escape(step)}
            </div>
        </div>
    """


def _metadata(
    workout: NextWorkoutData,
) -> str:
    values = [
        value
        for value in (
            workout.sport,
            _duration_label(
                workout.duration
            ),
            workout.intensity,
        )
        if value
    ]

    return " · ".join(
        values
    )


def _duration_label(
    duration: timedelta | None,
) -> str | None:
    if duration is None:
        return None

    total_minutes = round(
        duration.total_seconds() / 60
    )

    hours, minutes = divmod(
        total_minutes,
        60,
    )

    if hours and minutes:
        return f"{hours}h {minutes:02d}m"

    if hours:
        return f"{hours}h"

    return f"{minutes} min"