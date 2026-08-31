"""
PerformanceLab

Private alpha deployment record template tests.
"""

from pathlib import (
    Path,
)


TEMPLATE_PATH = (
    Path(__file__).parents[1]
    / "docs"
    / "ALPHA_DEPLOYMENT_RECORD_TEMPLATE.md"
)


def template_text():

    source = TEMPLATE_PATH.read_text(
        encoding="utf-8"
    )

    return " ".join(
        source.split()
    )


def test_template_is_not_an_execution_record():

    text = template_text()

    assert (
        "MODELO — NÃO REPRESENTA UM "
        "DEPLOYMENT EXECUTADO"
        in text
    )
    assert (
        "Não substituir este ficheiro pelo "
        "registo de uma operação real"
        in text
    )


def test_template_records_immutable_provenance():

    text = template_text()

    required_fields = (
        "Commit completo da `main`",
        "URL da execução da CI",
        "Digest imutável da imagem",
        "org.opencontainers.image.revision",
        "Revisão do Cloud Run",
    )

    for field in required_fields:

        assert field in text

    assert (
        "o label OCI e o commit associado "
        "ao digest devem coincidir"
        in text
    )


def test_template_records_database_safety():

    text = template_text()

    required_fields = (
        "Revisões Alembic antes da operação",
        "Revisões Alembic esperadas",
        "Revisões Alembic depois da operação",
        "Identificador do backup anterior",
        "Restauro disponível",
    )

    for field in required_fields:

        assert field in text

    assert (
        "Não registar o `DATABASE_URL`"
        in text
    )


def test_template_requires_all_preflights():

    text = template_text()

    preflights = (
        "Configuração runtime",
        "Configuração OIDC",
        "Ligação PostgreSQL",
        "Revisões das migrações",
    )

    for preflight in preflights:

        assert preflight in text

    assert (
        "Qualquer falha bloqueia o arranque"
        in text
    )


def test_template_prohibits_sensitive_values():

    text = template_text()

    protected_values = (
        "passwords",
        "tokens",
        "chaves",
        "cookies",
        "DSN",
        "`secrets.toml`",
        "`DATABASE_URL`",
        "dados dos atletas",
    )

    for protected_value in protected_values:

        assert protected_value in text


def test_template_preserves_activation_boundary():

    text = template_text()

    assert "não ativa serviços" in text
    assert "não publica imagens" in text
    assert "não executa migrações" in text
    assert "não inicia custos" in text

def test_template_records_internal_validation():

    text = template_text()

    required_checks = (
        "Endpoint de saúde",
        "Login da primeira conta interna",
        "Login da segunda conta interna",
        "Isolamento entre contas",
        "Importação com dados descartáveis",
        "Exportação com dados descartáveis",
        "Eliminação com dados descartáveis",
        "Alertas operacionais",
    )

    for check in required_checks:

        assert check in text

    assert (
        "Não incluir emails, nomes, "
        "identificadores OIDC ou dados dos atletas"
        in text
    )

