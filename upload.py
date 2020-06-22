import os
import subprocess
import shlex
for f in os.listdir('.'):
    if f.endswith('.log'):
        print(f)

        #curl -i -F 'file=@172.30.121.21.messages-20200605.processed.log' eg.bucknell.edu:5000/upload

        cmd = "-i -F 'file=@{}' eg.bucknell.edu:5000/upload".format(f)
        proc = subprocess.Popen(
            shlex.split('/usr/bin/curl ' + cmd))
        print("running curl ", cmd)
        print(proc.wait())
