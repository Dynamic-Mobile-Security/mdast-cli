class DastState:
    CREATED = 0
    STARTING = 1
    STARTED = 2
    ANALYZING = 3
    SUCCESS = 4
    FAILED = 5

DastStateDict = {
    0: "CREATED",
    1: "STARTING",
    2: "STARTED",
    3: "ANALYZING",
    4: "SUCCESS",
    5: "FAILED"
}

TRY_COUNT = 120
SLEEP_TIMEOUT = 30
