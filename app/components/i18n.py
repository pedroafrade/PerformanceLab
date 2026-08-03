"""
PerformanceLab

Lightweight user-interface internationalisation.
"""

from __future__ import annotations

import streamlit as st


DEFAULT_LANGUAGE = "en"

SUPPORTED_LANGUAGES = {
    "en": "English",
    "pt": "Português",
}

_TRANSLATIONS = {
    "en": {
        "nav.today": "Today",
        "nav.plan": "Plan",
        "nav.activities": "Activities",
        "nav.calendar": "Calendar",
        "nav.development": "Development",
        "nav.settings": "Settings",
        "athlete.edit": "Edit athlete",
        "plan.section": "Training plan",
        "plan.generate": "Generate plan",
        "activity.section": "Import activity",
        "activity.add": "Add activity",
        "activity.source": "Activity source",
        "activity.manual": "Manual",
        "activity.file": "File",
        "activity.choose_file": "Choose activity file",
        "language.label": "Language",
    },
    "pt": {
        "nav.today": "Hoje",
        "nav.plan": "Plano",
        "nav.activities": "Atividades",
        "nav.calendar": "Calendário",
        "nav.development": "Desenvolvimento",
        "nav.settings": "Definições",
        "athlete.edit": "Editar atleta",
        "plan.section": "Plano de treino",
        "plan.generate": "Gerar plano semanal",
        "activity.section": "Importar treino",
        "activity.add": "Adicionar atividade",
        "activity.source": "Origem da atividade",
        "activity.manual": "Manual",
        "activity.file": "Ficheiro",
        "activity.choose_file": "Selecionar ficheiro de atividade",
        "language.label": "Idioma",
    },
}


def current_language() -> str:
    """
    Returns the active interface language.
    """

    language = st.session_state.get(
        "language",
        DEFAULT_LANGUAGE,
    )

    if language not in SUPPORTED_LANGUAGES:
        language = DEFAULT_LANGUAGE
        st.session_state.language = language

    return language


def set_language(
    language: str,
) -> None:
    """
    Stores the active interface language.
    """

    if language not in SUPPORTED_LANGUAGES:
        raise ValueError(
            f"Unsupported language: {language}"
        )

    st.session_state.language = language


def translate(
    key: str,
    *,
    language: str | None = None,
) -> str:
    """
    Returns the translated interface string for a stable key.

    Missing translations fall back to English and finally to the
    key itself, so the interface remains usable during migration.
    """

    selected = (
        language
        if language is not None
        else current_language()
    )

    if selected not in SUPPORTED_LANGUAGES:
        selected = DEFAULT_LANGUAGE

    selected_catalogue = _TRANSLATIONS.get(
        selected,
        {},
    )
    default_catalogue = _TRANSLATIONS[
        DEFAULT_LANGUAGE
    ]

    return selected_catalogue.get(
        key,
        default_catalogue.get(
            key,
            key,
        ),
    )