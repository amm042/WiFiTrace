#!/usr/bin/env python3
import os
import os.path
import subprocess
import shlex
import datetime
import time
import json
progdir='/home/amm042/src/WiFiTrace/Preprocessor/src/'
os.chdir(progdir)
datadir='../../WiFiTrace/data/'

statfile='../../heatmap-stat.json'
logfile='../../heatmapdir.log'

if os.path.exists(statfile):
    with open(statfile, 'r') as f:
        statinfo = json.load(f)
else:
    statinfo = {}
skipped= 0
print("="*40)
print("heatmapdir check begin at ", datetime.datetime.now())
for f in os.listdir(datadir):
    if f.endswith('.csv'):
        f = os.path.join(datadir, f)
        #print('Checking {} '.format(f), end="")

        # use modification time
        st = os.stat(f).st_mtime

        process = True
        if f in statinfo:
            # check access time
            if statinfo[f] == st:
                #print('no change since last run.')
                process = False
                skipped += 1

        if process:
            print('Processing {} '.format(f), end="")
            # new file
            cmd = "python3 heatmapper.py {}".format(f)

            with open(logfile, 'a') as runlog:
                proc = subprocess.Popen(
                    shlex.split('/usr/bin/env ' + cmd),
                    cwd = '.',
                    stdout = runlog,
                    stderr = runlog)
                #print("running ", cmd, end="")
                returncode = proc.wait()

            # check proc return code?
            if returncode == 0:
                print("success.")
                # update stat file
                statinfo[f] = st
                with open(statfile, 'w') as f:
                    json.dump(statinfo, f)
            else:
                print("error! ({}).".format(returncode))
print("heatmapdir check finished at ", datetime.datetime.now(), skipped, "files unchanged.")
print("="*40)
