import os
import os.path
import subprocess
import shlex
import datetime
import time

p = datetime.timedelta(seconds=5)
for f in os.listdir('./rawlogs'):
    if f.endswith('.log'):
        s = datetime.datetime.now()
        f = os.path.join('rawlogs', f)
        print(f)

        #curl -i -F 'file=@172.30.121.21.messages-20200605.processed.log' eg.bucknell.edu:5000/upload

        cmd = "-i -F 'file=@{}' eg.bucknell.edu:5000/upload".format(f)
        proc = subprocess.Popen(
            shlex.split('/usr/bin/curl ' + cmd))
        print("running curl ", cmd)
        print(proc.wait())


        w = p - (datetime.datetime.now() - s)

        while w.total_seconds() > 1:
            print("Wait {} sec".format(w.total_seconds()))
            time.sleep(1)
            w = p - (datetime.datetime.now() - s)
