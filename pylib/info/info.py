"""
    obtain information about the current run

    - who's the user?
    - what CPU?
    - what OS?  etc.

"""
import datetime
import getpass
import platform


def get_machine():
    return " ".join(platform.machine())

def get_uname():
    return " ".join(platform.uname())

def get_platform():
    return " ".join(map(str, [platform.system(), platform.release(),
            platform.version()]))

def get_computer():
    return socket.gethostname()

def get_now():
    return str(datetime.datetime.now())

class Info:
    def __init__(self):
        self.machine = get_machine()
        self.uname = get_uname()
        self.platform = get_platform()
        self.computer = get_computer()
        self.start = get_now()

    @property
    def now(self):
        return get_now()
