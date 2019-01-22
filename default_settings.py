# Copy and rename this file to settings.py to be in effect.

URL = "https://localhost:8088"
HEC_TOKEN = "b71b8557-2286-4222-97d2-2940c003a763"

THREADS = 24

SLEEP = 0.1
TIMEOUT = 3
# How many seconds to sleep before trying to send the data via HEC again.
# If the last number is reached and the check still fails,
# then the whole script will exit and the current file list will be saved as
# a csv at SAVED_FILE_LIST_PATH below.
# This is to prevent the script from hanging while Splunk is down.
TRY_SLEEP = [0.5, 1, 2, 3, 5, 10, 15, 30]
ERROR_LIMIT = 100

SAVED_FILE_LIST_PATH = "/mnt/data/samples/mass_index_saved_file_list.csv"

# Prefix to add to Splunk's source field.
# The source is set to this prefix and the filename.
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
