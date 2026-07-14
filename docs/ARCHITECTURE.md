# PerformanceLab Architecture

## Vision

PerformanceLab is not intended to be just another training analysis library.

Its goal is to provide a complete digital representation of an endurance athlete, combining historical data, physiological information, objectives and intelligent analysis into a single coherent framework.

The project is designed around the athlete rather than around activity files.

---

# Core Principles

## Athlete-centric design

The athlete is the central object of the framework.

Everything else exists to describe:

- who the athlete is
- what the athlete has done
- what the athlete wants to achieve
- how the athlete is adapting

Training sessions are observations of the athlete, not the centre of the architecture.

---

## Domain-driven design

Every object should represent a real-world concept.

Examples:

- Athlete
- Workout
- History
- Goal
- Event
- Season
- TrainingPlan

The software architecture should reflect how coaches and athletes think about training.

---

## Separation of responsibilities

Each class should have a single responsibility.

Example:

History

stores workouts.

GoalBook

stores goals.

EventBook

stores events.

AthleteAnalytics

provides analysis.

Each object owns its own domain.

---

## Composition over inheritance

Objects should be composed from reusable components.

Example:

Workout

├── WorkoutInfo
├── Environment
├── AthleteFeedback
└── SensorCollection

instead of containing dozens of unrelated attributes.

---

# Athlete Model

The Athlete is the root of the domain model.

```
Athlete

├── History
├── GoalBook
├── EventBook
├── AthleteAnalytics
├── Physiology
├── Preferences
└── Workspace
```

Everything is accessed through the athlete.

---

# Workout

Workout represents one training session.

```
Workout

├── WorkoutInfo
├── Environment
├── AthleteFeedback
└── SensorCollection
```

Each component has a single responsibility.

---

# History

History represents everything the athlete has already done.

History is the source of truth for past performance.

It owns workouts but performs no analysis.

---

# Goals

Goals represent future objectives.

Examples:

- race
- FTP target
- weight target
- weekly consistency
- marathon preparation

Goals describe intent.

---

# Events

Events represent real sporting events.

An Event describes the competition.

An EventEntry describes the athlete's participation.

---

# Training Plans

Training plans are strategies.

Goals remain stable.

Plans adapt continuously according to:

- fatigue
- illness
- missed sessions
- fitness evolution
- available time

---

# Sensors

SensorCollection stores recorded sensor data.

Examples:

- Heart Rate
- GPS
- Power
- Cadence
- Temperature
- Altitude
- Running Dynamics

The architecture must remain open to future sensor types.

---

# Analysis Layer

Analysis is completely separated from the domain model.

```
analysis/

├── analytics.py
├── time.py
├── volume.py
├── consistency.py
├── goal_analysis.py
├── event_analysis.py
├── physiology.py
├── training_load.py
├── fatigue.py
└── performance.py
```

The domain model stores information.

The analysis layer interprets it.

---

# AthleteAnalytics

AthleteAnalytics is the public API for analysis.

It acts as a facade.

It delegates computations to specialised analysis modules.

```
Athlete

↓

AthleteAnalytics

↓

time.py

volume.py

consistency.py

goal_analysis.py

event_analysis.py

...
```

The facade itself should contain little or no analytical logic.

---

# Domain Metrics

PerformanceLab distinguishes between domain metrics and physiological metrics.

Domain metrics belong to a specific sport.

Examples:

Running

- distance
- elevation
- pace

Cycling

- distance
- elevation
- power

Swimming

- distance
- pace
- SWOLF

These metrics are **never aggregated across sports**.

A total distance combining running and cycling has no physiological meaning.

---

# Physiological Metrics

Different sports become comparable only through physiological metrics.

Examples:

- Training Load
- TRIMP
- sRPE Load
- CTL
- ATL
- TSB
- Recovery
- Fatigue

These metrics represent the athlete rather than the activity.

They may legitimately aggregate different sports because they quantify physiological stress instead of physical distance.

---

# Development Philosophy

PerformanceLab prioritises:

- clarity
- scientific correctness
- extensibility
- maintainability
- clean APIs

Architecture is more important than rapidly adding features.

The project should grow as a coherent framework rather than as a collection of utilities.

---

# Long-term Vision

PerformanceLab aims to become a complete digital representation of an endurance athlete.

Instead of simply analysing workouts, it should understand:

- who the athlete is
- what the athlete has done
- what the athlete wants to achieve
- how the athlete is adapting
- what should be done next

The project should progressively evolve from a data analysis toolkit into an intelligent coaching platform.

---

# Current Domain Model

```
Athlete
│
├── History
│     └── Workout
│
├── GoalBook
│     └── Goal
│
├── EventBook
│     └── EventEntry
│             └── Event
│
└── AthleteAnalytics
      │
      ├── Time Analysis
      ├── Volume Analysis
      ├── Consistency Analysis
      ├── Goal Analysis
      └── Event Analysis
```

The Athlete remains the root of the entire model.

The domain layer stores data.

The analysis layer interprets data.

The public API exposes analysis through AthleteAnalytics.