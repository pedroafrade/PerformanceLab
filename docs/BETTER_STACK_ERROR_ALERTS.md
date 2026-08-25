# Alertas de Erro — Better Stack

## Decisão

O ambiente alpha do PerformanceLab utiliza o Better Stack para receber alertas operacionais de exceções.

A aplicação Better Stack deve ser criada numa região da União Europeia.

## Dados enviados

O PerformanceLab envia exclusivamente:

- nome interno da operação;
- tipo da exceção;
- identificador de correlação aleatório;
- ambiente da aplicação;
- versão da aplicação.

Não são enviados:

- a exceção original ou respetiva mensagem;
- traceback ou stack trace;
- breadcrumbs;
- email, nome ou identificador do participante;
- dados de atividade ou fisiológicos;
- pedidos HTTP;
- variáveis de ambiente;
- credenciais ou segredos;
- tracing, profiling ou session replay.

## Configuração

O DSN é guardado exclusivamente no secret:

```text
BETTER_STACK_ERROR_DSN