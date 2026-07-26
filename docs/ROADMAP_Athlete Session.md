# PerformanceLab - Persistence & Multi-Athlete Roadmap


Primeiro incremento concreto

O primeiro commit deve limitar-se a:

1. Adicionar athlete_id ao Athlete
2. Criar AthleteRepository
3. Criar JsonAthleteRepository
4. Adaptar os testes de serialização
5. Manter a aplicação a funcionar com um único atleta

Só no commit seguinte adicionamos:

6. Migração do athlete.json atual
7. Lista de atletas
8. Seleção e troca de perfil
9. Criação do segundo atleta

Critérios para considerar a primeira fase concluída
[ ] O Athlete possui um ID persistente
[ ] O app.py não chama diretamente load_athlete/save_athlete
[ ] O JSON está escondido atrás de AthleteRepository
[ ] Guardar e carregar mantém o mesmo athlete_id
[ ] Os testes continuam a passar
[ ] A aplicação continua funcional com um atleta

## Vision

The athlete is the central object of PerformanceLab.

The application should never depend on where data is stored (JSON, SQLite, PostgreSQL or Cloud). It should only interact with an AthleteRepository responsible for loading and saving athlete data.

Long term, an athlete will authenticate into the platform and automatically access their complete profile, history, plans and analytics.

---

# Long-term Architecture

```
Authentication
        │
        ▼
 Athlete ID
        │
        ▼
 AthleteRepository
        │
        ├── JsonRepository      (development)
        ├── SQLiteRepository    (desktop)
        ├── PostgreSQLRepository (server)
        └── APIRepository       (cloud)
        │
        ▼
     Athlete
```

The coaching engine, analytics and UI must remain completely independent of the persistence layer.

---

# Short-term Goal

Replace the current single-athlete JSON approach with a multi-athlete workspace while keeping JSON as the temporary storage backend.

The objective is **not** to invest in JSON, but to invest in a persistence abstraction.

---

# Immediate Tasks

## Phase 1 — Repository abstraction

- Create `AthleteRepository` interface
- Move load/save logic out of `app.py`
- Implement `JsonRepository`

---

## Phase 2 — Multi-athlete support

Replace:

```
data/
    athlete.json
```

with:

```
workspace/

    athletes/

        joao/
            athlete.json

        maria/
            athlete.json
```

(or an equivalent structure)

---

## Phase 3 — Athlete selector

On startup:

```
Select athlete

○ João
○ Maria
○ New athlete
```

No authentication yet.

Simply choose which athlete to load.

---

## Phase 4 — Real athlete validation

Use only real athlete data:

- personal profile
- physiological thresholds
- availability
- goals
- events
- imported workouts
- generated plans

This becomes the primary validation dataset for PerformanceLab.

---

# Future Evolution

### Desktop

```
JsonRepository
        ↓
SQLiteRepository
```

No changes required in coaching or analytics.

---

### Cloud

```
Authentication
        ↓
APIRepository
        ↓
PostgreSQL
```

Again, no changes required in domain logic.

---

# Guiding Principle

PerformanceLab should never ask:

> "Where are the athlete's data stored?"

Instead it should always ask:

```
repository.load(athlete_id)
repository.save(athlete)
```

The storage technology is an implementation detail.

The Athlete remains the centre of the architecture.