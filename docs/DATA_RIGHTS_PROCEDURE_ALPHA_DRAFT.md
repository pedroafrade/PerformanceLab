# Procedimento de Direitos — Alpha Privada do PerformanceLab

**Versão do rascunho:** `data-rights-alpha-v1`  
**Data do rascunho:** 25 de agosto de 2026  
**Estado:** RASCUNHO — CONTACTO DE PRIVACIDADE PENDENTE

> Este procedimento destina-se à operação manual da alpha privada. Não pode ser apresentado aos participantes enquanto o responsável pelo tratamento e o contacto de privacidade não estiverem definidos.

## 1. Objetivo

Este procedimento descreve como receber, verificar, executar e encerrar pedidos dos participantes relacionados com:

- acesso;
- correção;
- exportação e portabilidade;
- eliminação;
- limitação do tratamento;
- oposição;
- retirada de consentimento;
- informação sobre fornecedores e transferências.

Aplica-se apenas à alpha privada do PerformanceLab.

## 2. Canal de receção

Os pedidos deverão ser enviados para:

`[POR DEFINIR — EMAIL DE PRIVACIDADE]`

Durante a alpha, este será o canal oficial para pedidos que não possam ser concluídos diretamente na aplicação.

O participante não deverá enviar passwords, tokens, ficheiros de atividade, dados médicos adicionais ou uma cópia de documento de identificação por email.

## 3. Informação mínima do pedido

O pedido deverá conter apenas:

- email utilizado no PerformanceLab;
- direito que o participante pretende exercer;
- descrição curta do pedido;
- identificação dos dados que pretende corrigir, quando aplicável.

Não é necessário incluir atividades, rotas ou outros dados pessoais já existentes na aplicação.

## 4. Registo interno mínimo

Cada pedido deverá receber uma referência interna.

O registo operacional deverá conter apenas:

- referência;
- tipo de pedido;
- data e hora de receção;
- email da conta;
- estado;
- data limite de resposta;
- ações realizadas;
- data de encerramento;
- indicação de eventual prorrogação;
- motivo da prorrogação, quando aplicável.

Não deverão ser copiados para o registo:

- passwords;
- tokens;
- chaves;
- prompts completos;
- ficheiros importados;
- exportações completas;
- payload fisiológico;
- dados de outros participantes.

O registo do pedido será conservado durante **90 dias após o encerramento**, de acordo com `RETENTION_SUPPORT_REQUEST_DAYS=90`.

## 5. Verificação da identidade

A identidade deverá ser verificada antes de divulgar, corrigir ou eliminar dados.

A verificação normal deverá utilizar:

1. o endereço de email verificado associado à identidade OIDC;
2. uma sessão autenticada no PerformanceLab, quando disponível;
3. confirmação adicional dentro da sessão para operações destrutivas.

Se existirem dúvidas razoáveis, poderá ser pedida informação adicional estritamente necessária.

Não deverá ser pedida automaticamente uma cópia de documento de identificação. Qualquer verificação adicional deverá ser proporcional ao risco do pedido.

Nunca se deve usar apenas um `user_id`, `athlete_id`, nome ou parâmetro fornecido pelo browser como prova de identidade.

## 6. Prazos de resposta

O participante deverá receber uma resposta sem demora injustificada e, no máximo, no prazo de **um mês após a receção do pedido**.

Quando o pedido for complexo ou existirem vários pedidos, o prazo poderá ser prorrogado por até mais dois meses.

O participante deverá ser informado da prorrogação e dos respetivos motivos dentro do primeiro mês.

Se o pedido não puder ser executado, a resposta deverá explicar o motivo e indicar a possibilidade de reclamação à Comissão Nacional de Proteção de Dados.

## 7. Pedido de acesso

Para responder a um pedido de acesso:

1. verificar a identidade;
2. confirmar se existem dados associados;
3. gerar a exportação completa através do caso de uso autorizado;
4. verificar que a exportação pertence apenas ao participante;
5. disponibilizar o ficheiro por um canal adequado;
6. explicar as categorias, finalidades, fornecedores, retenção e direitos aplicáveis;
7. registar a conclusão sem guardar uma cópia adicional da exportação.

A aplicação já permite ao participante descarregar diretamente uma exportação JSON na página Settings.

## 8. Pedido de correção

Para responder a um pedido de correção:

1. verificar a identidade;
2. identificar o dado concreto;
3. distinguir dados introduzidos pelo participante de valores calculados;
4. permitir a correção através da aplicação quando a funcionalidade existir;
5. usar uma operação administrativa controlada quando não existir edição direta;
6. verificar que a alteração afeta apenas o atleta autorizado;
7. confirmar a correção ao participante.

Não se deve alterar uma atividade, indicador ou plano sem preservar a coerência do agregado do atleta.

## 9. Pedido de exportação ou portabilidade

Para responder:

1. verificar a identidade;
2. gerar uma nova exportação;
3. confirmar que o JSON é legível e válido;
4. confirmar que não contém segredos;
5. confirmar que não contém dados de outro participante;
6. entregar a exportação;
7. não guardar uma cópia adicional no servidor.

A existência da exportação não elimina os dados da aplicação.

## 10. Pedido de eliminação

O participante pode eliminar diretamente a conta e os dados através da página Settings.

A aplicação exige:

- confirmação explícita de compreensão;
- introdução exata da frase `DELETE MY DATA`;
- autorização de proprietário sobre o atleta;
- eliminação transacional no PostgreSQL;
- encerramento da sessão após sucesso.

Se a eliminação for tratada manualmente:

1. verificar a identidade;
2. confirmar por escrito que o pedido abrange conta e dados do atleta;
3. recomendar uma exportação prévia;
4. executar o mesmo caso de uso de eliminação integral;
5. confirmar o resultado;
6. encerrar o acesso;
7. registar apenas a conclusão mínima durante 90 dias.

Os dados ativos são eliminados imediatamente após a execução bem-sucedida.

Podem permanecer temporariamente em backups por até **14 dias**, de acordo com `RETENTION_BACKUP_DAYS=14`.

## 11. Limitação do tratamento

Quando for pedida limitação:

1. verificar a identidade;
2. identificar os tratamentos contestados;
3. impedir novas alterações ou utilizações não necessárias;
4. manter apenas o necessário para preservar os dados durante a análise;
5. desativar o Training Coach quando o pedido o abranger;
6. informar o participante antes de levantar a limitação.

A implementação operacional desta suspensão deverá ser concluída antes do primeiro convite externo.

## 12. Oposição

Quando o participante se opuser a um tratamento:

1. verificar a identidade;
2. identificar a finalidade e o fundamento jurídico;
3. suspender o tratamento contestado quando necessário;
4. avaliar se existem motivos legítimos para continuar;
5. documentar a decisão;
6. responder numa linguagem clara.

A avaliação jurídica do pedido não deverá ser automatizada.

## 13. Retirada de consentimento

A retirada do Training Coach:

- pode ser feita separadamente;
- impede novas gerações;
- não impede o uso das restantes funcionalidades.

A retirada da participação na alpha:

- impede a continuação da participação;
- pode ser acompanhada de pedido de exportação;
- pode ser acompanhada de eliminação integral.

A retirada não altera retroativamente o tratamento realizado antes da retirada.

## 14. Fornecedores e transferências

Quando o pedido envolver fornecedores ou transferências, a resposta deverá utilizar a informação factual mais recente sobre:

- Google OIDC;
- Google Gemini;
- alojamento da aplicação;
- PostgreSQL;
- backups;
- logs e monitorização.

Não deverão ser indicados fornecedor, país, região ou mecanismo de transferência por suposição.

## 15. Segurança da resposta

Antes de enviar dados:

- confirmar o destinatário;
- confirmar que a exportação pertence ao participante;
- não enviar dados em canais públicos;
- não colocar dados pessoais em issues do GitHub;
- não incluir dados de outro atleta;
- não conservar cópias desnecessárias;
- eliminar ficheiros temporários após a entrega.

Qualquer envio incorreto ou acesso indevido deverá ser tratado como possível incidente.

## 16. Encerramento do pedido

Antes de encerrar:

- confirmar que a identidade foi verificada;
- confirmar que todas as ações foram concluídas;
- registar a data da resposta;
- indicar eventuais limitações;
- informar o participante do resultado;
- definir a eliminação do registo após 90 dias.

O encerramento não deverá depender apenas de uma mensagem enviada. Deve existir confirmação de que a operação técnica terminou sem erros.

## 17. Escalação

O pedido deverá ser escalado quando:

- a identidade não puder ser verificada;
- existirem dados de mais do que um participante;
- houver risco de divulgação indevida;
- o pedido envolver fundamento jurídico contestado;
- os dados estiverem presentes num backup restaurado;
- ocorrer falha parcial de eliminação;
- o prazo de um mês estiver em risco;
- existir possível incidente de segurança.

## 18. Ensaio antes dos convites

Antes do primeiro convite externo, executar um ensaio com contas descartáveis:

1. pedido de acesso;
2. exportação;
3. correção;
4. retirada do Training Coach;
5. eliminação integral;
6. confirmação de isolamento;
7. simulação de pedido recebido por email;
8. verificação dos prazos e do registo mínimo.

O ensaio não deverá utilizar dados pessoais reais.

## 19. Decisões pendentes

Este procedimento não pode ser publicado enquanto não estiverem definidos:

- [ ] responsável pelo tratamento;
- [ ] email de privacidade;
- [ ] alojamento e fornecedores;
- [ ] regiões e transferências;
- [ ] mecanismo operacional de limitação;
- [ ] procedimento de incidentes;
- [ ] revisão jurídica.

## 20. Referências

- RGPD: https://eur-lex.europa.eu/eli/reg/2016/679/oj
- Direitos dos titulares — CNPD: https://www.cnpd.pt/cidadaos/direitos/
- Direito ao apagamento — CNPD: https://www.cnpd.pt/cidadaos/direitos/direito-ao-apagamento-dos-dados/