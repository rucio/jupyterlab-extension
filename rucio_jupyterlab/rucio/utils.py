import time
import calendar


def parse_timestamp(timestr):
    time_struct = time.strptime(timestr, '%a, %d %b %Y %H:%M:%S %Z')
    return int(calendar.timegm(time_struct))
