import re

# from UMass session.py

# Association Events
assoc_events = [501009, 501110, 501093, 501094, 501109, 501101, 501112, 501100,
                501095, 501097, 501092]

# Dis-association events
dis_events = [501099, 501102, 501104, 501113, 501107, 501108, 501114, 501105,
              501044, 501098, 501080, 501081, 501106, 501111]


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

    macs = re_mac.findall(msg)
    aps = re_ap.findall(msg)
    ips = re_ip.findall(msg)

    result = None
    if event in assoc_events:
        if len(aps)==0:
            # print(msg)
            # print(macs)
            # print(aps)
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
