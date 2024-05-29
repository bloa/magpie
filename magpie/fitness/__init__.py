from .bloat import BloatCharsFitness, BloatLinesFitness, BloatWordsFitness
from .gnu_time import (
    GnuMajorPagefaultsFitness,
    GnuMemoryFitness,
    GnuMinorPagefaultsFitness,
    GnuPagefaultsFitness,
    GnuSwapsFitness,
    GnuSystemTimeFitness,
    GnuTimeFitness,
    GnuUserTimeFitness,
)
from .output import OutputFitness
from .repair import RepairFitness
from .time import (
    PerfInstructionsFitness,
    PerfTimeFitness,
    PosixTimeFitness,
    TimeFitness,
)
