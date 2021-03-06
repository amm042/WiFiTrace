
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
                        default=None, type=int)
    parser.add_argument('--debug_ap', help="AP hash to debug (print details)",
                        default=None)
    parser.add_argument('--duration', help="Min duration in minutes for inclusion",
                        default=0.25)
    # parser.add_argument('-m', '--heatmap_output_filename', required = True,
    #                     help='Name of file to write heatmap to.')
    parser.add_argument('--overwrite', default=False,
                        help="Overwrite existing output instead of appending.")
    args = parser.parse_args()

    lines = 0

    outdir = os.path.split(args.output_filename)[0]
    if not os.path.exists(outdir):
        print("Creating output dir: {}".format(outdir))
        os.makedirs(outdir)

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
    mindur = datetime.timedelta(minutes=args.duration)
    heatmap_mindate = last_when - mindur
    print("min duration is {}".format(mindur))
    # print("Heatmap min date is {}".format(heatmap_mindate))

    if args.debug_ap:
        print("Debug station: {}".format(args.debug_ap))

    if args.overwrite == False and os.path.exists(args.output_filename):
        # prepare to merge
        #old_df = pandas.read_csv(args.output_filename, index_col=False)
        old_df = pandas.read_csv(args.output_filename)
        # old_df.set_index(["MAC", "Session_AP_Name", "Start_Time", "End_Time"],
        #                  inplace=True)
        print("Loaded {} events from output.".format(len(old_df)))
        print("Types are", old_df.dtypes)
    else:
        old_df = None
        # old_df = pandas.DataFrame(
        #     columns = ["MAC","Session_AP_Name","Year","Month","Date",
        #              "Start_Time","End_Time",
        #              "Unix_Start_Time","Unix_End_Time"])


    all_aps = set()
    all_devs = set()
    client_sessions = {} # store last ap associated for each client
    sessions = []
    with syslogfile(args.input_filename) as db:

        # process input file
        for rawline, when, event in db:


            if event == None:
                if args.debug_ap and args.debug_ap in rawline:
                    print("ERROR: No event with this ap: ", rawline)
                    exit(44)
                else:
                    continue

            evtinfo = aruba_event(event, rawline)

            if evtinfo == None and args.debug_ap and args.debug_ap in rawline:
                print("WARN: No aruba event for line:", rawline, event)
            #    exit(45)

            if evtinfo:
                etype, stamac, apmac = evtinfo

                if args.debug_ap and stamac == args.debug_ap:
                    print('ERROR: got station as debug ap--HALT')
                    print(rawline)
                    exit(56)

                if args.debug_ap and apmac == args.debug_ap:
                #    print(rawline)
                    print(etype, stamac, apmac)

                all_aps.add(apmac)
                all_devs.add(stamac)

                if apmac in all_devs:
                    print("ERROR: AP in device set!")
                    print(rawline)
                    print(evtinfo)
                    #exit(42)
                    continue
                if stamac in all_aps:

                    print("ERROR: Device in AP set!")
                # if apmac == 'PSgfrasv':
                    print(rawline)
                    print(evtinfo)
                    #exit(43)
                    continue

                if etype == 'assoc':
                    dupe = False

                    if stamac in client_sessions:
                        if client_sessions[stamac] != apmac:
                            # disassociate from old station
                            oldap = client_sessions[stamac]
                            q = stations[stamac+":"+oldap]
                            record = {
                                "MAC": stamac,
                                "Session_AP_Name": oldap,
                                "Year": args.year if args.year else when.year,
                                "Month": when.month,
                                "Date": when.day,
                                "Start_Time": q.strftime("%H:%M"),#time HH:MM
                                "End_Time":when.strftime("%H:%M"), #when.time(),
                                "Unix_Start_Time": time.mktime(q.timetuple()),
                                "Unix_End_Time": time.mktime(when.timetuple())
                            }
                            sessions.append(record)
                        del client_sessions[stamac]

                    client_sessions[stamac] = apmac

                    if stamac+":"+apmac in stations:
                        # dupe assoc. keep old info
                        pass

                    else:
                        # new association
                        stations[stamac+":"+apmac] = when
                        if args.debug_ap and args.debug_ap == apmac:
                            print('session begin for {} at {} on {}'.format(
                                stamac, when, apmac
                                ))

                elif etype == 'dis':

                    if stamac in client_sessions:
                        # this can happen when roaming
                        # if client_sessions[stamac] != apmac:
                        #     print("{} got dis but from wrong ap {}, had {}".format(
                        #         stamac,
                        #         apmac,
                        #         client_sessions[stamac]))
                        #     print(rawline)
                        #     print(evtinfo)
                        #     exit(46)

                        del client_sessions[stamac]

                    if stamac+":"+apmac in stations:

                        q = stations[stamac+":"+apmac]

                        if args.debug_ap and args.debug_ap == apmac:
                            print('session end for {} at {} on {} -- len: {}'.format(
                                stamac, when, apmac,
                                when - q
                            ))
                        if when - q >= mindur:
                            if when >= heatmap_mindate:
                                ap_heatmap[apmac].add(stamac)
                                #print("ADD HEATMAP ", stamac)

                            record = {
                                "MAC": stamac,
                                "Session_AP_Name": apmac,
                                "Year": args.year if args.year else when.year,
                                "Month": when.month,
                                "Date": when.day,
                                "Start_Time": q.strftime("%H:%M"),#time HH:MM
                                "End_Time":when.strftime("%H:%M"), #when.time(),
                                "Unix_Start_Time": time.mktime(q.timetuple()),
                                "Unix_End_Time": time.mktime(when.timetuple())
                            }
                            sessions.append(record)
                        else:
                            if args.debug_ap and apmac == args.debug_ap:
                                print("SHORT SESSION IGNORED: {}, {}, {}".format(
                                    apmac, stamac, when - q))
                        del stations[stamac+":"+apmac]
                    else:
                        # duplicate dis
                        pass
            lines += 1

            # if lines >1000:
            #     break


    print ("end of file -- closing {} remaining sessions".format(
        len(stations)
    ))

    for key, q in stations.items():
        stamac, apmac = key.split(":")
        when = last_when # assume end time is now

        if when - q > mindur:
            ap_heatmap[apmac].add(stamac)
            #print("ADD HEATMAP ", stamac)

            if args.debug_ap and apmac == args.debug_ap:
                print('session end for {} at {} on {} -- len: {}'.format(
                    stamac, when, apmac,
                    when - q
             ))

            record = {
                "MAC": stamac,
                "Session_AP_Name": apmac,
                "Year": args.year if args.year else when.year,
                "Month": when.month,
                "Date": when.day,
                "Start_Time": q.strftime("%H:%M"),#time HH:MM
                "End_Time":when.strftime("%H:%M"), #when.time(),
                "Unix_Start_Time": time.mktime(q.timetuple()),
                "Unix_End_Time":time.mktime(when.timetuple())
            }
            index = (record["MAC"],
                     record["Session_AP_Name"],
                     record["Year"],
                     record["Month"],
                     record["Date"],
                     record["Start_Time"],
                     record["End_Time"])
            sessions.append(record)

        else:
            if not args.debug_ap or args.debug_ap == apmac:
                print("Short duration", when-q, apmac, stamac)



    # make a DataFrame
    df = pandas.DataFrame.from_records(sessions,
        columns = ["MAC","Session_AP_Name","Year","Month","Date",
                   "Start_Time","End_Time","Unix_Start_Time","Unix_End_Time"])

    print("df Types are", df.dtypes)

    if old_df is None:
        new = df
    else:
        new = old_df.append(df, sort=False, ignore_index=True)
        new = new.drop_duplicates(subset=["MAC","Session_AP_Name",
        "Year","Month","Date",
        "Start_Time","End_Time"])

    print("new Types are", new.dtypes)
    print("Writing csv. Old len {}, new len {}.".format(
        0 if old_df is None else len(old_df), len(new)
    ))

    new.to_csv(args.output_filename, index=False)

    if args.debug_ap:
        print("DEBUG INFO for {}\n".format(args.debug_ap))
        print(ap_heatmap[args.debug_ap])

    # create heatmap data
    # for k,i in ap_heatmap.items():
    #     ap_heatmap[k] = len(i)

    # print("AP Heatmap")
    # print(ap_heatmap)
    # # write heatmap file
    # with open(args.heatmap_output_filename, 'w') as heatmapfile:
    #     json.dump(ap_heatmap, heatmapfile)

if __name__=="__main__":
    main()
