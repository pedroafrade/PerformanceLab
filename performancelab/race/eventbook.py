"""
PerformanceLab

EventBook

Container for an athlete's event entries.
"""

from dataclasses import dataclass, field

from .entry import EventEntry


@dataclass
class EventBook:

    entries: list[EventEntry] = field(default_factory=list)

    # ======================================================

    def add(self, entry: EventEntry):

        self.entries.append(entry)

        self._sort()

    # ======================================================

    def remove(self, entry: EventEntry):

        if entry in self.entries:

            self.entries.remove(entry)

    # ======================================================

    def clear(self):

        self.entries.clear()

    # ======================================================

    def _sort(self):

        self.entries.sort(

            key=lambda entry: (

                entry.event.date is None,

                entry.event.date,

            )

        )

    # ======================================================

    @property
    def upcoming(self):

        return [

            entry

            for entry in self.entries

            if entry.pending and entry.event.is_future

        ]

    # ======================================================

    @property
    def completed(self):

        return [

            entry

            for entry in self.entries

            if entry.completed

        ]

    # ======================================================

    @property
    def next(self):

        if not self.upcoming:

            return None

        return self.upcoming[0]

    # ======================================================

    def __len__(self):

        return len(self.entries)

    # ======================================================

    def __iter__(self):

        return iter(self.entries)

    # ======================================================

    def __getitem__(self, index):

        return self.entries[index]

    # ======================================================

    def __contains__(self, entry):

        return entry in self.entries

    # ======================================================

    def __repr__(self):

        return (

            f"EventBook("

            f"{len(self.entries)} events)"

        )