# PerformanceLab - Persistence & Multi-Athlete Roadmap


Roadmap — Identity & Access

1. Modelo de utilizador
Criar performancelab/identity.py.
Introduzir User.
Distinguir os papéis athlete e coach.
Associar diretamente um utilizador-atleta ao respetivo athlete_id.

2. Testes do modelo
Confirmar que cada utilizador recebe um user_id.
Validar email.
Validar os papéis permitidos.
Garantir que um utilizador com papel athlete tem athlete_id.

3. Serviço de autenticação
Criar performancelab/authentication.py.
Implementar login temporário sem password.
Guardar o utilizador autenticado.
Implementar logout.

4. Persistência de utilizadores
Criar um UserRepository.
Começar com JSON.
Manter a possibilidade de migrar para SQLite ou PostgreSQL.

5. Controlo de acesso
Atleta: acesso apenas ao próprio athlete_id.
Treinador: acesso aos atletas que lhe forem atribuídos.
Não colocar esta lógica diretamente no app.py.

6. Integração com Streamlit
Mostrar login quando não existe utilizador autenticado.
Carregar diretamente o atleta do utilizador.
Mostrar seletor apenas quando o utilizador é treinador.

7. Autenticação real
Adicionar passwords com hash seguro ou serviço externo.
Sessões persistentes.
Recuperação de acesso.
OAuth, caso venha a fazer sentido.

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