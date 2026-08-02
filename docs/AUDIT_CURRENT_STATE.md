# PerformanceLab — Auditoria do estado atual

**Data da auditoria:** 2 de agosto de 2026  
**Fonte de verdade:** branch `main` do repositório `pedroafrade/PerformanceLab`  
**Âmbito:** documentação, domínio, planeamento, reconciliação, análise, persistência, autenticação, apresentação, dashboard e testes relevantes.

## 1. Conclusão executiva

O motor de domínio do PerformanceLab já é um protótipo funcional bastante avançado. O produto, a documentação e a infraestrutura necessária para uma aplicação pública estão, contudo, várias etapas atrás.

O projeto deixou de ser apenas uma biblioteca de análise. Já possui:

- um atleta como raiz do domínio;
- histórico e eventos persistentes;
- análise fisiológica;
- planeamento completo até à prova;
- periodização;
- uma janela móvel de sete dias;
- reconciliação entre treino planeado e realizado;
- adaptação incremental do futuro;
- importação de atividades;
- autenticação básica;
- persistência multiatleta;
- dashboard Streamlit;
- testes unitários e integrados relevantes.

A prioridade seguinte não deve ser acrescentar novas métricas isoladas. Deve ser alinhar documentação, correção científica, experiência do utilizador, segurança e operação em torno de uma primeira versão pública claramente delimitada.

## 2. Arquitetura atual

O fluxo conceptual principal é:

```text
Athlete
├── History
├── Events
├── TrainingPlan
└── AthleteAnalytics
    ├── TrainingState
    └── PerformanceProfile

Event + TrainingState + PerformanceProfile
                    ↓
                 Planner
                    ↓
            TrainingPlan persistente
                    ↓
             WeeklyPlan móvel

History + TrainingPlan + TrainingState
                    ↓
              Reconciler
                    ↓
                Adapter
                    ↓
       TrainingPlan futuro adaptado
```

Esta arquitetura está globalmente alinhada com a forma como atletas e treinadores pensam:

- o histórico representa factos passados;
- os eventos representam objetivos futuros;
- a análise interpreta o atleta;
- o plano representa uma estratégia persistente;
- a janela semanal apresenta uma parte do plano;
- a reconciliação compara intenção e realidade;
- a adaptação altera apenas o futuro.

## 3. Pontos fortes

### 3.1. Domínio centrado no atleta

`Athlete` funciona como raiz do domínio e agrega histórico, eventos, objetivos, configuração, análise e plano. Isto evita que a aplicação seja organizada em torno de ficheiros FIT, componentes Streamlit ou métricas isoladas.

### 3.2. Separação entre factos, análise e planeamento

`History` guarda atividades realizadas. `AthleteAnalytics` calcula e apresenta o estado do atleta. O Planner trabalha sobre objetos de domínio, em particular `TrainingState` e `PerformanceProfile`, em vez de depender diretamente de CTL, ATL ou TSB dispersos pela aplicação.

### 3.3. Ciclo de vida correto do plano

O `TrainingPlan` contém o plano completo e persistente. O `WeeklyPlan` é apenas uma janela móvel de sete dias. Navegar no calendário não regenera o plano.

### 3.4. Periodização e especificidade

O planeamento já contempla Build, Peak, Taper, Race, Transition e Regeneration, além de modalidade da prova, provas múltiplas, treinos longos, sessões exigentes, recuperação e taper.

### 3.5. Reconciliação incremental

O sistema já consegue:

- comparar treino planeado e atividade realizada;
- classificar `pending`, `missed`, `equivalent`, `modified` e `substitute`;
- calcular diferença de carga quando existem dados suficientes;
- reconhecer atividades tardias;
- reconhecer várias atividades no mesmo dia;
- reconhecer atividades revistas;
- guardar identidades e assinaturas reconciliadas;
- evitar repetir a mesma adaptação;
- reconciliar dias fechados ao abrir a aplicação.

### 3.6. Adaptação conservadora

O adaptador:

- preserva treinos passados;
- altera apenas treinos futuros;
- não altera provas, taper, shakeout, pre-race ou recovery;
- responde proporcionalmente à carga em excesso;
- recupera apenas uma fração limitada de carga em falta;
- tenta preservar a família da modalidade planeada;
- não move automaticamente um treino falhado para o dia seguinte.

### 3.7. Persistência com evolução de formato

A serialização JSON já suporta versões de formato, identidade persistente de atividades, estado de reconciliação e gravação atómica através de ficheiro temporário.

### 3.8. Testes relevantes

Existem testes para o domínio, planeamento, periodização, persistência, apresentação, importação, reconciliação e adaptação. Os fluxos recentes também possuem testes integrados desde a entrada da atividade no histórico até à alteração do plano do atleta.

## 4. Riscos e dívida técnica

### 4.1. O código está mais avançado do que a documentação

O `README.md` ainda descreve o projeto como estando numa fase inicial de fundação. Essa classificação já não corresponde ao código existente.

Consequências:

- novos contributos podem partir de pressupostos errados;
- decisões atuais não estão documentadas;
- funcionalidades concluídas continuam listadas como futuras;
- não existe uma definição clara da primeira aplicação pública.

### 4.2. Contradição sobre modalidade e estímulo

O Manifesto afirma que o objetivo fisiológico é mais importante do que a modalidade. A ideia necessita de maior precisão.

A formulação recomendada é:

> A carga fisiológica pode ser comparada entre modalidades, mas a especificidade do estímulo não é totalmente transferível.

Exemplos:

- ciclismo fácil pode contribuir para endurance;
- ciclismo Z2 não substitui automaticamente LT2 Run;
- um longo de bicicleta não reproduz toda a especificidade musculoesquelética de um longo de trail;
- a modalidade principal continua a ser determinada pela prova.

### 4.3. Roadmaps atuais não são normativos

Os documentos de roadmap atuais misturam trabalho concluído, ideias, notas de conversa, hipóteses antigas e decisões arquiteturais. Devem ser arquivados e substituídos por um único roadmap priorizado.

### 4.4. Fronteira de apresentação incompleta

`performancelab/presentation/dashboard.py` conhece Streamlit. A camada de apresentação deveria apenas produzir modelos prontos para a UI.

A dependência desejada é:

```text
domínio → modelos de apresentação → app Streamlit
```

e nunca:

```text
domínio ou apresentação → Streamlit
```

### 4.5. Código legado e duplicação

Foram identificados sinais de transição ainda não concluída:

- `app/app_backup.py` permanece no repositório;
- existem implementações semanais e mensais muito semelhantes;
- existem componentes antigos e novos para alguns resumos;
- `app/app.py` concentra autenticação, inicialização, demonstração, navegação, reconciliação e persistência;
- os contratos dos repositórios ainda incluem documentação herdada do modelo de atleta único.

### 4.6. Dependências inconsistentes

`pyproject.toml` e `requirements.txt` não declaram o mesmo conjunto de dependências. Streamlit, Plotly e `fitdecode` aparecem apenas no segundo.

Antes de uma publicação deve existir uma única fonte de dependências, com versões suportadas e processo de instalação reproduzível.

### 4.7. Ausência de integração contínua

Não foi identificado um workflow GitHub Actions que execute automaticamente os testes. A qualidade depende atualmente da execução manual local.

### 4.8. Autenticação inadequada para utilização pública

A autenticação atual identifica o utilizador apenas por email. Não existe password, hash, sessão persistente, recuperação de conta nem integração com um fornecedor de identidade.

Isto é adequado para desenvolvimento local, mas bloqueia uma aplicação pública com dados reais.

### 4.9. JSON não é persistência pública

A abstração por repositório está corretamente encaminhada. Porém, ficheiros JSON locais não resolvem:

- concorrência entre utilizadores;
- controlo de acesso;
- sessões distribuídas;
- backups operacionais;
- auditoria;
- migrações transacionais;
- recuperação após falhas;
- escalabilidade de consultas.

### 4.10. Contrato semântico da carga planeada

`planned_workout_rpe()` reconhece um conjunto limitado de intensidades semânticas. É necessário confirmar que todas as intensidades produzidas pelo Planner possuem uma tradução de carga.

Devem ser auditados, entre outros:

- Tempo;
- LT2;
- Threshold;
- Recovery;
- combinações como Easy to moderate;
- sessões de prova e pre-race.

Uma sessão sem intensidade reconhecida pode ficar sem carga planeada e limitar a reconciliação.

### 4.11. Identidade de atividades importadas

O `workout_id` persistente é uma boa base. A deteção de duplicados ainda depende de data, modalidade, duração e distância dentro de tolerâncias. Para integrações públicas deverá considerar-se também a identidade fornecida pela origem, quando disponível.

### 4.12. Mutabilidade e responsabilidades do plano

O plano é corretamente persistente e precisa de poder evoluir. Ainda assim, existem mutações diretas durante a reconciliação. A médio prazo deverá ser avaliado se cada revisão do plano deve produzir explicitamente uma nova versão imutável ou um registo de alterações.

## 5. Auditoria do dashboard

### 5.1. O que funciona

- A primeira linha comunica atividade recente, plano semanal e próxima prova.
- O plano semanal ocupa corretamente o centro visual.
- A janela móvel de sete dias é compreensível.
- A prova seguinte possui boa visibilidade.
- O treino seguinte contém instruções concretas.
- A composição é limpa e relativamente consistente.
- A sidebar contém as ações essenciais do protótipo.

### 5.2. Precisão inadequada

O cartão Recovery apresenta um valor com precisão interna, por exemplo:

```text
83.20545327702672
```

Para o atleta, a apresentação deveria ser semelhante a:

```text
83
Boa recuperação
Treino normal recomendado
```

A complexidade matemática deve permanecer no software.

### 5.3. Training Summary sem janela temporal

O cartão mostra totais como número de treinos, dias, duração e modalidades, mas não identifica claramente o período. Visualmente parece um resumo atual, embora os valores aparentem ser totais históricos.

O dashboard deve escolher uma janela explícita, por exemplo:

- últimos 7 dias;
- últimas 4 semanas;
- mês atual;
- época completa.

Para o dashboard principal recomenda-se “Últimos 7 dias”.

### 5.4. Physiology dominado por dados ausentes

O cartão reserva uma área grande para métricas apresentadas como `—`.

Alternativas:

- mostrar apenas métricas disponíveis;
- explicar como obter cada métrica;
- usar um estado vazio compacto;
- encaminhar para configuração ou importação adequada.

### 5.5. CTL, ATL e TSB sem interpretação suficiente

Os valores técnicos são apresentados com destaque, mas não explicam a escala, período, tendência ou decisão associada.

A hierarquia recomendada é:

1. estado interpretado;
2. recomendação;
3. tendência;
4. valores técnicos como detalhe.

### 5.6. Duplicação entre Weekly Plan e Next Workout

O plano semanal já identifica a próxima sessão. O cartão Next Workout repete a informação e ocupa uma altura muito superior aos restantes cartões.

As instruções detalhadas podem aparecer:

- quando se seleciona um dia;
- num painel lateral;
- numa secção expansível abaixo do calendário.

### 5.7. Hierarquia vertical desequilibrada

O cartão Next Workout prolonga-se muito para baixo, enquanto os cartões adjacentes terminam cedo. O resultado é uma zona vazia ampla e uma leitura fragmentada.

### 5.8. Timeline de fases demasiado pequeno

Os pontos de Build, Peak, Taper, Race e Regeneration contêm informação importante, mas são demasiado pequenos para leitura confortável.

Uma alternativa mais acionável:

```text
Peak — semana 2 de 3
Próxima fase: Taper em 12 dias
```

### 5.9. Idioma inconsistente

A navegação e os cartões misturam português e inglês. Antes da primeira UI pública deve existir uma decisão explícita:

- português;
- inglês;
- internacionalização completa.

### 5.10. Importação comprimida na sidebar

A importação é uma operação central, mas surge numa área pequena no fundo da sidebar.

O fluxo público recomendado é:

1. escolher ficheiros;
2. validar;
3. mostrar atividades encontradas;
4. identificar novas, atualizadas e duplicadas;
5. confirmar a importação;
6. explicar qualquer adaptação aplicada ao plano.

### 5.11. Elementos técnicos do Streamlit

O menu da aplicação expõe opções como Deploy, Rerun e Clear cache. Estes elementos não devem fazer parte da experiência pública.

### 5.12. Resumos semanal e mensal

Existem componentes separados com muita lógica e CSS repetidos. O dashboard também utiliza o espaço inferior de forma pouco equilibrada. Os resumos devem partilhar modelos, formatadores e componentes.

## 6. Estrutura documental recomendada

Os documentos normativos recomendados são:

| Documento | Responsabilidade |
| --- | --- |
| `README.md` | Produto, estado atual, instalação e navegação |
| `docs/PRODUCT_VISION.md` | Propósito, utilizador-alvo, princípios e limites |
| `docs/DOMAIN_MODEL.md` | Objetos de domínio e relações reais |
| `docs/ARCHITECTURE.md` | Camadas, dependências e fluxos |
| `docs/TRAINING_SCIENCE.md` | Métricas, pressupostos, fórmulas e limitações |
| `docs/PLANNING.md` | Geração, periodização, reconciliação e adaptação |
| `docs/ROADMAP.md` | Trabalho futuro priorizado |

Também se recomenda:

```text
docs/decisions/
├── ADR-001-training-plan-lifecycle.md
├── ADR-002-cross-sport-load.md
├── ADR-003-reconciliation-identity.md
└── ADR-004-presentation-boundaries.md
```

Os roadmaps históricos devem ser removidos da documentação normativa ou movidos para `docs/archive/`.

## 7. Decisão recomendada

O próximo ciclo deve começar pela documentação e pelos contratos do produto, antes de uma reformulação visual.

A ordem recomendada é:

1. registar esta auditoria;
2. aprovar o roadmap público;
3. reescrever `PRODUCT_VISION.md`;
4. reescrever o modelo de domínio e arquitetura;
5. documentar ciência, planeamento e adaptação;
6. auditar contratos científicos;
7. redesenhar a arquitetura de informação do dashboard;
8. só depois alterar componentes visuais.

## 8. Regra orientadora

Cada nova funcionalidade deve responder afirmativamente a três perguntas:

1. Ajuda o atleta a tomar uma decisão melhor?
2. A decisão é explicável com os dados disponíveis?
3. A funcionalidade respeita as fronteiras entre domínio, apresentação e infraestrutura?

