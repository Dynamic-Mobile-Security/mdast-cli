class DastState:
    CREATED = 0
    STARTING = 1
    STARTED = 2
    ANALYZING = 3
    SUCCESS = 4
    FAILED = 5
    STOPPING = 6
    RECALCULATING = 7
    INTERRUPTING = 8
    INITIALIZING = 9
    CANCELLED = 10
    CANCELLING = 11


DastStateDict = {
    0: "CREATED",
    1: "STARTING",
    2: "STARTED",
    3: "ANALYZING",
    4: "SUCCESS",
    5: "FAILED",
    6: "STOPPING",
    7: "RECALCULATING",
    8: "INTERRUPTING",
    9: "INITIALIZING",
    10: "CANCELLED",
    11: "CANCELLING"
}


class Architectures:
    ANDROID_8 = 1
    ANDROID_11 = 2
    iOS_14 = 3


TRY_COUNT = 360
SLEEP_TIMEOUT = 10
