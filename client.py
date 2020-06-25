import argparse
import requests
import time
import pprint

API_URL = "http://eg.bucknell.edu:5000"

def main ():
    parser = argparse.ArgumentParser(
        description='WiFiTrace API client example.')

    parser.add_argument('mac_id', help="MAC ID patient value to trace.")
    parser.add_argument('start_date', help="Date (YYYYMMDD) to begin tracing (inclusive)")
    parser.add_argument('end_date', help="Date (YYYYMMDD) to end tracing (inclusive)")
    parser.add_argument('-l','--length',
                        help="Minimum session length (minutes) to use in tracing",
                        type=int,
                        default=15)

    args = parser.parse_args()

    # step 1 start the trace
    r = requests.post(API_URL + '/begin_trace/' + args.mac_id,
                      params = {
                          "start_date": args.start_date,
                          "end_date": args.end_date,
                          "min_session_length": args.length
                      })
    r.raise_for_status()
    begin_resp = r.json()
    assert begin_resp['success']
    print('Begin response:', begin_resp)

    # step 2 wait for the report
    check_resp = {'running': True}
    while check_resp['running']:
        r = requests.get(API_URL + '/check_trace/' + begin_resp['uid'])
        r.raise_for_status()
        check_resp = r.json()
        assert check_resp['success']
        #print(check_resp)
        if check_resp['running']:
            print("Server running, server pid is", check_resp['pid'])
            time.sleep(1)
        else:
            print("Server finished.")

    # step 3 get the reports (json)
    for filename in begin_resp['reports']:
        if filename.endswith('json'):
            r = requests.get(API_URL + '/get_report/' + filename)
            r.raise_for_status()
            print("="*20, filename, "="*20)
            pprint.pprint(r.json())


if __name__=="__main__":
    main()
