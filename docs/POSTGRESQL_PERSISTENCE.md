# PerformanceLab — Persistência PostgreSQL

**Estado:** decisão aceite  
**Data:** 15 de agosto de 2026  
**Fase:** C — Persistência PostgreSQL

## Contexto

A alpha privada não pode depender de ficheiros JSON guardados no
sistema de ficheiros da aplicação.

O alojamento pode reiniciar, substituir a instância ou executar mais
de uma sessão. Duas sessões que alterem o mesmo atleta também não
podem substituir silenciosamente os dados uma da outra.

A transição deve preservar o domínio atual e os protocolos de
repositório. PostgreSQL é uma implementação de infraestrutura, não
uma dependência do domínio.

## Decisão

A persistência remota utilizará:

- PostgreSQL como base de dados;
- SQLAlchemy 2 para ligações, transações, metadata e SQL;
- Psycopg 3 como driver PostgreSQL;
- Alembic para migrações versionadas;
- execução síncrona na primeira alpha.

As dependências possuem limites de versão principais:

- `SQLAlchemy>=2.0,<3`;
- `alembic>=1.16,<2`;
- `psycopg[binary]>=3.2,<4`.

## Motivos

### SQLAlchemy 2

Permite:

- gerir engines e ligações;
- delimitar transações;
- definir tabelas e constraints;
- usar PostgreSQL sem introduzir essa dependência no domínio;
- testar a infraestrutura através dos protocolos existentes.

A primeira implementação deverá preferir SQLAlchemy Core e modelos
de persistência explícitos. O agregado `Athlete` não será convertido
num grande grafo ORM.

### Psycopg 3

É o driver PostgreSQL atual escolhido para Python.

A variante `binary` é usada inicialmente porque:

- não exige compilador C local;
- inclui as bibliotecas cliente necessárias;
- simplifica Windows e o primeiro ambiente alpha;
- mantém o mesmo módulo Python `psycopg`.

A escolha poderá ser revista para uma instalação compilada quando o
ambiente de alojamento estiver definido e testado.

### Alembic

Todas as alterações ao esquema serão aplicadas através de migrações
versionadas.

Não serão criadas ou alteradas tabelas automaticamente durante o
arranque normal da aplicação.

Cada migração deverá possuir:

- operação `upgrade`;
- operação `downgrade`, quando tecnicamente segura;
- teste de aplicação desde uma base vazia;
- revisão antes de entrar na `main`.

### Execução síncrona

O Streamlit atual executa os casos de uso de forma síncrona.

Adicionar uma stack assíncrona nesta fase aumentaria a complexidade
sem resolver um requisito da alpha. Concorrência será controlada por
transações e versão do agregado.

## Estrutura inicial prevista

O primeiro esquema deverá suportar:

- utilizadores internos;
- identidades externas;
- atletas;
- convites;
- autorizações utilizador–atleta;
- snapshots versionados do agregado `Athlete`;
- migrações do esquema.

Consentimentos, utilização de IA e auditoria operacional serão
adicionados nas fases correspondentes.

## Regras

- `DATABASE_URL` nunca é guardada no Git;
- nenhuma password é apresentada em logs ou mensagens da UI;
- o domínio não importa SQLAlchemy, Psycopg ou Alembic;
- o ambiente local pode continuar com JSON durante a transição;
- o ambiente alpha será impedido de arrancar com JSON;
- leituras e escritas PostgreSQL incluem sempre o `athlete_id`
  autorizado;
- alterações lógicas que envolvam vários registos usam uma única
  transação;
- conflitos concorrentes não podem resultar em substituição
  silenciosa.
  
## Fronteira obrigatória da alpha privada

A aplicação local pode continuar a utilizar os repositórios JSON
durante o desenvolvimento.

A alpha privada deve ser iniciada com:

```text
PERFORMANCELAB_ENV=alpha
DATABASE_URL=<ligação PostgreSQL guardada como segredo>

## Não decidido neste passo

Este passo ainda não define:

- fornecedor de PostgreSQL gerido;
- esquema SQL definitivo;
- formato final do snapshot;
- pool de ligações;
- política de backups;
- configuração por ambiente;
- mecanismo de migração dos dados reais.

Essas decisões serão tomadas em commits próprios da Fase C.