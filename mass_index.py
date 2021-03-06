#!/usr/bin/env python
# hobbes3

import os
import time
import sys
import glob
import csv
import io
import logging
import logging.handlers
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from tqdm import tqdm
from pathlib import Path
from shutil import copy2
from multiprocessing import RawValue, Lock
from multiprocessing.dummy import Pool
from threading import Lock

from settings import *

# https://stackoverflow.com/a/47562583/1150923
class Counter(object):
    def __init__(self, initval=0):
        self.val = RawValue('i', initval)
        self.lock = Lock()

    def increment(self):
        with self.lock:
            self.val.value += 1

    @property
    def value(self):
        return self.val.value

def save_and_exit():
    with lock:
        logger.info("Saving remaining file list (length={}) as {}...".format(len(data), SAVED_FILE_LIST_PATH))

        with open(SAVED_FILE_LIST_PATH, "w") as csv_file:
            fields = ["file_path", "index", "sourcetype"]
            writer = csv.DictWriter(csv_file, fieldnames=fields)
            writer.writeheader()
            writer.writerows(data)
        csv_file.close()

        logger.info("{} saved.".format(len(data), SAVED_FILE_LIST_PATH))
        print("File list saved.")
        logger.info("INCOMPLETE. Total elapsed seconds: {}.".format(time.time() - start_time))
        os._exit(1)

def send_hec_raw(datum):
    file_path = datum["file_path"]
    index = datum["index"]
    sourcetype = datum["sourcetype"]

    url = URL + "/services/collector/raw"
    headers = {
        "Authorization": "Splunk " + HEC_TOKEN
    }

    params = {
        "index": index,
        "sourcetype": sourcetype,
        "source": SOURCE_PREFIX + (file_path if SOURCE_FULL_PATH else os.path.split(file_path)[1]),
    }

    f = io.open(file_path, mode="r", encoding="utf-8")
    raw = f.read()

    count_try = 0

    if not raw:
        logger.warning("Try #{}, total error #{}: {} - 0 size file. Skipping. Sleeping for {} seconds.".format(count_try+1, count_error.value, file_path, SLEEP))
        return
    else:
        while True:
            if count_error.value > count_total_errors:
                logger.error("Over {} total errors. Script exiting!".format(count_total_errors))
                save_and_exit()

            try:
                r = requests.post(url, headers=headers, params=params, data=raw.encode("utf-8"), verify=False, timeout=TIMEOUT)
                r.raise_for_status()
            except (requests.exceptions.HTTPError, requests.exceptions.Timeout, requests.exceptions.TooManyRedirects, requests.exceptions.RequestException) as e:
                count_error.increment()
                sleep = TRY_SLEEP[min(count_try, len(TRY_SLEEP)-1)]
                logger.error("Try #{}, total error #{}: {} - {}. Sleeping for {} second(s).".format(count_try+1, count_error.value, file_path, str(e), sleep))
                time.sleep(sleep)
                count_try += 1
                pass
            except:
                logger.fatal("{}. Script exiting!".format(sys.exc_info()[0]))
                save_and_exit()
            else:
                logger.info("Try #{}, total error #{}: {} - Successfully sent. Sleeping for {} seconds(s).".format(count_try+1, count_error.value, file_path, SLEEP))
                data.remove(datum)
                break

    time.sleep(SLEEP)

if __name__ == "__main__":
    start_time = time.time()

    setting_file = Path(os.path.dirname(os.path.realpath(__file__)) + "/settings.py")

    if not os.path.exists(setting_file):
        sys.exit("The config file, settings.py, doesn't exist! Please copy, edit, and rename default_settings.py to settings.py.")

    logger = logging.getLogger("logger")
    logger.setLevel(logging.DEBUG)
    handler = logging.handlers.RotatingFileHandler(LOG_PATH, maxBytes=LOG_ROTATION_BYTES, backupCount=LOG_ROTATION_LIMIT)
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)-7s] (%(threadName)-10s) %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
    logger.addHandler(handler)

    print("Log file at {}.".format(LOG_PATH))

    logger.info("===START OF SCRIPT===")
    logger.debug(
        "From settings.py: " +
        "URL={}, ".format(URL) +
        "THREADS={}, ".format(THREADS) +
        "SLEEP={}, ".format(SLEEP) +
        "TIMEOUT={}, ".format(TIMEOUT) +
        "TRY_SLEEP={}, ".format(TRY_SLEEP) +
        "ERROR_LIMIT_PCT={}, ".format(ERROR_LIMIT_PCT) +
        "SAVED_FILE_LIST_PATH={}, ".format(SAVED_FILE_LIST_PATH) +
        "SOURCE_PREFIX={}, ".format(SOURCE_PREFIX) +
        "SOURCE_FULL_PATH={}, ".format(SOURCE_FULL_PATH) +
        "LOG_PATH={}, ".format(LOG_PATH) +
        "LOG_ROTATION_BYTES={}, ".format(LOG_ROTATION_BYTES) +
        "LOG_ROTATION_LIMIT={}, ".format(LOG_ROTATION_LIMIT) +
        "DATA={}.".format(DATA)
    )

    data = []

    count_error = Counter(0)

    if os.path.exists(SAVED_FILE_LIST_PATH):
        logger.info("Saved file list found at {}. Loading file list...".format(SAVED_FILE_LIST_PATH))
        print("Saved file list found at {}. Loading file list...".format(SAVED_FILE_LIST_PATH))

        with open(SAVED_FILE_LIST_PATH) as csv_file:
            reader = csv.DictReader(csv_file)
            for r in reader:
                data.append(r)

        logger.info("File list loaded.")
        print("File list loaded.")
    else:
        logger.info("Saved file list not found at {}. Creating file list...".format(SAVED_FILE_LIST_PATH))
        print("Saved file list not found at {}. Creating file list...".format(SAVED_FILE_LIST_PATH))

        for i, d in enumerate(DATA):
            path = d["path"]
            index = d["index"]
            sourcetype = d["sourcetype"]

            file_paths = glob.glob(path)
            logger.debug("DATA #{}: path={}, index={}, sourcetype={}, len(file_paths)={}.".format(i, path, index, sourcetype, len(file_paths)))

            data.extend([
                {
                    "file_path": file_path,
                    "index": index,
                    "sourcetype": sourcetype,
                }
                for file_path in file_paths
            ])

        logger.info("File list created.")
        print("File list created.")

    count_total_files = len(data)
    count_total_errors = count_total_files * THREADS * ERROR_LIMIT_PCT
    logger.debug("Total errors allowed: {}={} * {} * {} (total_errors = total_files * THREADS * ERROR_LIMIT_PCT).".format(count_total_errors, count_total_files, THREADS, ERROR_LIMIT_PCT))

    logger.info("Sending {} files via HEC...".format(count_total_files))
    print("Sending {} files via HEC...".format(count_total_files))
    print("Press ctrl-c to cancel and save remaining file list.")

    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    pool = Pool(THREADS)
    lock = Lock()

    try:
        for _ in tqdm(pool.imap_unordered(send_hec_raw, data), total=count_total_files):
            pass

        pool.close()
        pool.join()
    except KeyboardInterrupt:
        print("\nCaught KeyboardInterrupt! Terminating workers and saving remaining file list. Please wait...")
        logger.warning("Caught KeyboardInterrupt!") 
        pool.terminate()
        pool.join()
        save_and_exit()

    if os.path.exists(SAVED_FILE_LIST_PATH):
        os.remove(SAVED_FILE_LIST_PATH)
        logger.info("All files sent. {} deleted.".format(SAVED_FILE_LIST_PATH))

    logger.info("DONE. Total elapsed seconds: {}.".format(time.time() - start_time))
    print("Done!")
