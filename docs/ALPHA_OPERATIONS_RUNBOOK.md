# Operação da Alpha Privada do PerformanceLab

**Preparado em:** 25 de agosto de 2026  
**Estado:** PROCEDIMENTO PREPARADO — EXECUÇÃO PENDENTE

## 1. Objetivo

Este documento descreve como preparar, publicar, verificar,
interromper e recuperar a alpha privada do PerformanceLab.

Não significa que o deployment, os backups ou o restauro já tenham
sido realizados.

## 2. Bloqueadores antes dos convites

Nenhum participante real pode ser convidado enquanto estiver
pendente qualquer um destes pontos:

- revisão jurídica externa do passo F.9.2;
- contacto de privacidade definitivo;
- alojamento privado da aplicação;
- Google Cloud SQL configurado numa região da União Europeia;
- backups automáticos com retenção de 14 dias;
- restauro real testado numa base separada;
- Better Stack ativo e verificado;
- CI sem erros;
- autenticação, convites e isolamento testados no ambiente alpha;
- plano de incidente confirmado.

## 3. Preparação de uma publicação

Antes de publicar uma versão:

1. confirmar o commit exato da `main`;
2. confirmar que o GitHub Actions terminou sem erros;
3. executar localmente os testes completos;
4. confirmar que não existem alterações locais inesperadas;
5. confirmar que não existem dados, backups ou segredos no commit;
6. registar o commit que será publicado;
7. confirmar o estado dos backups;
8. confirmar que existe uma opção segura de rollback.

Comandos locais:

```powershell
pytest -q
git status --short
git diff --check
git log -1 --oneline
```

Nunca utilizar `git add .` para preparar uma publicação.

## 4. Segredos do ambiente alpha

Os valores reais são configurados apenas no serviço de alojamento.

Os nomes esperados incluem:

- `PERFORMANCELAB_ENV`;
- `DATABASE_URL`;
- `PRIVACY_CONTACT_EMAIL`;
- `BETTER_STACK_ERROR_DSN`;
- configuração OIDC;
- configuração do Gemini;
- limites do Training Coach;
- configurações de retenção.

Passwords, tokens, chaves, certificados e valores reais de
`DATABASE_URL` nunca são:

- adicionados ao Git;
- escritos na documentação;
- enviados em mensagens;
- incluídos em logs;
- incluídos em capturas de ecrã.

## 5. Instalação reproduzível

A fonte única das dependências é `pyproject.toml`.

A instalação da aplicação e dos testes utiliza:

```powershell
python -m pip install -e ".[test]"
```

A verificação mínima utiliza:

```powershell
python -m compileall -q app performancelab migrations
pytest -q
```

O ambiente de deployment deverá utilizar uma versão de Python
suportada pelo `pyproject.toml` e testada pelo CI.

## 6. Migrações PostgreSQL

As migrações utilizam Alembic e recebem a ligação através de
`DATABASE_URL`.

Antes de executar uma migração:

1. confirmar que `DATABASE_URL` aponta para a base correta;
2. confirmar que existe um backup recuperável;
3. registar o commit que contém a migração;
4. impedir alterações concorrentes durante a operação;
5. nunca mostrar o valor de `DATABASE_URL` no terminal partilhado.

Para consultar o estado:

```powershell
alembic current
alembic heads
```

Para aplicar todas as migrações pendentes:

```powershell
alembic upgrade head
```

Depois da migração:

```powershell
alembic current
```

É ainda obrigatório:

- executar a verificação de saúde;
- iniciar a aplicação;
- testar login com uma conta interna;
- testar dois utilizadores internos;
- confirmar que nenhum utilizador vê dados do outro;
- confirmar importação, exportação e eliminação com dados descartáveis.

## 7. Deployment

O fornecedor de alojamento da aplicação ainda está por confirmar.

Quando for escolhido, o processo deverá:

1. publicar apenas um commit confirmado da `main`;
2. instalar através de `pyproject.toml`;
3. configurar os segredos fora do repositório;
4. aplicar as migrações antes de aceitar utilização;
5. arrancar com `PERFORMANCELAB_ENV=alpha`;
6. recusar o arranque sem PostgreSQL;
7. executar a verificação de saúde;
8. confirmar os alertas do Better Stack;
9. testar com duas contas internas;
10. só depois permitir convites graduais.

O deployment não pode criar automaticamente atletas ou contas de
demonstração.

## 8. Rollback da aplicação

Rollback significa voltar à última versão confirmada quando uma nova
versão causa um problema.

Antes do rollback:

1. suspender novos convites;
2. impedir novas alterações, se houver risco para os dados;
3. registar o commit com problema;
4. registar o último commit confirmado;
5. identificar se houve alteração da base de dados.

Se não existiu alteração incompatível da base de dados, pode ser
publicado novamente o último commit confirmado.

Não utilizar `git reset --hard` como procedimento de deployment.

## 9. Rollback da base de dados

Não executar automaticamente:

```powershell
alembic downgrade -1
```

Uma migração inversa pode eliminar ou transformar dados. Antes de
qualquer downgrade é necessária uma avaliação específica da
migração envolvida.

Quando existir risco para os dados, o procedimento preferido é:

1. manter a base original sem novas escritas;
2. restaurar o backup numa base separada;
3. aplicar apenas as migrações necessárias;
4. reconciliar eliminações posteriores ao backup;
5. executar testes de integridade e isolamento;
6. alterar `DATABASE_URL` apenas depois da validação;
7. conservar temporariamente a base anterior para rollback;
8. eliminar a base anterior segundo o procedimento aprovado.

Nunca testar um restauro diretamente sobre a base ativa.

## 10. Classificação de incidentes

### Crítico

Inclui:

- dados de um atleta visíveis a outro;
- perda ou corrupção de dados;
- acesso não autorizado;
- segredo exposto;
- eliminação integral incompleta;
- backup ou restauro não fiável durante a alpha.

Ação imediata: suspender a aplicação e os convites.

### Elevado

Inclui:

- autenticação ou autorização intermitente;
- importações que alteram dados incorretamente;
- falha prolongada do PostgreSQL;
- Training Coach a ultrapassar limites;
- alertas operacionais indisponíveis.

Ação: desativar a funcionalidade afetada ou suspender a aplicação.

### Moderado

Inclui:

- erro funcional sem perda ou exposição de dados;
- problema visual;
- desempenho degradado;
- recomendação inesperada sem efeito persistente perigoso.

Ação: registar, avaliar e corrigir num commit próprio.

## 11. Resposta a incidente

Perante um incidente:

1. interromper a funcionalidade afetada;
2. suspender novos convites;
3. preservar apenas evidência técnica necessária;
4. registar data, hora e identificador de correlação;
5. não copiar dados pessoais para logs ou mensagens;
6. identificar versões da aplicação e migração;
7. avaliar participantes e dados afetados;
8. corrigir ou recuperar numa base separada;
9. testar antes de reabrir;
10. documentar causa, impacto, correção e prevenção;
11. avaliar as obrigações de comunicação aplicáveis.

O Better Stack serve para avisar que ocorreu uma falha. Não corrige
automaticamente a aplicação nem recupera os dados.

## 12. Suspensão segura

Se existir dúvida sobre isolamento, integridade ou segurança:

- parar novos convites;
- desativar o Training Coach, se estiver relacionado;
- suspender o acesso à aplicação, se necessário;
- não eliminar imediatamente a base ou os backups;
- não executar comandos destrutivos durante o diagnóstico;
- informar os participantes quando for aplicável.

A aplicação só deverá reabrir depois de os testes relevantes
passarem sem erros.

## 13. Registo de cada operação

Cada deployment, migração, rollback ou incidente deverá registar:

- data e hora;
- pessoa responsável;
- commit;
- migração atual;
- ambiente;
- resultado do CI;
- resultado da verificação de saúde;
- resultado dos testes internos;
- decisão de avançar ou suspender.

O registo não deve conter segredos nem dados dos atletas.

## 14. Estado atual

Neste momento:

- [x] CI criado;
- [x] testes de isolamento com dois utilizadores criados;
- [x] logging estruturado criado;
- [x] captura segura de exceções criada;
- [x] Better Stack escolhido;
- [x] verificação de saúde criada;
- [x] Google Cloud SQL escolhido;
- [x] procedimentos de deployment e incidente preparados;
- [ ] revisão jurídica externa concluída;
- [ ] alojamento da aplicação escolhido;
- [ ] avaliação Google Cloud iniciada;
- [ ] PostgreSQL alpha criado;
- [ ] backups automáticos ativos;
- [ ] restauro real testado;
- [ ] Better Stack ativado e verificado;
- [ ] deployment executado.

Os itens pendentes continuam a bloquear os convites.