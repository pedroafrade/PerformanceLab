# Política de Retenção — Alpha Privada do PerformanceLab

**Versão do rascunho:** `retention-alpha-v1`  
**Data do rascunho:** 25 de agosto de 2026  
**Estado:** RASCUNHO — NÃO ATIVAR NA ALPHA

> Esta política ainda não está concluída. Os campos `[POR DEFINIR]` exigem uma decisão explícita antes do primeiro convite externo.

## 1. Objetivo

Esta política define durante quanto tempo o PerformanceLab conserva cada categoria de dados pessoais da alpha privada e o que acontece quando:

- os dados deixam de ser necessários;
- uma conta fica inativa;
- um convite não é utilizado;
- um participante retira o consentimento;
- um participante elimina a conta;
- termina o período de conservação de logs ou backups.

A política abrange dados ativos, ficheiros temporários, metadados operacionais, convites e cópias de segurança.

## 2. Princípios

O PerformanceLab deverá:

- conservar apenas os dados necessários para as finalidades declaradas;
- utilizar prazos ou critérios objetivos por categoria;
- eliminar dados expirados de forma verificável;
- evitar conservar cópias redundantes;
- distinguir dados ativos de backups;
- impedir que dados eliminados regressem silenciosamente após um restauro;
- documentar qualquer obrigação que exija conservação adicional;
- não prolongar prazos apenas por conveniência técnica.

## 3. Contas e perfis ativos

Enquanto a participação estiver ativa, são conservados:

- conta interna;
- identidade externa associada;
- relação de autorização;
- perfil de atleta;
- atividades e rotas;
- objetivos e provas;
- planos, reconciliações e adaptações;
- indicadores e observações;
- interpretações do Training Coach;
- consentimentos;
- metadados operacionais necessários.

A conservação termina quando:

- o participante pede a eliminação;
- a participação é encerrada;
- a conta ultrapassa o prazo de inatividade definido.

Prazo de inatividade antes de contacto ou eliminação:

`[POR DEFINIR — PRAZO PARA CONTAS INATIVAS]`

Procedimento antes da eliminação por inatividade:

`[POR DEFINIR — AVISO E OPORTUNIDADE DE REATIVAÇÃO]`

## 4. Eliminação pedida pelo participante

A aplicação possui um processo de eliminação com confirmação forte.

A eliminação ativa abrange:

- conta do utilizador;
- ligações à identidade externa;
- convites associados;
- autorizações relativas ao atleta eliminado;
- perfil e agregado completo do atleta;
- atividades, rotas, planos e indicadores;
- interpretações do Training Coach;
- consentimentos da alpha;
- consentimentos do Training Coach;
- metadados de utilização do Training Coach.

No PostgreSQL, esta operação é executada dentro de uma transação.

A eliminação dos dados ativos ocorre quando o pedido confirmado é executado com sucesso.

A presença temporária dos dados em backups é tratada separadamente na secção de backups.

## 5. Ficheiros de atividade importados

Os ficheiros FIT, FIT.GZ, GPX e CSV são processados temporariamente.

Regra já definida:

- os ficheiros originais não são conservados depois do processamento;
- a libertação ocorre tanto após sucesso como após falha;
- apenas os dados de atividade extraídos e integrados no perfil podem permanecer.

Prazo dos ficheiros originais:

**eliminação no final do processamento**

## 6. Interpretações do Training Coach

Regra já definida:

- é conservada apenas a interpretação mais recente por atividade;
- uma nova interpretação substitui a anterior;
- a interpretação é removida quando a atividade é eliminada;
- a interpretação é removida com a eliminação integral do atleta.

Não são conservados prompts completos em logs operacionais.

## 7. Metadados de utilização do Training Coach

Os metadados podem incluir:

- identificador do evento;
- utilizador;
- data e hora;
- resultado;
- fornecedor;
- modelo;
- código de erro;
- latência;
- limites restantes.

Não incluem o prompt completo, o payload fisiológico ou a interpretação gerada.

Prazo de conservação:

`[POR DEFINIR — RETENÇÃO DOS METADADOS DO TRAINING COACH]`

Finalidade durante esse prazo:

- aplicação e diagnóstico dos limites de utilização;
- análise de falhas;
- controlo operacional da alpha.

## 8. Consentimentos

São tratados separadamente:

- consentimento de participação na alpha;
- autorização opcional do Training Coach.

Enquanto a conta existe, cada registo pode incluir:

- versão;
- finalidade;
- data de aceitação ou concessão;
- eventual data de retirada.

Os consentimentos ativos são eliminados com a eliminação integral da conta.

Caso seja necessária conservação posterior para demonstrar o consentimento ou a retirada, deverão ser definidos:

- fundamento;
- conteúdo mínimo;
- prazo;
- acesso autorizado.

Retenção posterior à eliminação da conta:

`[POR DEFINIR — RETENÇÃO DE PROVA DE CONSENTIMENTO]`

## 9. Convites

Os convites podem conter:

- email;
- papel;
- atleta associado;
- estado de utilização;
- utilizador que reclamou o convite.

Os convites associados ao participante ou ao atleta são eliminados durante a eliminação integral implementada.

Para convites não utilizados, expirados ou revogados:

- prazo de validade do convite: `[POR DEFINIR — VALIDADE DO CONVITE]`
- prazo adicional antes da eliminação: `[POR DEFINIR — RETENÇÃO DE CONVITES EXPIRADOS]`

## 10. Logs de aplicação e segurança

A fase G ainda deverá implementar logging estruturado sem dados sensíveis.

Os logs não deverão conter:

- passwords;
- tokens;
- chaves de API;
- `DATABASE_URL`;
- prompts completos;
- payload fisiológico;
- ficheiros importados;
- exportações do participante.

Antes de ativar logs na alpha deverão ser definidos:

- eventos registados;
- campos permitidos;
- acessos;
- sistema de armazenamento;
- região;
- prazo de conservação;
- eliminação automática.

Prazo de conservação:

`[POR DEFINIR — RETENÇÃO DOS LOGS]`

## 11. Erros e alertas

A futura captura de exceções deverá minimizar os dados enviados ao fornecedor de monitorização.

Antes da ativação deverão ser definidos:

- fornecedor;
- campos enviados;
- região;
- transferências;
- prazo de conservação.

Prazo de conservação:

`[POR DEFINIR — RETENÇÃO DE ERROS E ALERTAS]`

## 12. Backups

Os backups ainda não estão configurados.

Antes do primeiro convite deverão ser definidos:

- fornecedor;
- região;
- frequência;
- encriptação;
- acessos;
- prazo de conservação;
- número de versões;
- processo de eliminação;
- procedimento de restauro.

Prazo de conservação dos backups:

`[POR DEFINIR — RETENÇÃO DOS BACKUPS]`

Os dados eliminados da base ativa poderão permanecer temporariamente num backup até à expiração normal desse backup.

Um restauro não deverá reativar silenciosamente contas ou dados previamente eliminados. O procedimento de restauro deverá reaplicar ou reconciliar eliminações realizadas depois da data do backup.

## 13. Exportações

As exportações são geradas a pedido e entregues diretamente ao participante através do browser.

O PerformanceLab não deverá guardar uma cópia adicional da exportação no servidor.

O participante é responsável pela cópia descarregada para o seu dispositivo.

## 14. Pedidos de suporte e exercício de direitos

Podem existir comunicações relacionadas com:

- suporte;
- acesso;
- correção;
- exportação;
- eliminação;
- incidentes.

Antes do primeiro convite deverão ser definidos:

- canal utilizado;
- informação mínima registada;
- controlo de acesso;
- prazo de conservação;
- eliminação segura.

Prazo de conservação:

`[POR DEFINIR — RETENÇÃO DE PEDIDOS E SUPORTE]`

## 15. Fim da alpha privada

Antes de terminar a alpha deverá ser decidido se:

- os dados serão migrados para uma fase posterior;
- será pedida nova aceitação;
- os participantes poderão exportar os dados;
- todas as contas e dados serão eliminados.

Prazo após o encerramento da alpha:

`[POR DEFINIR — PRAZO APÓS O FIM DA ALPHA]`

## 16. Execução e verificação

A política final deverá identificar, para cada categoria:

- evento que inicia o prazo;
- duração ou critério;
- operação de eliminação;
- responsável pela execução;
- forma de verificar a eliminação;
- tratamento em backups;
- exceções documentadas.

As rotinas automáticas de limpeza, logs, backups e restauro pertencem à implementação operacional da fase G.

## 17. Decisões obrigatórias pendentes

A política não pode ser ativada enquanto não forem definidos:

- [ ] prazo para contas inativas;
- [ ] aviso antes da eliminação por inatividade;
- [ ] retenção dos metadados do Training Coach;
- [ ] eventual retenção mínima de prova de consentimento;
- [ ] validade dos convites;
- [ ] retenção de convites expirados;
- [ ] retenção dos logs;
- [ ] retenção de erros e alertas;
- [ ] retenção dos backups;
- [ ] retenção de pedidos de suporte e direitos;
- [ ] prazo após o fim da alpha;
- [ ] procedimento que impede o restauro de dados eliminados;
- [ ] revisão jurídica dos prazos.