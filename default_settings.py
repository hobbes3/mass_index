# Copy and rename this file to settings.py to be in effect.

URL = "https://localhost:8088"
HEC_TOKEN = "b71b8557-2286-4222-97d2-2940c003a763"

THREADS = 24

# How many seconds a thread sleeps after a successful HEC send.
SLEEP = 0.1
# How many seconds a thread waits for a response
# before declaring a timeout (and adding toward the ERROR_LIMIT).
TIMEOUT = 3
# How many seconds a thread sleeps before trying to send the file via HEC again.
# The thread will sleep for each number in order until the last number is reached.
# Then it will repeat on the last number forever until ERROR_LIMIT is reached.
# The thread resets back to the first sleep number after a successful send.
TRY_SLEEP = [0.5, 1, 2, 3, 5, 10, 15, 30]
# How many total errors (timeouts, HTTP error codes, etc.) allowed among all threads
# before the entire script exits (and saves the remaining file list).
# This is to prevent the script from hanging while Splunk is down.
ERROR_LIMIT = 100

SAVED_FILE_LIST_PATH = "/mnt/data/samples/mass_index_saved_file_list.csv"

# The script overrides Splunk's default source for HEC with this prefix and the filename.
# Change this to an empty string "" if you don't want the prefix.
SOURCE_PREFIX = "hec::"

LOG_PATH = "/mnt/data/samples/mass_index.log"
# Size of each log file.
# 1 MB = 1 * 1024 * 1024
LOG_ROTATION_BYTES = 25 * 1024 * 1024
# Maximum number of log files.
LOG_ROTATION_LIMIT = 100

DATA = [
    {
        "path": "/path/to/some/logs/*.log",
        "index": "foo",
        "sourcetype": "some_sourcetype",
    },
    {
        "path": "/path/to/some/other/logs/*.log",
        "index": "bar",
        "sourcetype": "another_sourcetype",
    },
]
