
"""

This takes Bucknell anonymized syslog files and creates input files for WiFiTrace.

### WiFiTrace : Contact Tracing Tool

**Input Data Format :**

The input to WiFiTrace is a csv file where each row of the csv file represents a device session.
The columns in the csv file are:

  MAC,Session_AP_Name,Year,Month,Date,Start_Time,End_Time,Unix_Start_Time,Unix_End_Time

Field Description:
    MAC: (MAC Id of the device)
    Session_AP_Name: Access Point Name/ID where device was connected
    Year: YYYY
    Month: MMM (eg: Jan, Feb, Mar, etc)
    Date: DD (01-31)
    Start_Time : Start time of session in HH:MM (24-hr format)
    End_Time : End time of session in HH:MM (24-hr format)
    Unix_Start_Time : Start time of session in Unix Timestamp
    Unix_End_Time : End time of session in Unix Timestamp

"""

import argparse
from syslogdb import syslogfile
from syslogdb import aruba_event

def main ():
    parser = argparse.ArgumentParser(description='Process Bucknell Aruba syslogs to WifiTrace device sessions')

    parser.add_argument('input_filename', help="Name of aruba log file to parse sessions from.")
    args = parser.parse_args()

    lines = 0

    print("Opening Aruba syslog: ", args.input_filename)

    with syslogfile(args.input_filename) as db:
        for rawline, when, event, msg in db:
            print(rawline)
            print("::: ", when, event, msg)
            print("--> ", aruba_event(event, msg))
            lines += 1
            if lines > 500:
                break

if __name__=="__main__":
    main()
