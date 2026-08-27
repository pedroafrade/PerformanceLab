"""
PerformanceLab

Streamlit OIDC configuration preflight tests.
"""

from scripts.check_alpha_auth_configuration import (
    FAILURE_MESSAGE,
    REQUIRED_AUTH_SETTINGS,
    SUCCESS_MESSAGE,
    main,
    validate_auth_configuration,
)


def valid_auth_values() -> dict[
    str,
    object,
]:

    return {
        "auth": {
            "redirect_uri": (
                "https://alpha.example.com/"
                "oauth2callback"
            ),
            "cookie_secret": (
                "fictitious-cookie-secret"
            ),
            "client_id": (
                "fictitious-client-id"
            ),
            "client_secret": (
                "fictitious-client-secret"
            ),
            "server_metadata_url": (
                "https://accounts.google.com/"
                ".well-known/"
                "openid-configuration"
            ),
        },
    }

def test_requires_all_streamlit_auth_settings():

    values = valid_auth_values()

    assert validate_auth_configuration(
        values
    )

    for setting_name in REQUIRED_AUTH_SETTINGS:

        incomplete_values = (
            valid_auth_values()
        )

        del incomplete_values[
            "auth"
        ][setting_name]

        assert not validate_auth_configuration(
            incomplete_values
        )


def test_rejects_missing_auth_section():

    assert not validate_auth_configuration(
        {}
    )


def test_accepts_valid_toml_file(
    tmp_path,
    capsys,
):

    path = (
        tmp_path
        / "secrets.toml"
    )

    path.write_text(
        """
[auth]
redirect_uri = "https://alpha.example.com/oauth2callback"
cookie_secret = "fictitious-cookie-secret"
client_id = "fictitious-client-id"
client_secret = "fictitious-client-secret"
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"
""".strip(),
        encoding="utf-8",
    )

    result = main(path)

    captured = capsys.readouterr()

    assert result == 0
    assert SUCCESS_MESSAGE in captured.out
    assert captured.err == ""


def test_failure_does_not_expose_secret(
    tmp_path,
    capsys,
):

    path = (
        tmp_path
        / "secrets.toml"
    )

    path.write_text(
        """
[auth]
client_secret = "super-secret-value"
""".strip(),
        encoding="utf-8",
    )

    result = main(path)

    captured = capsys.readouterr()

    output = (
        captured.out
        + captured.err
    )

    assert result == 1
    assert FAILURE_MESSAGE in captured.err
    assert "super-secret-value" not in output


def test_rejects_missing_file(
    tmp_path,
    capsys,
):

    result = main(
        tmp_path
        / "missing.toml"
    )

    captured = capsys.readouterr()

    assert result == 1
    assert FAILURE_MESSAGE in captured.err