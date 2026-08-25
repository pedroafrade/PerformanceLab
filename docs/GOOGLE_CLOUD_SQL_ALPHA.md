# Google Cloud SQL — Alpha Privada

**Preparado em:** 25 de agosto de 2026  
**Estado:** FORNECEDOR ESCOLHIDO — ATIVAÇÃO PENDENTE

## 1. Decisão

O fornecedor PostgreSQL escolhido para a alpha privada é o
Google Cloud SQL for PostgreSQL.

A utilização inicial deverá aproveitar a avaliação gratuita da
Google Cloud, limitada a:

- 300 USD de crédito;
- 90 dias após o início da avaliação;
- ausência de cobrança automática enquanto a conta permanecer
  identificada como Free Trial e não for convertida numa conta paga.

A elegibilidade e as condições apresentadas pela Google deverão ser
confirmadas no momento da criação da conta.

## 2. Limites obrigatórios

A alpha não poderá depender da continuidade do serviço depois de:

- terminar o período de 90 dias;
- terminar o crédito de 300 USD;
- a Google interromper a conta experimental;
- ser tomada uma decisão explícita de não continuar com o serviço.

O botão Activate ou Ativar, que converte a conta numa conta paga,
não deverá ser utilizado sem uma nova decisão explícita sobre custos.

## 3. Calendário de segurança

O dia em que a avaliação gratuita começar será registado como Dia 0.

A alpha com participantes termina obrigatoriamente no Dia 60,
deixando 30 dias de margem antes do limite da avaliação Google.

O calendário será:

- Dia 0: início da avaliação;
- Dias 0–20: configuração e testes exclusivamente internos;
- até ao Dia 21: início gradual dos convites;
- Dia 30: primeira revisão de utilização e custos;
- Dia 60: fim obrigatório da alpha com participantes;
- Dias 61–75: exportação, migração ou decisão de continuidade;
- Dia 75: início obrigatório do encerramento, se ainda estiver pendente;
- Dia 85: conclusão da exportação, migração ou eliminação;
- Dias 86–90: margem final reservada para imprevistos;
- Dia 90: limite absoluto da avaliação gratuita.

Se a configuração e os testes internos não estiverem concluídos até
ao Dia 20, o início dos convites será adiado e a duração da alpha
será reduzida.

A participação nunca será prolongada além do Dia 60 apenas para
compensar um atraso na preparação.

A alpha também poderá terminar antes do Dia 60 se:

- o crédito atingir 270 USD;
- existir um incidente de segurança ou integridade;
- os backups ou alertas deixarem de funcionar;
- for necessário migrar ou encerrar antecipadamente.

## 4. Controlo do crédito

Deverão ser criados alertas de orçamento para:

- 150 USD — 50% do crédito;
- 225 USD — 75% do crédito;
- 270 USD — 90% do crédito.

Os alertas de orçamento servem para avisar. Não garantem que os
serviços sejam automaticamente interrompidos.

Ao atingir 270 USD, não deverão ser iniciados novos convites e deverá
ser tomada uma decisão imediata entre:

- reduzir ou suspender os serviços;
- migrar a base de dados;
- terminar a alpha;
- aprovar conscientemente uma conta paga.

## 5. Configuração pretendida

A instância deverá utilizar:

- Google Cloud SQL for PostgreSQL;
- região pertencente à União Europeia;
- backups automáticos diários;
- retenção de backups durante 14 dias;
- encriptação fornecida pelo Google Cloud;
- acesso administrativo limitado;
- ligação encriptada;
- recuperação para uma instância separada;
- retenção do backup final, quando aplicável.

A região concreta será registada apenas depois de ser escolhida e
confirmada na consola da Google Cloud.

## 6. Portabilidade

O PerformanceLab deverá continuar independente do Google Cloud.

A aplicação utiliza:

- PostgreSQL normal;
- SQLAlchemy;
- Psycopg 3;
- migrações Alembic;
- configuração através de `DATABASE_URL`;
- repositórios PostgreSQL próprios da aplicação.

Não deverão ser introduzidas funcionalidades exclusivas do Google
Cloud que impeçam a utilização futura de outro serviço PostgreSQL.

Uma futura mudança poderá utilizar:

1. criação de uma nova base PostgreSQL;
2. aplicação das migrações Alembic;
3. exportação lógica da base de origem;
4. restauro na nova base;
5. execução dos testes de integridade e isolamento;
6. alteração segura de `DATABASE_URL`;
7. conservação temporária da base anterior para rollback;
8. eliminação da base anterior depois da confirmação.

Passwords, tokens, certificados e valores reais de `DATABASE_URL`
nunca serão guardados no repositório.

## 7. Saída antes do fim da avaliação

Até ao Dia 60 será obrigatório escolher uma destas opções, para que
a respetiva execução possa terminar até ao Dia 85:

### Continuação paga

Manter o Cloud SQL depois de aprovar explicitamente o custo previsto.

### Migração

Transferir os dados para outro PostgreSQL, testar a nova base e só
depois eliminar a instância do Google Cloud.

### Encerramento

Disponibilizar as exportações necessárias, eliminar os dados ativos,
tratar os backups segundo a política de retenção e fechar a conta de
faturação.

Nenhuma destas decisões pode ser deixada para depois do Dia 90.

## 8. Estado atual

Neste momento:

- [x] Google Cloud SQL escolhido como fornecedor PostgreSQL;
- [x] limite de 300 USD identificado;
- [x] limite de 90 dias identificado;
- [x] estratégia de portabilidade definida;
- [ ] elegibilidade para a avaliação confirmada;
- [ ] conta Google Cloud criada;
- [ ] Dia 0 e datas de controlo registados;
- [ ] região europeia confirmada;
- [ ] instância PostgreSQL criada;
- [ ] alertas de orçamento criados;
- [ ] backups automáticos configurados;
- [ ] retenção de 14 dias confirmada;
- [ ] primeira cópia de segurança confirmada;
- [ ] restauro real testado.

Enquanto os itens pendentes não forem concluídos, os backups não
podem ser considerados operacionais e os convites permanecem
bloqueados.