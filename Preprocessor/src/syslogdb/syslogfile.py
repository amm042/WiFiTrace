import dateutil.parser
import re

class syslogfile:

    """
    sample log file lines

Jun  4 14:49:11 <IP: Yby4RwHE> stm[2793]:  <501093> <NOTI> |AP <AP: zHA8HqvF>@<IP: Yby4RwHE> stm|  Auth success: b4:f1:da:<MAC: 7jhQ59up>: AP <IP: Yby4RwHE>-18:64:72:<MAC: a6DOjQ2Z>-<AP: zHA8HqvF>

Jun  4 14:49:11 <IP: Yby4RwHE> stm[2793]:  <501095> <NOTI> |AP <AP: zHA8HqvF>@<IP: Yby4RwHE> stm|  Assoc request @ 14:49:11.797027: b4:f1:da:<MAC: 7jhQ59up> (SN 32): AP <IP: Yby4RwHE>-18:64:72:<MAC: a6DOjQ2Z>-<AP: zHA8HqvF>

Jun  4 14:49:11 Aruba_MD3 stm[30085]: <501218> <30085> <NOTI> <Aruba_MD3 <IP: RzBjt6+u>>  stm_sta_assign_vlan 21416: VLAN: sta b4:f1:da:<MAC: 7jhQ59up>, STM assigns MAC based vlan_id 111

Jun  4 14:49:11 Aruba_MD3 stm[30085]: <501080> <30085> <NOTI> <Aruba_MD3 <IP: RzBjt6+u>>  Deauth to sta: b4:f1:da:<MAC: 7jhQ59up>: Ageout AP <IP: FPi2mkE2>-18:64:72:<MAC: cXFJFLde>-<AP: BVr/7c1k> STA has roamed to another AP

Jun  4 14:49:11 Aruba_MD3 stm[30085]: <501100> <30085> <NOTI> <Aruba_MD3 <IP: RzBjt6+u>>  Assoc success @ 14:49:11.809533: b4:f1:da:<MAC: 7jhQ59up>: AP <IP: Yby4RwHE>-18:64:72:<MAC: a6DOjQ2Z>-<AP: zHA8HqvF>

Jun  4 14:49:11 Aruba_MD3 authmgr[3956]: <522008> <5194> <NOTI> <Aruba_MD3 <IP: RzBjt6+u>>  User Authentication Successful: username=<USERNAME: 0u1zqMTU> MAC=b4:f1:da:<MAC: 7jhQ59up> IP=<IP: 8xLwHtFO> role=bu_user VLAN=111 AP=<AP: zHA8HqvF> SSID=bucknell.edu AAA profile=cp-bucknell.edu auth method=802.1x auth server=netauth-1

Jun  4 14:49:11 <IP: Yby4RwHE> stm[2793]:  <501100> <NOTI> |AP <AP: zHA8HqvF>@<IP: Yby4RwHE> stm|  Assoc success @ 14:49:11.804189: b4:f1:da:<MAC: 7jhQ59up>: AP <IP: Yby4RwHE>-18:64:72:<MAC: a6DOjQ2Z>-<AP: zHA8HqvF>

Jun  4 14:49:11 <IP: FPi2mkE2> stm[2764]:  <501105> <NOTI> |AP <AP: BVr/7c1k>@<IP: FPi2mkE2> stm|  Deauth from sta: b4:f1:da:<MAC: 7jhQ59up>: AP <IP: FPi2mkE2>-18:64:72:<MAC: cXFJFLde>-<AP: BVr/7c1k> Reason STA has roamed to another AP

Jun  4 14:49:14 <IP: Rxk6sTF4> stm[3319]:  <501093> <NOTI> |AP <AP: ryya9cBB>@<IP: Rxk6sTF4> stm|  Auth success: cc:61:e5:<MAC: Y7LoG01v>: AP <IP: Rxk6sTF4>-7c:57:3c:<MAC: miVKzyjT>-<AP: ryya9cBB>

Jun  4 14:49:14 <IP: Rxk6sTF4> stm[3319]:  <501095> <NOTI> |AP <AP: ryya9cBB>@<IP: Rxk6sTF4> stm|  Assoc request @ 14:49:14.968934: cc:61:e5:<MAC: Y7LoG01v> (SN 0): AP <IP: Rxk6sTF4>-7c:57:3c:<MAC: miVKzyjT>-<AP: ryya9cBB>

    """

    # match digits enclosed in brackets (first one is the event id)
    brackets = re.compile("<(\d*)>")

    def __init__(self, syslogfilename=None):
        "attach to a syslog file"
        self.syslogfilename = syslogfilename

    def __enter__(self):
        self.syslogfile = open(self.syslogfilename,
            encoding="ascii", errors="backslashreplace")
        return self

    def __exit__(self, type, value, traceback):
        self.syslogfile.close()

    def __iter__(self):
        return self

    def __next__(self):
        rawline = self.syslogfile.readline()

        if rawline == "":
            raise StopIteration

        items = rawline.split()

        #print("-"*60)
        #print(rawline)

        # 0,1,2 event time
        # Month (3 letter), Day of month, Time (24 hr 00:00:00)
        when = dateutil.parser.parse(" ".join(items[0:3]))


        # 3 process name/pid
        # 'stm[3644]:'
        # ignore

        # 4 event code '<501093>'
        # remove brackets
        evt = syslogfile.brackets.search(rawline)
        if (evt):
            event = int(evt.group(1))
        else:
            event = None

        return rawline, when, event
