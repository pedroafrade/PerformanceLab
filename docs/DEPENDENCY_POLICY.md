# Política de Dependências do PerformanceLab

## Fonte única

O ficheiro `pyproject.toml` é a única fonte de dependências Python do PerformanceLab.

Não deve existir um `requirements.txt` independente, porque duas listas de dependências podem ficar dessincronizadas.

## Instalação

Para instalar a aplicação:

```powershell
python -m pip install -e .
```

Para desenvolvimento e execução dos testes:

```powershell
python -m pip install -e ".[test]"
```

## Versões suportadas

O projeto suporta Python 3.11, 3.12, 3.13 e 3.14.

Cada dependência direta deve possuir:

- uma versão mínima compatível com o código atual;
- um limite superior que impeça a instalação automática da próxima versão principal;
- uma exceção apenas quando o esquema de versões do projeto exigir outro limite seguro.

## Atualizações

As dependências não são atualizadas automaticamente sem validação.

Cada atualização deve:

1. alterar apenas as versões necessárias;
2. instalar o projeto num ambiente limpo;
3. executar o pytest completo;
4. confirmar o arranque do Streamlit;
5. verificar importação, autenticação, PostgreSQL e Training Coach quando forem afetados;
6. ser registada num commit próprio.

Correções de segurança urgentes podem ultrapassar esta sequência apenas quando a razão e a validação realizada ficarem documentadas.

## Deployment

O ambiente alpha deve instalar a aplicação através do `pyproject.toml`.

A versão de Python usada no deployment deve estar dentro do intervalo declarado em `requires-python`.