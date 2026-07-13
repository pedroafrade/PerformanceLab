# PerformanceLab Architecture

## Vision

PerformanceLab is not intended to be just another training analysis library.

Its goal is to provide a complete digital representation of an endurance athlete, combining historical data, physiological information, objectives and intelligent analysis into a single coherent framework.

The project is designed around the athlete rather than around activity files.

---

# Core Principles

## Domain-driven design

Every object should represent a real-world concept.

Examples:

- Athlete
- Workout
- History
- Goal
- Season
- Race
- TrainingPlan

The software architecture should reflect how coaches and athletes think about training.

---

## Separation of responsibilities

Each class should have a single responsibility.

For example:

Workout
    represents one training session.

History
    represents the athlete's training history.

Goal
    represents a future objective.

Season
    groups multiple goals into a competitive season.

TrainingPlan
    represents the strategy to reach a goal.

No class should try to perform the role of another.

---

## Composition over inheritance

Objects should be composed from smaller reusable components whenever possible.

Example:

Workout

├── WorkoutInfo
├── Environment
├── AthleteFeedback
└── SensorCollection

instead of storing dozens of unrelated attributes directly inside Workout.

---

# Athlete Model

The Athlete is the central object of the library.

Everything else revolves around it.

Athlete

├── History
├── Goals
├── Seasons
├── Physiology
├── Preferences
└── Workspace

---

# History

History represents everything the athlete has already done.

It is more than a list of workouts.

It provides:

- filtering
- statistics
- summaries
- analysis
- data export

History is the source of truth for past performance.

---

# Workout

Workout represents a single training session.

Workout

├── WorkoutInfo
├── Environment
├── AthleteFeedback
└── SensorCollection

Each component has a single responsibility.

---

# Goals

Goals represent future objectives.

Examples:

- Race
- Personal record
- FTP target
- Weight target
- Weekly consistency
- Marathon preparation

A Goal is independent from the workouts already performed.

---

# Seasons

A Season groups multiple Goals.

Example:

2026 Season

├── Trail Race
├── Ultra Marathon
└── Autumn Marathon

This reflects how athletes usually organize their year.

---

# Training Plans

A TrainingPlan is not the goal.

A TrainingPlan is the strategy used to reach a Goal.

Goals remain stable.

Plans may change continuously according to:

- fatigue
- injuries
- missed sessions
- fitness evolution
- available time

The plan should be adaptive rather than static.

---

# Sensors

SensorCollection stores every recorded sensor.

Examples:

- Heart Rate
- GPS
- Power
- Cadence
- Temperature
- Altitude
- Running Dynamics
- Future sensors

The architecture must remain open for new sensor types without modifying the Workout model.

---

# Future Analysis Modules

The long-term objective is to provide intelligent analysis rather than simple data visualization.

Examples:

- Training Load
- Acute / Chronic Load
- Fitness
- Fatigue
- Readiness
- Performance Prediction
- Race Readiness
- Training Recommendations

---

# Development Philosophy

PerformanceLab should prioritize:

- clarity
- extensibility
- scientific correctness
- maintainability
- clean APIs

Internal architecture is more important than quickly adding features.

The project should grow as a coherent framework rather than as a collection of utilities.

---

# Long-term Vision

PerformanceLab aims to become a complete digital model of an endurance athlete.

Instead of simply analysing workouts, it should understand:

- who the athlete is
- what the athlete has done
- where the athlete wants to go
- what should be done next

The software should progressively evolve from a data analysis toolkit into an intelligent coaching platform.