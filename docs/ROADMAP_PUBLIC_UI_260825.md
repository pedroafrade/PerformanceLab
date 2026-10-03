# PerformanceLab — Roadmap de operação e evolução da alpha privada

**Atualizado:** 3 de outubro de 2026

**Fonte auditada:** `main`, commit `bfc40a9` (`Add adaptive base training microcycles`).

**Estado:** alpha privada online, conforme confirmação do responsável pelo projeto.
O nome do ficheiro é mantido para preservar as referências existentes.

## 1. Âmbito e evidência

Este roadmap substitui a sequência de preparação anterior ao lançamento.
O objetivo atual é estabilizar a utilização real e evoluir o planeamento de
forma explicável, sem abrir inscrição pública livre.

Há três estados distintos:

| Estado | Evidência necessária |
|---|---|
| Implementado | Código e testes no commit identificado |
| Publicado | Revisão Cloud Run e digest associados ao commit |
| Validado em operação | Registo do teste no ambiente publicado |

A CI do commit auditado terminou com sucesso em Python 3.11 e 3.14 e nas
verificações da imagem Docker. Não confirma o commit publicado, testes móveis,
backups, restauros, fornecedores ativos ou revisão jurídica externa.

## 2. Regras preservadas

- Sem inscrição pública livre; convites individuais e revogáveis.
- Alpha destinada a 3–5 participantes convidados, com 18 anos ou mais.
- Autenticação externa por OIDC e autorização por utilizador e atleta.
- PostgreSQL obrigatório na alpha; JSON apenas para desenvolvimento local.
- Gemini opcional, explicado, consentido e limitado por quotas.
- Exportação, eliminação e informação de privacidade acessíveis.
- Nenhuma exposição de segredos ou dados pessoais em logs e documentação.
- Passado, atividades realizadas e sessões protegidas preservados.
- Uma alteração lógica de cada vez, com testes e confirmação de commit e push.

## 3. Capacidades implementadas

| Área | Estado do código auditado |
|---|---|
| Contratos de aplicação | Casos de uso para importação, edição, eliminação, geração e recuperação do plano |
| Identidade | OIDC Google e email, convites e associação ao atleta autorizado |
| Onboarding | Perfil no primeiro login autorizado, importação e gravação do progresso |
| Persistência | Repositórios PostgreSQL, migrações e correções do ciclo de vida das ligações Streamlit |
| Uploads | Validação, limites, processamento temporário e sensores comprimidos com leitura diferida |
| Training Coach | Consentimento, minimização, quotas partilhadas e tratamento de erros |
| Daily Brief | Persistência, timezone confirmado, quotas e isolamento de falhas |
| Controlo dos dados | Consentimento alpha, exportação, eliminação e Recovery Log privado |
| Plano | Geração, reconciliação, adaptação, Plan Builder, revisões e restore |
| Qualidade | CI, testes de isolamento, preflights e verificações do contentor |

O arranque alpha valida a configuração runtime, a configuração OIDC, a ligação
PostgreSQL e as revisões das migrações antes de iniciar o Streamlit.

## 4. Estado operacional a registar

O deployment já foi executado, conforme confirmação do responsável.
Os restantes pontos abaixo aguardam confirmação documental; isto não significa
que estejam por implementar ou que não tenham sido executados.

| Ponto | Confirmação necessária |
|---|---|
| Versão publicada | Commit, digest e revisão Cloud Run |
| Serviços e região | Google Cloud Run, Google Cloud SQL PostgreSQL, Google Secret Manager e região da União Europeia efetivamente usada |
| Identidade | Login Google/email, convites e recusa de conta não convidada |
| Isolamento | Fluxos críticos com duas contas no ambiente publicado |
| Privacidade | Textos em vigor, contactos reais e revisão jurídica externa |
| Recuperação | backup automático, retenção e restauro real numa base separada |
| Observabilidade | Logs, retenção, alerta real e fornecedor efetivamente ativo |
| Interface | Fluxos essenciais em desktop, Android e iOS, nos temas claro e escuro |
| Suporte | contacto de suporte visível e procedimento de incidente |

Better Stack passou a ser opcional na configuração da alpha. Não confundir
essa opção com ausência de necessidade de monitorização. Confirmar a solução
efetivamente utilizada sem declarar um fornecedor ativo por suposição.

A revisão jurídica externa continua a ser um requisito antes da publicação
final dos textos e de novos convites a participantes reais. Se estiver
pendente, essas ações permanecem bloqueadas. A alpha online não comprova
que a revisão tenha sido concluída. O trabalho técnico pode continuar
sem presumir aprovação jurídica ou autorizar novos convites.

Usar `ALPHA_OPERATIONS_RUNBOOK.md` e `ALPHA_DEPLOYMENT_RECORD_TEMPLATE.md`.
O modelo de registo permanece vazio; a evidência operacional fica fora do
repositório, sem segredos nem dados dos atletas.

## 5. Alterações recentes incorporadas

### Setembro — acesso e persistência

- Identidade visual Journal e login Google/código por email.
- Criação do perfil no primeiro login convidado e onboarding da alpha.
- Correções de transações, ligações PostgreSQL e reconciliação no carregamento.
- Gravação do perfil e proteção do fluxo de importação e conclusão do onboarding.

### Outubro — planeamento e estabilidade

- Persistência do plano e referências habituais de treino do atleta.
- Proteção de recuperação pós-prova e regeneração explícita.
- Menor consumo de memória dos sensores e concorrência Cloud Run limitada.
- Afinidade de sessão configurada para Cloud Run.
- Plan Builder com identidade estável do componente durante alterações do rascunho.
- Volume habitual tratado como referência flexível, mantendo restrições explícitas.
- Preservação de sessões produtivas após semanas de taper, prova e regeneração.
- Microciclos Base com estímulos distintos para estrada/trail e semanas de carga reduzida.

Configuração e código versionados não provam que a respetiva mudança já esteja
aplicada ao serviço publicado.

## 6. Próxima sequência de desenvolvimento

1. Confirmar e registar a revisão realmente publicada e os controlos operacionais.
2. Validar a coerência dos novos microciclos entre geração, edição e adaptação:
   duração, estrutura, carga, recuperação e preservação do estímulo.
3. Atualizar `PLANNING.md`, `TRAINING_SCIENCE.md` e o guia de métricas após
   confirmar as regras atuais, incluindo as exceções ao limite de carga semanal.
4. Repetir a validação visual dos fluxos críticos em desktop e móvel.
5. Priorizar problemas observados pelos participantes com exemplos reproduzíveis.

Não recomeçar a implementação de autenticação, PostgreSQL, reconciliação,
Daily Brief ou Recovery Log como se ainda não existissem.

## 7. Decisões e investigações abertas

- Recomendações: distinguir aviso, aplicação explícita e bloqueio.
- Retenção técnica de revisões removidas após restore.
- Preservação da dose e estrutura dos novos templates durante adaptação.
- Correspondência de várias atividades e sessões planeadas no mesmo dia.
- Metadados explícitos de estímulo e proteção em vez de inferência por texto.
- Uso do feedback subjetivo diário: o Recovery Log existe; confirmar o papel
  de cada campo antes de o integrar nas decisões do motor.
- Sincronização com plataformas externas continua a ser evolução futura.

Os itens acima são prioridades propostas, não compromissos de implementação.

## 8. Critério de conclusão

Cada alteração funcional requer testes específicos, `pytest -q`,
`git diff --check`, validação visual quando aplicável e commit/push confirmados.
Mudanças ao plano devem manter células, gráficos, eventos e persistência na
mesma revisão. Alterações ao ambiente precisam também de registo operacional.

A atualização documental não executa deployment, não altera recursos Google
Cloud nem certifica controlos externos.
