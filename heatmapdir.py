import os
import os.path
import subprocess
import shlex
import datetime
import time
progdir='./Preprocessor/src/'
os.chdir(progdir)
datadir='../../WiFiTrace/data/'
for f in os.listdir(datadir):
    if f.endswith('.csv'):
        f = os.path.join(datadir, f)
        print(f)

        cmd = "python3 heatmapper.py {}".format(f)
        proc = subprocess.Popen(
            shlex.split('/usr/bin/env ' + cmd),
            cwd = '.')
        print("running ", cmd)
        print(proc.wait())
