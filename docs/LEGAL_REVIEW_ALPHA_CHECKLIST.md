# Revisão Jurídica — Alpha Privada do PerformanceLab

**Preparado em:** 25 de agosto de 2026  
**Estado:** REVISÃO EXTERNA PENDENTE  
**Âmbito:** alpha privada para 3–5 participantes convidados, exclusivamente com 18 anos ou mais

> Este documento organiza a revisão. Não constitui uma aprovação jurídica e não deve ser assinalado como concluído pelo autor técnico do projeto.

## 1. Documentos para revisão

O revisor deverá receber as versões atuais de:

- `docs/PRIVACY_POLICY_ALPHA_DRAFT.md`;
- `docs/RETENTION_POLICY_ALPHA_DRAFT.md`;
- `docs/DATA_RIGHTS_PROCEDURE_ALPHA_DRAFT.md`;
- `docs/ROADMAP_PUBLIC_UI_260825.md`;
- aviso de participação apresentado no primeiro login;
- aviso e autorização separados do Training Coach;
- descrição da exportação e eliminação integral;
- lista final de fornecedores e regiões;
- termos e documentação dos fornecedores relevantes.

## 2. Contexto da alpha

Confirmar que a revisão considera:

- acesso apenas por convite;
- 3–5 participantes;
- todos os participantes com 18 anos ou mais;
- autenticação externa por Google OIDC;
- perfil e atividades de treino;
- localização e rotas;
- frequência cardíaca e indicadores físicos;
- feedback subjetivo;
- PostgreSQL remoto;
- Google Gemini opcional;
- recomendações experimentais de treino;
- ausência de aconselhamento ou finalidade médica;
- exportação e eliminação pelo participante.

## 3. Identificação do responsável

Antes da publicação, confirmar:

- [ ] nome completo ou entidade responsável;
- [ ] morada ou identificação exigida;
- [ ] país de estabelecimento;
- [ ] email de privacidade;
- [ ] contacto de suporte;
- [ ] necessidade de encarregado de proteção de dados;
- [ ] papéis e responsabilidades efetivas.

Valores ainda pendentes no repositório:

- responsável pelo tratamento;
- email de privacidade.

## 4. Categorias de dados

Rever a descrição de:

- identidade e conta;
- convite e autorização;
- perfil do atleta;
- atividades;
- rotas e coordenadas;
- frequência cardíaca;
- desempenho e recuperação;
- sono, stress, motivação, dor e rigidez;
- objetivos e provas;
- planos e adaptações;
- VO₂max e outros indicadores;
- interpretações do Training Coach;
- consentimentos;
- metadados operacionais.

Confirmar:

- [ ] classificação dos dados relacionados com saúde;
- [ ] necessidade e proporcionalidade de cada categoria;
- [ ] dados que devem ser removidos ou descritos de outra forma;
- [ ] aplicação do artigo 9.º do RGPD;
- [ ] adequação da exclusão de menores.

## 5. Finalidades e fundamentos jurídicos

Para cada finalidade, o revisor deverá indicar:

- finalidade específica;
- fundamento do artigo 6.º;
- eventual condição do artigo 9.º;
- necessidade de consentimento;
- possibilidade e efeito da retirada;
- tratamentos necessários para prestar o serviço;
- interesses legítimos, se aplicáveis;
- obrigações legais, se aplicáveis.

Finalidades a rever:

- autenticação;
- gestão de convites;
- autorização;
- perfil e histórico;
- importação;
- análise de treino;
- planeamento;
- Training Coach;
- segurança;
- limites de utilização;
- diagnóstico de falhas;
- suporte;
- exercício de direitos;
- melhoria da alpha.

**Decisão pendente:** fundamentos jurídicos por finalidade.

## 6. Consentimento da alpha

Confirmar:

- [ ] se o consentimento é o fundamento adequado para a participação;
- [ ] separação entre participação e Training Coach;
- [ ] linguagem clara e específica;
- [ ] caráter voluntário;
- [ ] possibilidade real de retirada;
- [ ] consequências da retirada;
- [ ] versão e data guardadas;
- [ ] tratamento de dados relacionados com saúde;
- [ ] necessidade de nova aceitação após alterações materiais.

## 7. Training Coach e Google Gemini

Confirmar:

- [ ] papel jurídico do fornecedor;
- [ ] categorias exatas enviadas;
- [ ] minimização do payload;
- [ ] ausência de ficheiros originais;
- [ ] fundamento para o envio;
- [ ] validade da autorização separada;
- [ ] retirada;
- [ ] retenção no fornecedor;
- [ ] utilização dos dados pelo fornecedor;
- [ ] localização do tratamento;
- [ ] transferências internacionais;
- [ ] mecanismo e garantias;
- [ ] informação necessária ao participante;
- [ ] adequação dos limites das recomendações.

## 8. Fornecedores e subprocessadores

Obter e rever, para cada fornecedor:

- nome legal;
- serviço utilizado;
- função;
- papel jurídico;
- contrato ou termos;
- acordo de tratamento de dados;
- subprocessadores;
- região;
- localização de backups;
- medidas de segurança;
- retenção;
- eliminação;
- transferências;
- mecanismo jurídico;
- contacto de privacidade.

Fornecedores a confirmar:

- Google OIDC;
- Google Gemini;
- alojamento da aplicação;
- PostgreSQL;
- backups;
- logging;
- alertas e captura de exceções.

Não concluir esta secção com base apenas no código-fonte.

## 9. Transferências internacionais

Confirmar:

- [ ] países envolvidos;
- [ ] entidades importadoras;
- [ ] decisão de adequação, quando aplicável;
- [ ] cláusulas contratuais-tipo, quando aplicável;
- [ ] medidas suplementares;
- [ ] informação ao participante;
- [ ] possibilidade de evitar ou reduzir transferências.

**Decisão pendente:** transferências e garantias por fornecedor.

## 10. Conservação

Rever os prazos aprovados:

- contas inativas: 90 dias;
- aviso: 14 dias;
- metadados do Training Coach: 30 dias;
- prova de consentimento após eliminação: 0 dias;
- convites não utilizados: 14 dias;
- convites expirados ou revogados: 7 dias;
- logs: 14 dias;
- erros e alertas: 30 dias;
- backups: 14 dias;
- suporte e direitos: 90 dias;
- fim da alpha: 30 dias.

Confirmar:

- [ ] adequação de cada prazo;
- [ ] evento inicial de cada prazo;
- [ ] compatibilidade da eliminação de consentimentos com obrigações de prova;
- [ ] exceções legais;
- [ ] eliminação em fornecedores;
- [ ] tratamento de dados eliminados em backups;
- [ ] impedimento de reativação após restauro.

## 11. Direitos dos participantes

Rever:

- acesso;
- correção;
- exportação;
- portabilidade;
- eliminação;
- limitação;
- oposição;
- retirada de consentimento;
- reclamação à CNPD.

Confirmar:

- [ ] canal;
- [ ] verificação de identidade;
- [ ] prazo de um mês;
- [ ] prorrogação;
- [ ] comunicação de recusa;
- [ ] segurança da entrega;
- [ ] registo mínimo;
- [ ] retenção do pedido;
- [ ] mecanismo operacional de limitação.

## 12. Exportação

Confirmar:

- [ ] completude;
- [ ] formato legível;
- [ ] adequação para portabilidade;
- [ ] isolamento por participante;
- [ ] ausência de segredos;
- [ ] método de entrega;
- [ ] ausência de cópia adicional no servidor.

## 13. Eliminação

Confirmar:

- [ ] confirmação forte;
- [ ] âmbito dos dados ativos;
- [ ] eliminação da conta;
- [ ] eliminação do atleta;
- [ ] consentimentos;
- [ ] metadados do Training Coach;
- [ ] convites;
- [ ] autorizações;
- [ ] efeito nos fornecedores;
- [ ] efeito nos backups;
- [ ] confirmação ao participante;
- [ ] exceções legalmente justificadas.

## 14. Decisões automatizadas e recomendações

Confirmar:

- [ ] descrição das regras e cálculos;
- [ ] descrição do Training Coach;
- [ ] ausência de efeitos jurídicos;
- [ ] possibilidade de erro;
- [ ] ausência de finalidade médica;
- [ ] ausência de aconselhamento médico;
- [ ] necessidade de informação adicional;
- [ ] aplicabilidade do artigo 22.º do RGPD.

## 15. Segurança e incidentes

Rever, depois da implementação da fase G:

- autenticação;
- autorização;
- isolamento;
- segredos;
- logging;
- alertas;
- backups;
- restauro;
- rollback;
- incidentes;
- acessos administrativos.

Confirmar:

- [ ] procedimento de violação de dados;
- [ ] avaliação de risco;
- [ ] registo de incidentes;
- [ ] notificação à CNPD, quando aplicável;
- [ ] comunicação aos participantes, quando aplicável;
- [ ] contactos e responsabilidades;
- [ ] prazos legais.

## 16. Avaliação de impacto

O revisor deverá indicar:

- [ ] se é necessária uma avaliação de impacto sobre a proteção de dados;
- [ ] fatores de risco relevantes;
- [ ] medidas adicionais;
- [ ] momento em que deverá estar concluída;
- [ ] necessidade de consulta prévia.

A decisão deverá considerar dados relacionados com saúde, localização, monitorização de treino, inteligência artificial e participantes reais.

## 17. Texto final e publicação

Antes da aprovação, confirmar:

- [ ] remoção de todos os campos `[POR DEFINIR]`;
- [ ] coerência entre documentos;
- [ ] coerência entre documentos e aplicação;
- [ ] linguagem clara;
- [ ] versões e datas;
- [ ] contacto funcional;
- [ ] fornecedores reais;
- [ ] regiões reais;
- [ ] fundamentos jurídicos;
- [ ] retenção;
- [ ] direitos;
- [ ] processo de alterações;
- [ ] necessidade de nova aceitação.

## 18. Registo da revisão externa

Preencher apenas após revisão efetiva:

- Revisor: `[PENDENTE]`
- Organização: `[PENDENTE]`
- Qualificação ou função: `[PENDENTE]`
- Data: `[PENDENTE]`
- Documentos e versões revistos: `[PENDENTE]`
- Resultado: `[PENDENTE — APROVADO / ALTERAÇÕES NECESSÁRIAS / NÃO APROVADO]`
- Restrições ou condições: `[PENDENTE]`
- Próxima revisão: `[PENDENTE]`

## 19. Critério de conclusão

O passo 9 só pode ser concluído quando:

1. existir um revisor jurídico identificado;
2. as decisões estiverem documentadas;
3. as alterações necessárias forem aplicadas;
4. os testes estiverem atualizados;
5. todos os campos obrigatórios estiverem preenchidos;
6. o resultado da revisão estiver registado;
7. a política continuar marcada como rascunho até aprovação efetiva.

## 20. Estado atual

**REVISÃO EXTERNA NÃO REALIZADA**

A existência desta checklist não significa que a política foi revista ou aprovada.