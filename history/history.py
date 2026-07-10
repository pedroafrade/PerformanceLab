 """
PerformanceLab

History
-------

Histórico de sessões de um atleta.
"""

from dataclasses import dataclass, field
from datetime import timedelta

import pandas as pd


@dataclass
class History:

    athlete: object

    sessions: list = field(default_factory=list)

    # ======================================================

    def add(self, session):

        self.sessions.append(session)

        self.sessions.sort(key=lambda s: s.start)

        return self

    # ======================================================

    def remove(self, index):

        self.sessions.pop(index)

    # ======================================================

    def clear(self):

        self.sessions.clear()

    # ======================================================

    @property
    def dataframe(self):

        rows = []

        for session in self.sessions:

            rows.append(

                {

                    "date": session.start,

                    "sport": session.sport,

                    "duration": session.duration,

                    "sensors": len(session),

                }

            )

        return pd.DataFrame(rows)

    # ======================================================

    @property
    def first_session(self):

        if not self.sessions:

            return None

        return self.sessions[0]

    # ======================================================

    @property
    def last_session(self):

        if not self.sessions:

            return None

        return self.sessions[-1]

    # ======================================================

    @property
    def total_duration(self):

        total = timedelta()

        for session in self.sessions:

            total += session.duration

        return total

    # ======================================================

    @property
    def sports(self):

        return sorted(

            {

                s.sport

                for s in self.sessions

            }

        )

    # ======================================================

    def summary(self):

        print()

        print("=" * 45)

        print("ATHLETE HISTORY")

        print("=" * 45)

        print(f"Athlete : {self.athlete.name}")

        print(f"Sessions: {len(self.sessions)}")

        print(f"Sports  : {', '.join(self.sports)}")

        print(f"Duration: {self.total_duration}")

        if self.first_session:

            print()

            print(f"First   : {self.first_session.start}")

            print(f"Last    : {self.last_session.start}")

        print("=" * 45)

    # ======================================================

    def __len__(self):

        return len(self.sessions)

    # ======================================================

    def __getitem__(self, item):

        return self.sessions[item]

    # ======================================================

    def __iter__(self):

        return iter(self.sessions)

    # ======================================================

    def __repr__(self):

        return (

            f"History("

            f"{len(self.sessions)} sessions)"

        )