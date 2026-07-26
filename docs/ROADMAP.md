# PerformanceLab Roadmap

---

ONGOING

Vamos começar por: 
1. Eventos – fazer o planeador olhar para provas futuras e periodizar automaticamente, 

4. Qualidade dos treinos – enriquecer o WorkoutGenerator para produzir sessões mais variadas e específicas.

5. Prioridade alta: tornar as estratégias dependentes do desporto (running, cycling, triathlon, etc.), ajustando volume, sessões intensas e sessões longas.
6. Prioridade média: distinguir eventos A/B/C (prova principal vs secundária), para que uma corrida de treino não desencadeie a mesma recuperação que uma maratona-alvo.
7. Prioridade média: considerar a distância/tipo do evento (5 km, meia maratona, maratona, ultra), adaptando a recuperação pós-prova.
8. Prioridade baixa: usar o histórico das últimas semanas (consistência, carga, progressão) para personalizar ainda mais a estratégia.

9. O plano não deveria ser gerado a cada semana, mas por provas. No weekly plan, a semana deveria ir avançando - o centro deveria ser sempre o dia actual, à esquerda com os 3 dias anteriores e à direita com os 3 dias seguintes. Isto evitaria o que acontece agora, que ao Domingo, não é visivel o treino de segunda-feira. Devem ser ainda implementadas setas de forma a poder fazer scroll horizontal para os dias passados e para os futuros.
____________________________

Eu também reparei noutra coisa

Neste momento a máquina de estados é apenas baseada em:

days_until_event

Mas um treinador normalmente pensa em dois estados:

Antes da prova
↓

Base
Build
Peak
Taper
Race

Depois da prova
↓

Regeneration
↓
Maintenance
↓
Base...

Só que isso assume que não existe outra competição logo a seguir.

________________________


# Version 0.1

## Foundation

### Goals

- Athlete model
- Sensor model
- Session model
- Synchronization
- Sensor comparison
- Metrics
- History
- GitHub repository

### Status

✅ Completed

---

# Version 0.2

## Domain Architecture

### Goals

- Complete domain redesign
- Workout package
- History package
- Goals package
- Race package
- Analysis package
- Athlete as root object
- Workout model
- Goal model
- Event model
- GoalBook
- EventBook
- AthleteAnalytics
- Unit tests
- Stable internal architecture

### Status

✅ Completed

---

# Version 0.3

## Athlete Analytics

### Goals

- Weekly statistics
- Monthly statistics
- Yearly statistics
- Distance analysis
- Duration analysis
- Elevation analysis
- Training consistency
- Sport distribution
- Goal progress
- Event analysis
- Summary reports

### Status

🚧 In Progress

---

# Version 0.4

## Training Physiology

### Goals

- Training Load
- Acute Training Load (ATL)
- Chronic Training Load (CTL)
- Training Stress Balance (TSB)
- Recovery analysis
- HR Drift
- Cardiac Efficiency
- Fatigue detection
- Performance trends

### Status

⬜ Planned

---

# Version 0.5

## Athlete Intelligence

### Goals

- Recommendation engine
- Recovery prediction
- Performance prediction
- Heat adaptation
- Terrain adaptation
- Training adaptation
- Personalised insights

### Status

⬜ Planned

---

# Version 0.6

## Natural Language

### Goals

- Conversational interface
- Athlete reports
- Coach reports
- Session explanations
- Automatic summaries
- Training recommendations in natural language

### Status

⬜ Planned

---

# Version 1.0

## Public Release

### Goals

- Stable API
- Complete documentation
- Tutorials
- Examples
- Full unit test coverage
- Continuous Integration
- First public release

### Status

⬜ Planned

---

# Long-Term Vision

PerformanceLab aims to become a complete endurance training analysis framework.

The project is organised around a single domain object:

```
Athlete
│
├── History
│     └── Workout
│
├── GoalBook
│     └── Goal
│
├── Calendar (EventBook)
│     └── EventEntry
│             └── Event
│
└── AthleteAnalytics
```

Every future feature should extend this architecture rather than replace it.

The long-term objective is to provide a flexible framework capable of analysing, interpreting and predicting endurance performance while remaining independent of any specific sport, device or data source.