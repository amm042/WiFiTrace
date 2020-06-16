
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
import datetime
import time
import csv
from syslogdb import syslogfile
from syslogdb import aruba_event



def main ():
    parser = argparse.ArgumentParser(
        description='Process Bucknell Aruba syslogs to WifiTrace device sessions')

    parser.add_argument('input_filename',
                        help="Name of aruba log file to parse sessions from.")
    parser.add_argument('-o', '--output_filename', required=True,
                        help='Name of the output file (csv) to write.')
    parser.add_argument('-y', '--year', help="Year to assume for dates",
                        default=str(datetime.datetime.now().year))
    args = parser.parse_args()

    lines = 0

    print("Opening Aruba syslog: ", args.input_filename)

    stations = {}

    with syslogfile(args.input_filename) as db:
        with open(args.output_filename, 'w') as csvfile:
            csvwriter = csv.writer(csvfile)
            #, dialect = 'unix')
            # write csv header
            csvwriter.writerow(["MAC","Session_AP_Name","Year","Month","Date","Start_Time","End_Time","Unix_Start_Time","Unix_End_Time"])

            # process input file
            for rawline, when, event in db:
                if event == None:
                    continue

                evtinfo = aruba_event(event, rawline)

                if evtinfo:
                    etype, stamac, apmac = evtinfo

                    if etype == 'assoc':
                        dupe = False
                        if stamac+apmac in stations:
                            # dupe assoc. keep old info
                            pass
                        else:
                            # new association
                            stations[stamac+apmac] = when
                            print('session begin for {} at {} on {}'.format(
                                stamac, when, apmac
                                ))

                    elif etype == 'dis':
                        if stamac+apmac in stations:
                            q = stations[stamac+apmac]
                            print('session end for {} at {} on {} -- len: {}'.format(
                                stamac, when, apmac,
                                when - q
                            ))
# fields ["MAC","Session_AP_Name","Year","Month","Date","Start_Time","End_Time","Unix_Start_Time","Unix_End_Time"]
                            csvwriter.writerow([
                                stamac,
                                apmac,
                                args.year if args.year else when.year,
                                when.month,
                                when.day,
                                q.strftime("%H:%M"),#time HH:MM
                                when.strftime("%H:%M"), #when.time(),
                                time.mktime(q.timetuple()),
                                time.mktime(when.timetuple())
                                ])
                            del stations[stamac+apmac]
                        else:
                            # duplicate dis
                            pass
                lines += 1


    print ("end of file -- closing remaining sessions")
    print(stations)
if __name__=="__main__":
    main()
