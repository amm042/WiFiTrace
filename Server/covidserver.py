"""

run the development server with "$ flask run"
"""

from flask import Flask, jsonify, request
from werkzeug.utils import secure_filename
import subprocess
import os.path
import shlex


from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/tmp/covid/upload'

app.config['PREPROCESSOR_PATH'] = '/home/amm042/src/WiFiTrace/Preprocessor/src'
app.config['PREPROCESSOR_PROG'] = 'buckell_preproc.py'
app.config['PROCESSED_DATA_PATH'] = '/home/amm042/src/WiFiTrace/WifiTrace/data'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

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
        file_date + "-wifitrace.log")

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
