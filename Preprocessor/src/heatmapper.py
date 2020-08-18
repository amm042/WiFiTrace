from pymongo import MongoClient
from pprint import pprint
from collections import defaultdict
import dateutil.parser
import argparse
import datetime
import pandas
import math
import sys
import traceback
import os
# {"date/time": "06/19/2020 11:30 AM",
#    "aplist": [
#       {"device": "+48Nms9t", "count": 18},
#       {"device": "5Q8v/Fru", "count": 67},
#       {"device": "7+szTUr+", "count": 33},
#       {"device": "7QwXL3rq", "count": 39},
#       {"device": "83vkZTbn", "count": 62},
#       {"device": "86LFwqme", "count": 59},
#       {"device": "8McEVKhM", "count": 55},
#       {"device": "AJ6EQWJq", "count": 28},
#       {"device": "dfZ1BsUH", "count": 70},
#       {"device": "Dupjz2cw", "count": 84},
#       {"device": "e4Y4cfla", "count": 82}
#    ]
# }

def main(server_url = None, db_name = None):
    parser = argparse.ArgumentParser(
        description='Process WifiTrace csv to heatmap data in Mongodb.')

    parser.add_argument('input_filename',
                        help="Name of WiFiTrace csv (input) file to parse sessions from.")
    parser.add_argument('-i', '--interval',
                        help="Size of interval for heatmap in minutes(default 15)",
                        required=False,
                        default=15)
    args = parser.parse_args()
    df = pandas.read_csv(args.input_filename)
    df = df.dropna()
    df['datetime'] = df.apply(
        lambda x:datetime.datetime.fromtimestamp(x['Unix_Start_Time']),
        axis=1)

    startd = df['datetime'].min()
    startd = startd.replace(hour=0, minute=0, second=0, microsecond=0)
    # round up to next day
    endd = df['datetime'].max()
    endd = endd.replace(hour=0, minute=0, second=0, microsecond=0)
    endd = endd + datetime.timedelta(days=1)

    print("min", startd)
    print("max", endd)
    num_bins = math.ceil((endd-startd).total_seconds()/60/args.interval)

    counts = [{
        "date/time": startd+datetime.timedelta(minutes=i*args.interval),
        "aplist": defaultdict(set)
        } for i in range(num_bins)]

    def counter(row):
        # compute range of bin where MAC is on Session_AP_Name
        # use datetime column

        b = row['datetime']#.to_pydatetime()
        e = datetime.datetime.fromtimestamp(row['Unix_End_Time'])

        i = math.floor((b-startd).total_seconds()/60/args.interval)
        while i<len(counts) and counts[i]['date/time'] <= e:
            # add device to correct ap list set
            counts[i]["aplist"][row["Session_AP_Name"]].add(row["MAC"])
            i = i+1
    df.apply(counter, axis=1)


    # ================== push results to mongo

    client = MongoClient(server_url)
    db = client[db_name]
    collection = db["connections"]

    for doc in counts:
        r = []

        for ap, devset in doc['aplist'].items():
            r.append({
                "device": ap,
                "count": len(devset)
            })
        doc['aplist'] = r

        print("Inserting {} ".format(doc['date/time']), end="")
        it = collection.find_one_and_replace(
            {'date/time': doc['date/time']},
            doc,
            upsert=True)
        if it and '_id' in it:
            print(it['_id'])
        else:
            print("inserted new doc")
if __name__=="__main__":
    import secret

    try:
        main(secret.server_url, secret.db_name)
    except:
      traceback.print_exc()
      sys.exit(os.EX_SOFTWARE)
