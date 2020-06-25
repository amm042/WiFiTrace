"""

run the development server with "$ flask run"
"""

from flask import Flask, jsonify, request, send_from_directory, abort
from werkzeug.utils import secure_filename
import subprocess
import os.path
import shlex

import threading
import uuid
import time
from datetime import datetime
import dateutil.parser

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/tmp/covid/upload'

# the bucknell preprocessor
app.config['PREPROCESSOR_PATH'] = '/home/amm042/src/WiFiTrace/Preprocessor/src'
app.config['PREPROCESSOR_PROG'] = 'buckell_preproc.py'

# this is where preprocessed outputs go, WIFITRACE knows about this from
# the config.txt file
app.config['PROCESSED_DATA_PATH'] = '/home/amm042/src/WiFiTrace/WiFiTrace/data'
app.config['WIFITRACE_REPORT_PATH'] = '/home/amm042/src/WiFiTrace/WiFiTrace/data/reports'

# this is the WIFITRACE program from UMASS
app.config['WIFITRACE_PATH'] = '/home/amm042/src/WiFiTrace/WiFiTrace/src'
app.config['WIFITRACE_PROG'] = 'main.py'

# where server keeps run logs and stdout
app.config['REPORT_PATH'] = '/home/amm042/src/WiFiTrace/Server/reports'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['REPORT_PATH'], exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload():
    """upload an anonymized syslog file to the server
    eg:
    $ curl -i -F 'file=@172.30.121.21.messages-20200604.processed.log' localhost:5000/upload

    """

    # check if the post request has the file part
    if 'file' not in request.files:
        app.logger.debug(request.files)
        response = jsonify(success=False, msg='No file in request.')
        response.status_code = 400
        return response

    file = request.files['file']
    if file.filename == '':
        app.logger.debug(request.files)
        response = jsonify(success=False, msg='Empty filename in request.')
        response.status_code = 400
        return response

    # no longer using IP source
    file_ip_src = ".".join(file.filename.split('.')[:4])
    file_date = file.filename.split('-')[1].split('.')[0]
    filename = os.path.join(app.config['UPLOAD_FOLDER'],
                            secure_filename(file.filename))

    processed_output_filename = os.path.join(
        app.config['PROCESSED_DATA_PATH'],
        file_date + "-wifitrace.csv")

    year = file_date[:4]

    app.logger.info("Upload file to {}".format(filename))
    app.logger.info("Processed file is {}".format(processed_output_filename))
    file.save(filename)

    preproc_cmd = '{} -o {} -y {} {}'.format(
        app.config['PREPROCESSOR_PROG'],
        processed_output_filename,
        year,
        filename)

    proc = subprocess.Popen(
        shlex.split('/usr/bin/env python3 ' + preproc_cmd),
        cwd = app.config['PREPROCESSOR_PATH'])

    return jsonify(success=True, pid=proc.pid)

def run_trace(uid, mac_id, start_date, end_date, min_session_length, pidfile):
    """this thread spawns a new process to run the wifi trace but captures
    stdout and stderr to an appropriate log file based on the uid
    """
    app.logger.info("Running trace {}".format(uid))

    try:
        s = datetime.now()
        with open(os.path.join(
                app.config['REPORT_PATH'],
                "{}.log".format(uid)), 'w') as logfile:

            wifitrace_cmd = "{} -m {} -s {} -e {} -l {}".format(
                app.config['WIFITRACE_PROG'],
                mac_id,
                start_date.strftime("%Y%m%d"),
                end_date.strftime("%Y%m%d"),
                min_session_length
            )
            app.logger.info("cmd is: {}".format(wifitrace_cmd))
            proc = subprocess.Popen(
                shlex.split('/usr/bin/env python3 ' + wifitrace_cmd),
                cwd = app.config['WIFITRACE_PATH'],
                stdout = logfile,
                stderr = logfile
            )

            with open(pidfile, 'w') as pf:
                pf.write("{}\n".format(proc.pid))

            proc.wait()
    finally:
        os.remove(pidfile)

    app.logger.info("Trace {} complete in {}.".format(
        uid, datetime.now() - s))

@app.route('/begin_trace/<mac_id>', methods=['POST'])
def begin_trace(mac_id):
    "begin a trace using a json object"

    app.logger.info("Begin trace for {}".format(mac_id))

    if 'start_date' not in request.args:
        return jsonify(success=False, message="No start_date specified.")
    else:
        start_date = dateutil.parser.parse(request.args['start_date'])

    if 'end_date' not in request.args:
        return jsonify(success=False, message="No end_date specified.")
    else:
        end_date = dateutil.parser.parse(request.args['end_date'])

    if 'min_session_length' not in request.args:
        min_session_length = 15
    else:
        min_session_length = int(request.args['min_session_length'])

    reports = ["{}_{}_{}_{}.{}".format(
        name,
        mac_id,
        end_date.strftime("%Y%m%d"),
        (end_date-start_date).days,
        ext) for name, ext in [("User_Report", "txt"),
                               ("User_Report", "json"),
                               ("Patient_Report", "txt"),
                               ("Patient_Report", "json")]]

    uid = uuid.uuid1()

    # create pid file to signal running, remove when complete.
    pidfile=os.path.join(
            app.config['REPORT_PATH'],
            "{}.pid".format(uid))
    open(pidfile, 'a').close()

    threading.Thread(target=run_trace,
                     name="WiFiTrace {}".format(uid),
                     args=(uid, mac_id,
                           start_date,
                           end_date,
                           min_session_length,
                           pidfile)
                     ).start()

    return jsonify(success="True", reports=reports, uid=uid)

@app.route('/check_trace/<uid>', methods=['GET'])
def check_trace(uid):
    pidfile = os.path.join(
        app.config['REPORT_PATH'],
        "{}.pid".format(uid))
    if os.path.exists(pidfile):
        try:
            with open(pidfile, 'r') as f:
                pid = int(f.readline())
        except:
            pid = None
        return jsonify(success=True, running=True, pid=pid)
    else:
        return jsonify(success=True, running=False)

@app.route('/get_report/<filename>', methods=['GET'])
def get_report(filename):

    app.logger.info("Get report: {}".format(filename))

    return send_from_directory(app.config['WIFITRACE_REPORT_PATH'],
                                filename)
