
3 - Plano persistente associado a uma prova, substituindo a geração "por semana" por um plano completo que depois é apenas "recortado" para apresentação.
4 - Revisão do algoritmo de prescrição (distribuição de intensidade, dias de recuperação, duração mínima, progressão e taper).


Passo 1 — Corrigir o ciclo de vida do plano

Confirmar que o plano:
está associado a uma prova;
tem identidade própria;
é persistido;
não é regenerado por mudança de semana;
só é regenerado por uma ação explícita ou alteração relevante.

Passo 2 — Transformar o Weekly Plan numa janela móvel

Implementar:
hoje no centro;
três dias anteriores;
três dias seguintes;
setas esquerda e direita;
estado da janela em session_state.

Passo 3 — Corrigir as regras de prescrição

Começaria por regras pequenas e testáveis:
nunca gerar duas sessões intensas consecutivas;
permitir dias de descanso em qualquer dia da semana;
diferenciar Recovery, Easy, Endurance e Long;
remover o mínimo universal de 50 minutos;
limitar dias consecutivos;
controlar volume semanal e progressão.

Passo 4 — Só depois melhorar periodização

Depois podemos tratar:
fases do plano;
semanas de descarga;
taper;
especificidade para cada prova.


______________________________________________________




Em vez disso, criaria um Athlete State Score, contínuo, por exemplo entre 1 e 1000 (não apenas 100). Esse valor não seria apresentado ao utilizador; seria apenas uma variável interna que resume o estado fisiológico do atleta.

Por exemplo:

Estado = f(
    CTL,
    ATL,
    TSB,
    VO₂max,
    potência/ritmo nos limiares,
    monotonia,
    strain,
    consistência,
    volume,
    frequência,
    tempo desde última interrupção,
    experiência histórica,
    idade,
    ...
)

Assim:

um atleta completamente sedentário pode estar perto de 1;
um atleta que começou há duas semanas pode estar em 35;
um atleta consistente pode estar em 420;
um atleta de elite pode estar em 900.

O importante é que o algoritmo nunca pergunta:

"És avançado?"

Pergunta apenas:

"Qual é o teu estado fisiológico atual?"

Depois, o Planner passa a trabalhar sobre esse estado.

Em vez de:

Beginner → +10%
Advanced → +5%

faz algo como:

Próxima carga = f(
    AthleteState,
    RaceGoal,
    Dias até à prova,
    Recuperação atual
)

Ou seja, cada treino é consequência do estado fisiológico e não de uma categoria.

Outra vantagem é que o estado evolui continuamente. Se o atleta parar três semanas, o score desce naturalmente porque o CTL diminui, o ATL desaparece e a consistência degrada-se. Não há uma mudança brusca de "Advanced" para "Intermediate".

Uma pequena extensão

Em vez de um único valor, eu criaria um vetor de estado:

AthleteState
├── aerobic_capacity
├── fatigue
├── durability
├── training_consistency
├── recovery_capacity
├── intensity_tolerance
├── long_run_tolerance
└── readiness

Cada componente varia continuamente (0–1000, por exemplo). O Planner decide então:

aumentar volume;
aumentar intensidade;
introduzir VO₂max;
fazer taper;
reduzir carga.

Com base nesse vetor, e não apenas num número.

Acho que esta abordagem encaixa muito bem com a filosofia do PerformanceLab: o planeamento deixa de ser baseado em "regras por nível" e passa a ser baseado no estado fisiológico observado, alimentado pelos indicadores que já calculas (ATL, CTL, TSB, etc.) e por outros que venhas a acrescentar no futuro. Isso torna o sistema muito mais adaptativo e evita os limites artificiais das classificações tradicionais.



___________________________________


Athlete
    │
    ▼
AthleteAnalytics
    │
    ├── Performance Profile
    │       ├── VO₂max
    │       ├── Threshold Pace
    │       ├── Threshold HR
    │       ├── FTP
    │       ├── Running Economy
    │       └── ...
    │
    ├── Training State
    │       ├── CTL
    │       ├── ATL
    │       ├── TSB
    │       ├── ACWR
    │       ├── Monotony
    │       ├── Strain
    │       ├── Recovery
    │       ├── Consistency
    │       └── ...
    │
    └── Planner
            │
            ▼
    TrainingPlan


    _______________________________________________


    Roadmap — Novo Motor de Planeamento Fisiológico
Fase 1 — Fundação
Criar TrainingState (estado atual do atleta).
Criar PerformanceProfile (capacidade fisiológica do atleta).
Tornar ambos objetos imutáveis (@dataclass(frozen=True)).
Não depender do Planner.
Fase 2 — Integração
Adicionar training_state a AthleteAnalytics.
Adicionar performance_profile a AthleteAnalytics.
Construir ambos apenas com informação já existente no projeto.
Fase 3 — Estado de treino

Expandir TrainingState para representar o estado fisiológico atual.

Indicadores iniciais:

CTL
ATL
TSB
ACWR
Training Monotony
Training Strain
Consistency
Weekly Frequency
Days Since Last Workout
Recent Training Load
Training Trend
Recovery Status
Fase 4 — Perfil fisiológico

Expandir PerformanceProfile.

Indicadores iniciais:

VO₂max
FTP
Threshold Heart Rate
Threshold Pace
Threshold Power
Running Economy
Height
Weight
Age
Maximum Heart Rate
Resting Heart Rate
Fase 5 — Capacidades derivadas

Adicionar propriedades de domínio.

Exemplos:

needs_recovery
can_absorb_more_volume
can_tolerate_intensity
long_run_capacity
endurance_capacity
speed_capacity
training_momentum
fatigue_level

Estas propriedades escondem toda a matemática ao restante sistema.

Fase 6 — Refatoração do Planner

O Planner deixa de utilizar diretamente:

CTL
ATL
TSB
ACWR
VO₂max

Passa apenas a consumir:

athlete.analytics.training_state

athlete.analytics.performance_profile
Fase 7 — Planeamento Inteligente

O algoritmo passa a decidir:

fase de treino
volume semanal
intensidade
recuperação
progressão
taper
regeneração

em função do estado fisiológico do atleta e não de categorias como "Beginner" ou "Advanced".