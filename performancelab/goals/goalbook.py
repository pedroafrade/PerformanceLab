"""
PerformanceLab

GoalBook

Container for an athlete's goals.
"""

from dataclasses import dataclass, field

from .goal import Goal


@dataclass
class GoalBook:

    goals: list[Goal] = field(default_factory=list)

    # ======================================================

    def add(self, goal: Goal):

        self.goals.append(goal)

    # ======================================================

    def remove(self, goal: Goal):

        if goal in self.goals:

            self.goals.remove(goal)

    # ======================================================

    def clear(self):

        self.goals.clear()

    # ======================================================

    @property
    def active(self):

        return [

            goal

            for goal in self.goals

            if goal.is_future

        ]

    # ======================================================

    def __len__(self):

        return len(self.goals)

    # ======================================================

    def __iter__(self):

        return iter(self.goals)

    # ======================================================

    def __getitem__(self, index):

        return self.goals[index]

    # ======================================================

    def __repr__(self):

        return (

            f"GoalBook("

            f"{len(self.goals)} goals)"

        )