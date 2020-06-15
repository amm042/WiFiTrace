# from UMass session.py

# Association Events
assoc_events = [501009, 501110, 501093, 501094, 501109, 501101, 501112, 501100,
                501095, 501097, 501092, 522008]

# Dis-association events
dis_events = [501099, 501102, 501104, 501113, 501107, 501108, 501114, 501105,
              501044, 501098, 501080, 501081, 501106, 501111]

# modified from UMass session.py
def aruba_event(event, msg):
    if event == 501044:
        # Event has substring:
        # sta:%m]: No authentication found trying to de-authenticate to BSSID [bss:%m] on AP [name:%s]
        # For eg:
        # Station [sta:%m]: No authentication found trying to de-authenticate to BSSID [bss:%m] on AP [name:%s]

        keyword_split = line.split("Station ",1)
        ap_item = keyword_split[1].split("BSSID ")[1].split(" ")

        return {
            'macid': keyword_split[1].split(" ")[0],
            'ap_bssid': ap_item[0],
            'ap_name': ap_item[-1]
        }

    elif event == 501098:
        # Events have common substring "[mac:%m]: Moved out from AP [ip:%P]-[bssid:%m]-[name:%s]"
        # Eg.
        # Deauth to sta: [mac:%m]: Moved out from AP [ip:%P]-[bssid:%m]-[name:%s] to new AP
        event_list.append(event)
        month.append(items[0])
        date.append(items[1])
        timestamp.append(items[2])
        keyword_split = line.split(": Moved out from AP ")
        macid.append(keyword_split[0].split(" ")[-1])

        try :
            ap_item = keyword_split[1].split(" ")[0].split("-",2)
        except :
            ap_item = []
            #print(line)
        try:
            ap_bssid.append(ap_item[1])
        except:
            ap_bssid.append("-1")
        try:
            ap_name.append(ap_item[-1])
        except:
            ap_name.append("-1")
        try:
            ap_ip.append(ap_item[0])
        except:
            ap_ip.append("-1")

    elif event in [501080, 501081, 501106]:

        # All events have common substring "[mac:%m]: Ageout AP [ip:%P]-[bssid:%m]-[name:%s]"
        # For eg:
        # Auth request: [mac:%m]: AP [ip:%P]-[bssid:%m]-[name:%s] auth_alg [auth_alg:%d]
        event_list.append(event)
        month.append(items[0])
        date.append(items[1])
        timestamp.append(items[2])
        keyword_split = line.split(": Ageout AP ")
        macid.append(keyword_split[0].split(" ")[-1])

        try :
            ap_item = keyword_split[1].split(" ")[0].split("-",2)
        except :
            ap_item = []
            #print(line)
        try:
            ap_bssid.append(ap_item[1])
        except:
            ap_bssid.append("-1")
        try:
            ap_name.append(ap_item[-1])
        except:
            ap_name.append("-1")
        try:
            ap_ip.append(ap_item[0])
        except:
            ap_ip.append("-1")

    elif event in [501009, 501110, 501111,501093,501094, 501099, 501109
                ,501101 ,501102,501104,501112,501113, 501100 ,501107 , 501108
                ,501114, 501117 ,501126,501129,501130, 501128 ,501105 ,501118 ,501119, 501120 ,501121 ,501122 ,501123,501124 ,501125
                ,501127 ,501130, 501082 ,501085, 501090]:

        # All events have common substring [mac:%m]: AP [ip:%P]-[bssid:%m]-[name:%s]"
        # For eg:
        # Auth request: [mac:%m]: AP [ip:%P]-[bssid:%m]-[name:%s] auth_alg [auth_alg:%d]

        keyword_split = msg.rsplit(": AP ",1)
        try:
            ap_item = keyword_split[1].split(" ")[0].split("-",2)
        except:
            ap_item = [-1,-1,-1]

        print(ap_item)

        return {
            'macid': keyword_split[0].split(" ")[-1],
            'ap_bssid': ap_item[1],
            'ap_name': ap_item[-1],
            'ap_ip': ap_item[0]
        }

    elif event == 501095:

        # All events have common substring "[mac:%m] (SN [sn:%d]): AP [ip:%P]-[bssid:%m]-[name:%s]"
        # For eg:
        #Assoc request @ [tstr:%s]: [mac:%m] (SN [sn:%d]): AP [ip:%P]-[bssid:%m]-[name:%s]
        event_list.append(event)
        month.append(items[0])
        date.append(items[1])
        timestamp.append(items[2])
        keyword_split = line.rsplit(" AP ",1)
        macid.append(keyword_split[0].split(" (SN")[0].split(" ")[-1])

        try :
            ap_item = keyword_split[1].split(" ")[0].split("-",2)
        except :
            ap_item = []
            #print(line)
        try:
            ap_bssid.append(ap_item[1])
        except:
            ap_bssid.append("-1")
        try:
            ap_name.append(ap_item[-1])
        except:
            ap_name.append("-1")
        try:
            ap_ip.append(ap_item[0])
        except:
            ap_ip.append("-1")

    elif event in [501097, 501092,501084,501087, 501088, 501089]:

        # All events have common substring "[mac:%m]: Dropped AP [ip:%P]-[bssid:%m]-[name:%s]"
        # For eg:
        # Assoc request: [mac:%m]: Dropped AP [ip:%P]-[bssid:%m]-[name:%s] for STA DoS protection
        event_list.append(event)
        month.append(items[0])
        date.append(items[1])
        timestamp.append(items[2])
        keyword_split = line.rsplit(": Dropped AP ",1)
        macid.append(keyword_split[0].split(" ")[-1])

        try :
            ap_item = keyword_split[1].split(" ")[0].split("-",2)
        except :
            ap_item = []
            #print(line)
        try:
            ap_bssid.append(ap_item[1])
        except:
            ap_bssid.append("-1")
        try:
            ap_name.append(ap_item[-1])
        except:
            ap_name.append("-1")
        try:
            ap_ip.append(ap_item[0])
        except:
            ap_ip.append("-1")

    elif event == 522008:
        # This is the authentication messages, which is very different
        event_list.append(event)
        month.append(items[0])
        date.append(items[1])
        timestamp.append(items[2])

        # get mac
        try:
            macid.append(items[14].split("=")[1])
        except:
            macid.append("-1")

        # get ip
        try:
            ap_ip.append(items[15].split("=")[1])
        except:
            ap_ip.append("-1")

        # get AP
        try:
            ap_name.append(items[18].split("=")[-1])
        except:
            ap_name.append("-1")

        #get SSID
        try:
            ap_bssid.append(items[19].split("=")[-1])
        except:
            ap_bssid.append("-1")

    else:
        print("*** WARNING: Event not considered: Add in user_trajectory.py : extract_traj_items function, ",event)
