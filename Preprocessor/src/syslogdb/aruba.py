import re

# from UMass session.py

# Association Events
assoc_events = [501009,
                501110, # assoc success
                501093, # Auth success
                501109, 501112, 501100,
                501095, 501097, 501092]

# Dis-association events
dis_events = [501099, 501102, 501104, 501113, 501107, 501108, 501114, 501105,
              501098, 501080, 501081, 501106, 501111]


ignore_events = [501218,    # vlan assignment
                 522038,    # association event, doesn't have AP (location)
                 522008,    # user auth success, doesn't have AP (location)
                 522274,    # user auth failed
                 522310,    #  auth_gsm_publish_cluster_sta_section: csta_section_update failed
                 522010,    # User de-authenticated cause=user request
                 522275,    # User Authentication failed.
                 520002,    # Authentication server request Timeout
                 501037,    # no association found trying to disassociate
                 522276,    # Authentication Server Out Of Service while serving request,
                 522329,    # Auth GSM : STA change repkey failed
                 522027,    # IP Spoof from
                 501053,    # STA UP sent to wrong UAC
                 524132,    # GSM: Failed to activate PMK-cache object.
                 524151,    # Failed to delete GSM ager node.
                 501044,    # No authentication found trying to de-authenticate
                 501101,    # Assoc failure
                 501094,    # Auth failure
                 520003,    # Accounting server request Timeout
                 ]

re_mac = re.compile(r"<MAC: (.*?)>")
re_ap = re.compile(r"<AP: (.*?)>")
re_ip = re.compile(r"<IP: (.*?)>")

# station mac
re_station_mac = re.compile(r"sta: \S* [^<]*<MAC: (.*?)>")

# ap IP, OUI, MAC, NAME
re_ap_info = re.compile(r"AP\s*<IP:\s(.*?)>-([^<]*?)<MAC:\s*(.*?)>-<AP:\s*(.*?)>")


# modified from UMass session.py
def aruba_event(event, msg):
    "returns event type, DEVICE ID, AP ID"
    macs = re_mac.findall(msg)
    aps = re_ap.findall(msg)
    ips = re_ip.findall(msg)

    result = None

    if event in [501105]:
        #deauth
        # print(msg)
        # print(aps)
        # print(macs)
        dmsg = msg.split("Deauth from sta")[1]
        stamac = re_mac.findall(dmsg)[0]
        if (stamac == macs[0]):
            if len (aps) > 0:
                result = ("dis", stamac, aps[0])
            else:
                print("CHECK ME: ", msg)
                print(aps)
                print(macs)
                result = ("dis", stamac, macs[1])
        else:
            # unnamed ap reports mac address
            result = ("dis", stamac, macs[0])
    # elif event in [501080]:
    #     #deauth to sta / ageout AP
    elif event in [501080, 501106]:
        #deauth to sta
        # print(msg)
        # print(aps)
        # print(macs)
        dmsg = msg.split("Deauth to sta")[1]
        stamac = re_mac.findall(dmsg)[0]
        if (stamac == macs[0]):
            if len(aps)> 0:
                result = ("dis", stamac, aps[0])
            else:
                result = ("dis", stamac, macs[1])
        else:
            # unnamed ap reports mac address
            result = ("dis", stamac, macs[0])
    elif event in [501102]:
        #Disassoc from sta
        # print(msg)
        # print(aps)
        # print(macs)
        dmsg = msg.split("Disassoc from sta")[1]
        stamac = re_mac.findall(dmsg)[0]
        if (stamac == macs[0]):
            result = ("dis", stamac, aps[0])
        else:
            # unnamed ap reports mac address
            result = ("dis", stamac, macs[0])
    elif event in [501109]:
        #Auth request from sta
        # print(msg)
        # print(aps)
        # print(macs)
        dmsg = msg.split("Auth request")[1]
        stamac = re_mac.findall(dmsg)[0]
        if (stamac == macs[0]):
            result = ("assoc", stamac, aps[0])
        else:
            # unnamed ap reports mac address
            result = ("assoc", stamac, macs[0])
    elif event in [501093, 501095] and len(aps)==0:
        # auth success
        result = ("assoc", macs[1], macs[0])
    elif event in [501100]:
        # assoc success
        if len(aps)==0:
            if len(macs)==3:
                result = ("assoc", macs[0], macs[1])
            else:
                result = ("assoc", macs[1], macs[0])
        else:
            result = ("assoc", macs[0], aps[0])
    else:
        # generic rules
        if event in assoc_events:

            if len(aps)==0:
                aps = macs[1:]

            result = ("assoc", macs[0], aps[0])

        elif event in dis_events:

            if len(aps)==0:
                # print(msg)
                # print(macs)
                # print(aps)
                aps = macs[1:]
            result = ("dis", macs[0], aps[0])

        elif event in ignore_events:
            pass
        else:
            print("*** WARNING: Event not considered: Add in aruba.py: aruba_event function event number, ",event)
            print("***", msg)

    return result
