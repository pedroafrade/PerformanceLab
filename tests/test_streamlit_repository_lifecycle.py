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


def test_repository_bundle_is_reused_by_one_streamlit_session():
    app = source()

    assert (
        'if "_repository_bundle" not in st.session_state:'
        in app
    )
    assert (
        'repository_bundle = st.session_state["_repository_bundle"]'
        in app
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
