import dateutil.parser

class syslogfile:

    """
    sample log file lines

    Jun  5 00:00:00 PsWJiKZKMdjIiBXJDFBFKw== stm[3644]:  <501093> <NOTI> |AP zLCa3w3aV2eMxOOKn5W0iA== stm|  Auth success: bc:3b:af:0QPMAJ1Y7lFafNTN9ClqeQ==: AP IglYn6MGNLJicRKWk83NBA==

    Jun  5 00:00:00 Aruba_MD3 authmgr[3956]: <522038> <3956> <NOTI> <Aruba_MD3 RzBjt6+u102Y7c/V4E0syQ==>  username=gHOpZ6u4/AcRjxL+MIF9ug== MAC=bc:3b:af:0QPMAJ1Y7lFafNTN9ClqeQ== IP=llR/WCvVnXCE/hwpurz76Q== Result=Successful method=MAC server=netauth-1
    """
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

        items = rawline.split()


        # 0,1,2 event time
        # Month (3 letter), Day of month, Time (24 hr 00:00:00)
        when = dateutil.parser.parse(" ".join(items[0:3]))

        # 3 process name/pid
        # 'stm[3644]:'
        # ignore

        # 4 event code '<501093>'
        # remove brackets
        event = int(items[5][1:-1])

        if items[7] == '<NOTI>':
            msg = rawline[rawline.index(items[8]):]
        else:
            msg = rawline[rawline.index(items[7]):]
        return rawline, when, event, msg
