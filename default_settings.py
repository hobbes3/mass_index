# Copy and rename this file to settings.py to be in effect.

URL = "https://localhost:8088"
HEC_TOKEN = "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"

THREADS = 8

# How many seconds a thread sleeps after a successful HEC send.
SLEEP = 0.1
# How many seconds a thread waits for a response
# before declaring a timeout (and adding toward the error count for ERROR_LIMIT_PCT).
TIMEOUT = 5
# How many seconds a thread sleeps before trying to send the file via HEC again.
# The thread will sleep for each number in order until the last number is reached.
# Then it will repeat on the last number forever until too many errors are reached (see ERROR_LIMIT_PCT).
# The thread resets back to the first sleep number after a successful send.
TRY_SLEEP = [1, 5, 10, 30, 60]
# If the total number of errors (timeouts, HTTP error codes, etc.) among all threads reaches a certain limit,
# then the entire script exits (and saves the remaining file list).
# The formula is
#     total_errors = total_files * THREADS * ERROR_LIMIT_PCT
# This is to prevent the script from hanging forever if Splunk is down or unresponsive.
ERROR_LIMIT_PCT = 0.01

SAVED_FILE_LIST_PATH = "/path/to/mass_index_saved_file_list.csv"

# The script overrides Splunk's default source for HEC with this prefix and the filename.
# Change this to an empty string "" if you don't want the prefix.
SOURCE_PREFIX = "hec::"
# If set to False, then it will only include the filename (and the SOURCE_PREFIX).
SOURCE_FULL_PATH = True

LOG_PATH = "/path/to/mass_index.log"
# Size of each log file.
# 1 MB = 1 * 1024 * 1024
LOG_ROTATION_BYTES = 25 * 1024 * 1024
# Maximum number of log files.
LOG_ROTATION_LIMIT = 100

# The list of file locations to mass index.
# If the file SAVED_FILE_LIST_PATH exists,
# then the script will ignore this setting and use that file to resume mass index instead.
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
