# mass_index.py
The unofficial way to mass index MANY files to Splunk!

### Use case
You have thousands, if not, millions of files that you want to index to Splunk. You try normal `monitor` and `batch` inputs, but it crashes Splunk or it's way too slow (like 1 file per second).

### How it works
This Python script uses multiprocessing to send the raw text from files via Splunk HEC. The script keep trying to send events to HEC until a maximum number of errors is reached. If that happens (ie Splunk is down or unresponsive) or `SIGINT` was detected (ie `ctrl-c`), then it'll save the remaining file list to a CSV and quit. The script will resume from the CSV on next run. Delete the CSV manually if you want the script to start over. See [`settings.py`](https://github.com/hobbes3/mass_index/blob/master/default_settings.py) for configuration settings.

### Requirements
1. Use Python 3 (tested on Python 3.7.0) and install [`tqdm`](https://pypi.org/project/tqdm/) and [`requests`](https://pypi.org/project/requests/).
2. Copy, edit, and rename `default_settings.py` to `settings.py`.
3. In Splunk, create your appropriate indexes and tune your instance appriopriately. See the [_Other considerations_](#other-considerations) section below.
4. In Splunk, create your `props.conf` and `transforms.conf` rules to index the files appropriately if necessary. Note that you can't use `INDEXED_EXTRACTIONS` with HEC.
5. Run `./mass_index.py`. The output should look like

```
[splunk@my_machine mass_index]$ ./mass_index.py
Log file at /mnt/data/mass_index.log.
Reading files and sending via HEC...
Press ctrl-c to cancel and save remaining file list.
 97%|█████████████████████████████████████████████████████▏ | 3027986/3134390 [9:57:24<17:50, 99.37it/s]
```

### How to read the `tqdm` progress bar
Using the example right above:

* `97%`: Percent completion rate.
* `3027986/3134390`: 3027986 files sent out of 3134390 files.
* `9:57:24`: Elapsed time (in this case, 9 hours and 57 minutes).
* `17:50`: Estimated time left (in this case, about 17 minutes left).
* `99.37it/s`: About 99 files copied per second.

### Other considerations
1. `indexes.conf`: You probably want to use `maxDataSize=auto_high_volume` if you're ingesting over 10 GB+ of data. Otherwise Splunk might complain about too many rolling buckets.
2. `indexes.conf`: You might also want to raise `maxTotalDataSizeMB` (default 500 GB). Otherwise Splunk will delete any old buckets once the total index size reaches over 500 GB.
3. You should probably run `tmux` or `screen` to keep your session alive and reattach after exiting, so you don't interrupt this script while it's running for hours.
4. If you're not seeing the same number of files in Splunk after the script finishes, then check for files with 0 size and also double check your Splunk rules (`props.conf` and `tranforms.conf`). If your Splunk-fu and Vim-fu are good, then you can do something like `ls -lah > file_list_on_disk.txt` on the system, Vim edit the text file to a CSV, then in Splunk find the missing files by running something like:

```
| tstats count where index=foo sourcetype=bar by source
| eval source=replace(source, "hec::", "")
| eval src="splunk"
| inputlookup append=t file_list_on_disk.csv
| eval src=coalesce(src, "disk")
| stats count values(src) as src first(size) as size by source
| where count=1
```
5. `settings.py`: You can increase or decrease the speed of the script by adjust `THREADS` and `SLEEP` depending on how many `ERROR` lines you see in `mass_index.py`. You can also increase `ERROR_LIMIT_PCT` if you want to the script to keep trying even if Splunk complains or timeouts.

### Performance references
Indexing tested on EC2 `c4.8xlarge` (36 vCPU, 30 GB memory):

* [GDELT dataset](https://blog.gdeltproject.org/gdelt-2-0-our-global-world-in-realtime/): Over 500k files (total around 400 GB), took about X.X hours (about 60 files/second). See [my script](https://github.com/hobbes3/gdelt/blob/master/bin/get_data.py) in my GDELT app on how I get the latest and historical GDELT data.
* [IRS 990 dataset](https://docs.opendata.aws/irs-990/readme.html): Over 2.6 million files (total around 160 GB), took about 7.3 hours (about XX files/second).

### Thanks
* Thanks to **Jackson Sie** from Splunk Professional Services for coming up with the HEC method to index many files.
* Thanks to **Ali Okur** from Splunk Professional Services for helping me with other, previous methods and testing each of these methods.
* Thanks to **Corey Marshall** for insisting on indexing the huge GDELT and IRS 990 datasets, which Splunk couldn't do on its own, and which eventually lead to this solution :-).
