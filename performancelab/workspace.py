"""
PerformanceLab v1.0

workspace.py

Cria um ambiente completo de trabalho para testes.
"""

from dataclasses import dataclass

from .readers import (
    read_apple_gpx,
    read_polar_csv
)

from .athlete import Athlete
from .session import Session
from .sync import Synchronizer


# ==========================================================
# Workspace
# ==========================================================

@dataclass
class Workspace:

    athlete: Athlete

    session: Session

    apple: object

    polar: object

    sync: Synchronizer

    comparison: object


# ==========================================================
# Demo loader
# ==========================================================

def load_demo(

    apple_file="APPLEWATCH.gpx",

    polar_file="Pedro_Frade_2026-07-08_21-28-14.CSV"

):

    # ------------------------------------------------------

    athlete = Athlete(

        name="Pedro Frade",

        birth_year=1989,

        gender="M",

        weight=72,

        height=1.78,

        resting_hr=48,

        max_hr=190,

        threshold_hr=172,

        sports=["Trail Running"]

    )

    # ------------------------------------------------------

    apple = read_apple_gpx(apple_file)

    polar = read_polar_csv(polar_file)

    # ------------------------------------------------------

    session = Session(

        athlete=athlete,

        sport="Trail Running"

    )

    session.add_sensor(apple)

    session.add_sensor(polar)

    # ------------------------------------------------------

    sync = Synchronizer(

        reference=polar,

        target=apple

    )

    comparison = sync.compare()

    # ------------------------------------------------------

    return Workspace(

        athlete=athlete,

        session=session,

        apple=apple,

        polar=polar,

        sync=sync,

        comparison=comparison

    )
