# PerformanceLab Domain Model

## Philosophy

PerformanceLab models the real world of endurance training.

Every class represents a real concept that exists in the athlete's training process.

The software is built around the athlete, not around files or algorithms.

---

# Core Entities

Athlete

↓

History

↓

Workout

↓

Session

↓

Sensor

---

# Athlete

Represents one person.

Owns:

- personal information
- physiology
- history
- goals

---

# History

Chronological collection of workouts.

Responsible for:

- statistics
- long-term trends
- progression
- training load

---

# Workout

Represents one complete training session.

Contains:

- metadata
- equipment
- environment
- sessions
- sensors
- subjective feedback
- analysis
- recommendations

Workout is the central object of the system.

---

# Session

A logical block inside one workout.

Examples:

- Warm-up
- Interval block
- Recovery
- Cool-down

A workout may contain multiple sessions.

---

# Sensor

Represents one recorded data stream.

Examples:

- Heart Rate
- GPS
- Power
- Cadence
- Speed
- Temperature

Each workout may contain multiple sensors.

---

# Workspace

User working environment.

Responsible for:

- importing data
- creating athletes
- managing projects
- running analyses

---

# Future Scientific Engines

Physiology Engine

↓

Interpretation Engine

↓

Recommendation Engine

These engines never replace the domain model.

They operate on it.

---

# Golden Rule

The athlete is the centre of the software.

Everything else exists to help understand the athlete.