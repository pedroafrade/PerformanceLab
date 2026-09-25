"""
PerformanceLab

Streamlit persistence resource lifecycle contract.
"""

from pathlib import Path


APP_SOURCE = (
    Path(__file__).parents[1]
    / "app"
    / "app.py"
)


def source() -> str:
    return APP_SOURCE.read_text(
        encoding="utf-8"
    )


def test_repository_bundle_is_rotated_between_streamlit_reruns():
    app = source()

    assert (
        'st.session_state.pop(\n'
        '        "_repository_bundle",'
        in app
    )
    assert "previous_repository_bundle.close()" in app
    assert (
        'st.session_state["_repository_bundle"] = (\n'
        '    repository_bundle'
        in app
    )
    assert (
        'if "_repository_bundle" not in st.session_state:'
        not in app
    )


def test_every_logout_releases_the_session_repository_bundle():
    app = source()

    assert "def close_repository_bundle()" in app
    assert 'st.session_state.pop(\n        "_repository_bundle",' in app
    assert "active_bundle.close()" in app
    assert "on_click=st.logout" not in app
    assert (
        app.index("close_repository_bundle()")
        < app.index("st.session_state.clear()")
    )


def test_active_athlete_load_commits_reconciliation_before_render():
    app = source()
    load_block = (
        app.split(
            'if "athlete" not in st.session_state:',
            1,
        )[1]
        .split(
            "except PermissionError:",
            1,
        )[0]
    )

    rollback = (
        "repository_bundle."
        "rollback_pending_read_transaction()"
    )
    transaction = (
        "with repository_bundle.transaction():"
    )
    load = "LoadActiveAthlete("

    assert rollback in load_block
    assert transaction in load_block
    assert load in load_block
    assert (
        load_block.index(rollback)
        < load_block.index(transaction)
        < load_block.index(load)
    )
