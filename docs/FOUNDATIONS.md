# PerformanceLab Foundations

## Purpose

PerformanceLab is built to transform physiological data into useful knowledge for athletes.

The software exists to help athletes understand their training, monitor long-term progression and make better decisions.

The code serves the athlete.
The athlete never serves the code.

---

# Design Philosophy

PerformanceLab follows a strict separation of responsibilities.

Sensor
↓
TrainingSession
↓
Workout
↓
History
↓
Physiology
↓
Analysis
↓
Interpretation
↓
Recommendation

Each layer has one responsibility.

---

# The Three Engines

PerformanceLab is built around three independent engines.

## 1. Scientific Engine

Responsible for:

- physiology
- heart rate
- training load
- recovery
- thresholds
- efficiency
- metrics

Characteristics

- deterministic
- reproducible
- explainable
- independent from AI

Scientific calculations are the single source of truth.

---

## 2. Statistical Engine

Responsible for learning from the athlete.

Examples

- individual recovery patterns
- heat adaptation
- altitude adaptation
- fatigue trends
- long-term progression

Characteristics

- personalised
- continuously updated
- never replaces scientific principles

---

## 3. Conversational Engine

Responsible for communication.

Examples

- answering questions
- explaining sessions
- generating reports
- summarising trends

This engine never calculates physiological metrics.

It explains decisions made by the Scientific and Statistical engines.

---

# Transparency

Every recommendation must be explainable.

The software should always be able to answer:

"Why?"

---

# Independence

PerformanceLab must never depend on a specific AI provider.

ChatGPT, Claude, Gemini or any future model are interfaces.

The intelligence belongs to PerformanceLab.

---

# Athlete First

Every architectural decision should answer one question:

Does this help the athlete?

If the answer is no, it probably does not belong in PerformanceLab.