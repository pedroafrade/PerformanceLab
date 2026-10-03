# PerformanceLab — handout de continuidade

**Atualizado:** 3 de outubro de 2026

## 1. Fonte da verdade

Repositório: https://github.com/pedroafrade/PerformanceLab

Fonte auditada: `main`, commit `bfc40a9` (`Add adaptive base training microcycles`).
A CI desse commit terminou com sucesso. Antes de cada alteração, consultar o
GitHub, confirmar a versão atual e ler os ficheiros relevantes.

Este handout sucede ao `HANDOUT_260814.md`, fornecido pelo utilizador como
anexo histórico. O anexo não foi encontrado na árvore atual do repositório.
O documento arquivado `docs/archive/HANDOUT 260801.md` permanece histórico.

## 2. Modo de trabalho

O utilizador aplica manualmente as alterações no VSCode, usando PowerShell.

- Consultar o GitHub sem escrever diretamente no repositório.
- Entregar patch ou ficheiros completos com caminhos e instruções inequívocas.
- Um commit lógico de cada vez; aguardar confirmação de pytest, commit e push.
- Preservar alterações locais; nunca usar `git add .` nem adicionar `data/`.
- Não adicionar patches temporários, exportações, backups ou segredos ao Git.
- A UI apresenta; regras e cálculos pertencem ao domínio ou presenter apropriado.
- Usar dataclasses imutáveis quando apropriado.

Cada entrega deve terminar com pytest específico, pytest completo,
necessidade de reinício, confirmação visual e comandos explícitos de
`git add`, `git commit` e `git push`.

## 3. Estado do produto e operação

A alpha privada está online, conforme confirmação do responsável em 3 de
outubro. A interface usa a identidade visual Journal.

Implementação, publicação e validação operacional são estados distintos.
O commit auditado não identifica automaticamente a revisão no Cloud Run.
Registar commit/digest publicados, região, contactos, revisão jurídica,
backups, restauro, monitorização e testes reais em dispositivos.
Better Stack é opcional; confirmar a solução de alertas efetivamente usada.

## 4. Capacidades existentes

- Login OIDC Google e código por email; convites e associação ao atleta autorizado.
- Perfil no primeiro login e onboarding com importação e gravação do progresso.
- PostgreSQL, migrações, autorização e testes de isolamento.
- Importação FIT/FIT.GZ/GPX e CSV auxiliar do Strava para títulos.
- Histórico, análise fisiológica, recuperação intradiária e tendências Development.
- Observações factuais e tendências VO2max com modelos de apresentação próprios.
- Geração e persistência do plano; reconciliação e adaptação incremental do futuro.
- Plan Builder, avaliação de impacto, revisões recuperáveis e restore.
- Daily Brief persistido e Training Coach com consentimento e quotas.
- Recovery Log privado, exportação e eliminação dos dados do participante.
- CI em Python 3.11/3.14 e verificações de segurança e saúde do contentor.

Os próximos passos de VO2max, cartões históricos, autenticação e persistência
descritos no handout de agosto já não devem ser assumidos como por implementar.
Confirmar o comportamento atual antes de criar nova funcionalidade.

## 5. Alterações mais recentes

| Commit | Resultado |
|---|---|
| `9a4ae42` | Persistência do plano e referências habituais do atleta |
| `7be2671` | Recuperação pós-prova e regeneração explícita |
| `652c2d4` | Sensores comprimidos com leitura diferida e menor concorrência Cloud Run |
| `14c30f5` | Volume semanal flexível e afinidade de sessão |
| `fb72fbc` | Sessões produtivas preservadas entre fases |
| `bfc40a9` | Microciclos Base e identidade estável do componente Plan Builder |

O motor distingue Continuous Tempo, Threshold Cruise, Aerobic Hills e Easy +
Strides. A rotação depende da modalidade da prova e das semanas até ao evento;
há semanas de consolidação com menor carga. Estas são regras da implementação,
não uma certificação científica ou clínica.

## 6. Invariantes a preservar

- `TrainingPlan` é o plano completo persistente; `WeeklyPlan` é uma janela.
- Navegar ou abrir a aplicação não deve regenerar todo o plano.
- Reconciliar repetidamente os mesmos dados não reaplica a mesma adaptação.
- Adaptação altera apenas o futuro elegível e preserva provas e fases protegidas.
- Atividades realizadas e passado não são reescritos por alterações futuras.
- Restrições explícitas prevalecem sobre preferências e volume habitual.
- Células, gráficos, eventos e persistência devem representar a mesma revisão.
- Texto do Coach não altera autonomamente o plano.
- Recovery Log permanece privado e não é enviado ao Coach/IA.

## 7. Próximo trabalho proposto

Depois deste commit documental, confirmar o ambiente publicado e investigar
a coerência dos novos microciclos durante adaptação e edição.

Ficheiros a consultar antes de propor alterações:

- `performancelab/coaching/strategies/base.py`;
- `performancelab/coaching/workout_templates.py`;
- `performancelab/coaching/workout_generator.py`;
- `performancelab/training/planning/planner.py`;
- `performancelab/training/planning/training_plan_adapter.py`;
- `performancelab/training/planning/plan_builder_assessment.py`;
- `app/components/plan_page.py`;
- testes correspondentes em `tests/coaching/` e `tests/test_october_plan_regression.py`.

Verificar se duração, estrutura, dose e carga continuam coerentes após uma
adaptação. O adaptador ainda identifica estímulos por texto e contém estrutura
genérica de threshold; a preservação dos novos templates é uma investigação,
não um defeito já reproduzido.

Rever depois `PLANNING.md`, `TRAINING_SCIENCE.md` e o guia de métricas. O volume
habitual passou a ser flexível e o limite de crescimento semanal tem exceções
para preservar sessões produtivas. Não descrever o limite como universal.

## 8. Decisões abertas

- Aviso, aplicação explícita e bloqueio das recomendações.
- Retenção técnica de revisões removidas após restore.
- Correspondência de várias atividades/sessões no mesmo dia.
- Metadados de estímulo e proteção em vez de identificação por texto.
- Papel do feedback subjetivo diário nas decisões determinísticas.

Estas decisões precisam de exemplos e critérios concretos antes de implementação.

## 9. Documentação de referência

- `README.md`: produto, instalação e navegação.
- `ROADMAP_PUBLIC_UI_260825.md`: prioridades atuais da alpha.
- `APP_PAGE_IMPROVEMENTS_260903.md`: histórico de UI e validação contínua.
- `ALPHA_OPERATIONS_RUNBOOK.md`: publicação, recuperação e incidentes.
- `ALPHA_DEPLOYMENT_RECORD_TEMPLATE.md`: modelo vazio para registos externos.
- `PRODUCT_VISION.md`, `DOMAIN_MODEL.md`, `ARCHITECTURE.md`,
  `TRAINING_SCIENCE.md` e `PLANNING.md`: referência a confrontar com o código.
- `AUDIT_CURRENT_STATE.md`: auditoria histórica de 2 de agosto de 2026.

Não retomar listas históricas sem verificar o código atual. A próxima conversa
deve começar pela leitura do GitHub, não por repetir o último passo de agosto.
