
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
import pandas

import argparse
import datetime
import json
import time
import os.path
import csv
from syslogdb import syslogfile
from syslogdb import aruba_event

from collections import defaultdict

def main ():
    parser = argparse.ArgumentParser(
        description='Process Bucknell Aruba syslogs to WifiTrace device sessions')

    parser.add_argument('input_filename',
                        help="Name of aruba log file to parse sessions from.")
    parser.add_argument('-o', '--output_filename', required=True,
                        help='Name of the output file (csv) to write.')
    parser.add_argument('-y', '--year', help="Year to assume for dates",
                        default=str(datetime.datetime.now().year))
    parser.add_argument('--heatmap_duration', help="Min duration in minutes for heatmap inclusion",
                        default=5)
    # parser.add_argument('-m', '--heatmap_output_filename', required = True,
    #                     help='Name of file to write heatmap to.')
    parser.add_argument('--overwrite', default=False,
                        help="Overwrite existing output instead of appending.")
    args = parser.parse_args()

    lines = 0

    print("Opening Aruba syslog: ", args.input_filename)

    now = datetime.datetime.now()

    stations = {}
    ap_heatmap = defaultdict(set)

    # read once to get last timestamp (this is dumb)
    last_when = None
    with syslogfile(args.input_filename, tail = True) as db:
        for rawline, when, event in db:
            last_when = when

    if last_when == None:
        print("File has no events!")
        exit(10)

    #fake end
    #last_when = datetime.datetime(2020,6,8,11,30)

    print("Last event is at {}".format(last_when))
    heatmap_mindur = datetime.timedelta(minutes=args.heatmap_duration)
    heatmap_mindate = last_when - heatmap_mindur
    print("Heatmap min duration is {}".format(heatmap_mindur))
    print("Heatmap min date is {}".format(heatmap_mindate))

    if args.overwrite == False and os.path.exists(args.output_filename):
        # prepare to merge
        old_df = pandas.read_csv(args.output_filename, index_col=False)
        old_df.set_index(["MAC", "Session_AP_Name", "Start_Time", "End_Time"],
                         inplace=True)
        print("Loaded {} events from output.".format(len(old_df)))
    else:
        old_df = pandas.DataFrame(
            columns = ["MAC","Session_AP_Name","Year","Month","Date",
                     "Start_Time","End_Time",
                     "Unix_Start_Time","Unix_End_Time"])


    sessions = []
    with syslogfile(args.input_filename) as db:
        # with open(args.output_filename, 'w') as csvfile:
        #     csvwriter = csv.writer(csvfile)
            #, dialect = 'unix')
            # write csv header
            # csvwriter.writerow(["MAC","Session_AP_Name","Year","Month","Date",
            #                     "Start_Time","End_Time",
            #                     "Unix_Start_Time","Unix_End_Time"])

            # process input file
        for rawline, when, event in db:
            if event == None:
                continue

            evtinfo = aruba_event(event, rawline)

            if evtinfo:
                etype, stamac, apmac = evtinfo

                if etype == 'assoc':
                    dupe = False
                    if stamac+":"+apmac in stations:
                        # dupe assoc. keep old info
                        pass
                    else:
                        # new association
                        stations[stamac+":"+apmac] = when
                        # print('session begin for {} at {} on {}'.format(
                        #     stamac, when, apmac
                        #     ))

                elif etype == 'dis':
                    if stamac+":"+apmac in stations:

                        q = stations[stamac+":"+apmac]
                        # print('session end for {} at {} on {} -- len: {}'.format(
                        #     stamac, when, apmac,
                        #     when - q
                        # ))

                        if when >= heatmap_mindate and when - q >= heatmap_mindur:
                            ap_heatmap[apmac].add(stamac)
                            #print("ADD HEATMAP ", stamac)

# fields ["MAC","Session_AP_Name","Year","Month","Date","Start_Time","End_Time","Unix_Start_Time","Unix_End_Time"]
                        # csvwriter.writerow([
                        #     stamac,
                        #     apmac,
                        #     args.year if args.year else when.year,
                        #     when.month,
                        #     when.day,
                        #     q.strftime("%H:%M"),#time HH:MM
                        #     when.strftime("%H:%M"), #when.time(),
                        #     time.mktime(q.timetuple()),
                        #     time.mktime(when.timetuple())
                        #     ])

                        sessions.append({
                            "MAC": stamac,
                            "Session_AP_Name": apmac,
                            "Year": args.year if args.year else when.year,
                            "Month": when.month,
                            "Date": when.day,
                            "Start_Time": q.strftime("%H:%M"),#time HH:MM
                            "End_Time":when.strftime("%H:%M"), #when.time(),
                            "Unix_Start_Time": time.mktime(q.timetuple()),
                            "Unix_End_Time":time.mktime(when.timetuple())
                        })
                        del stations[stamac+":"+apmac]
                    else:
                        # duplicate dis
                        pass
            lines += 1

            # if lines >1000:
            #     break


    print ("end of file -- closing remaining sessions")
    print(stations)

    for key, q in stations.items():
        stamac, apmac = key.split(":")
        when = last_when # assume end time is now

        if when - q > heatmap_mindur:
            ap_heatmap[apmac].add(stamac)
            #print("ADD HEATMAP ", stamac)

        else:
            print("Short duration", when-q, apmac, stamac)
        # csvwriter.writerow([
        #     stamac,
        #     apmac,
        #     args.year if args.year else when.year,
        #     when.month,
        #     when.day,
        #     q.strftime("%H:%M"),# start time time HH:MM
        #     when.strftime("%H:%M"), #end time when.time(),
        #     time.mktime(q.timetuple()),
        #     time.mktime(when.timetuple())
        #     ])
        sessions.append({
            "MAC": stamac,
            "Session_AP_Name": apmac,
            "Year": args.year if args.year else when.year,
            "Month": when.month,
            "Date": when.day,
            "Start_Time": q.strftime("%H:%M"),#time HH:MM
            "End_Time":when.strftime("%H:%M"), #when.time(),
            "Unix_Start_Time": time.mktime(q.timetuple()),
            "Unix_End_Time":time.mktime(when.timetuple())
        })

    # make a DataFrame
    df = pandas.DataFrame.from_records(sessions,
        columns = ["MAC","Session_AP_Name","Year","Month","Date",
                   "Start_Time","End_Time","Unix_Start_Time","Unix_End_Time"],
        index = ["MAC", "Session_AP_Name", "Start_Time", "End_Time"])
    #
    # print(df)
    # print(old_df)

    new = pandas.concat([old_df, df], sort=False)
    #new = df.drop(dupes)
    new = new.drop_duplicates()

    print("Writing csv. Old len {}, new len {}.".format(
        len(df)+len(old_df), len(new)
    ))

    new.to_csv(args.output_filename)

    # create heatmap data
    for k,i in ap_heatmap.items():
        ap_heatmap[k] = len(i)

    # print("AP Heatmap")
    # print(ap_heatmap)
    # # write heatmap file
    # with open(args.heatmap_output_filename, 'w') as heatmapfile:
    #     json.dump(ap_heatmap, heatmapfile)

if __name__=="__main__":
    main()
