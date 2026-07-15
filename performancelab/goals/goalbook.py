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

        self._sort()

    # ======================================================

    def remove(self, goal: Goal):

        if goal in self.goals:

            self.goals.remove(goal)

    # ======================================================

    def clear(self):

        self.goals.clear()

    # ======================================================

    def _sort(self):

        self.goals.sort(

            key=lambda goal: (

                goal.date is None,

                goal.date,

            )

        )

    # ======================================================

    @property
    def active(self):

        return [

            goal

            for goal in self.goals

            if goal.is_active

        ]

    # ======================================================

    @property
    def completed(self):

        return [

            goal

            for goal in self.goals

            if goal.completed

        ]

    # ======================================================

    @property
    def next(self):

        if not self.active:

            return None

        return self.active[0]

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

    def __contains__(self, goal):

        return goal in self.goals

    # ======================================================

    def __repr__(self):

        return (

            f"GoalBook("

            f"{len(self.goals)} goals)"

        )