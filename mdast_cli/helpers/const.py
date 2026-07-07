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

ANDROID_EXTENSIONS = ['.apk', '.apks', '.zip', '.aab']

# Default architecture names for auto-selection
DEFAULT_ANDROID_ARCHITECTURE = 'Android 11'
DEFAULT_IOS_ARCHITECTURE = 'iOS 14'

# Timeout constants (in seconds)
TRY = 360
LONG_TRY = 20160
END_SCAN_TIMEOUT = 30
SLEEP_TIMEOUT = 10

# HTTP timeout constants
HTTP_REQUEST_TIMEOUT = 30
HTTP_DOWNLOAD_TIMEOUT = 300


# --- Microservices installation (Clark facade, scanyon-native contract) ---

class ScanStage:
    CREATED = 'CREATED'
    START = 'START'
    WORKING = 'WORKING'
    STOP = 'STOP'
    SUCCESS = 'SUCCESS'
    FAIL = 'FAIL'


class ScanStageStatus:
    INITIAL = 'INITIAL'
    PROCESSING = 'PROCESSING'
    WAITING = 'WAITING'
    COMPLETE = 'COMPLETE'
    PARTIAL_COMPLETE = 'PARTIAL_COMPLETE'
    FAIL = 'FAIL'


# Terminal (stage, status) pairs, confirmed with scanyon FSM (STG-4475).
# STOP is transitional: a stopped scan finishes as SUCCESS/COMPLETE or SUCCESS/PARTIAL_COMPLETE.
TERMINAL_SCAN_PAIRS = {
    (ScanStage.SUCCESS, ScanStageStatus.COMPLETE),
    (ScanStage.SUCCESS, ScanStageStatus.PARTIAL_COMPLETE),
    (ScanStage.FAIL, ScanStageStatus.FAIL),
}
PRE_START_STAGES = {ScanStage.CREATED, ScanStage.START}
ACTIVE_STAGES = {ScanStage.WORKING, ScanStage.STOP}

# Eucalyptus engine contract: platform in `type`, liveness in `status` (not `state`)
ENGINE_ACTIVE_STATUS = 'STARTED'
OS_ANDROID = 'ANDROID'
OS_IOS = 'IOS'

# Installation mode selection (no new CLI flags by contract, env vars only)
MODE_ENV_VAR = 'MDAST_CLI_MODE'
UPLOAD_TIMEOUT_ENV_VAR = 'MDAST_UPLOAD_TIMEOUT'
TLS_VERIFY_ENV_VAR = 'MDAST_TLS_VERIFY'
MODE_AUTO = 'auto'
MODE_MONOLITH = 'monolith'
MODE_MICROSERVICES = 'microservices'

# Clark upload contract (STG-4451): server-side upload_timeout query bounds
UPLOAD_TIMEOUT_MIN = 1
UPLOAD_TIMEOUT_MAX = 300
