import re
import socket



def check_l_dst(l_dst):
    l_dst.strip()
    ip_regexp = '^(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.' + \
                '(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.' + \
                '(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.' + \
                '(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$'
    hostname_regexp = '^[a-zA-Z0-9-_\.]+$'
    if l_dst in ('127.0.0.1', 'localhost'):
        print('Error localhost')
    elif re.match(ip_regexp, l_dst) or re.match(hostname_regexp, l_dst):
        return l_dst
    else:
        print('error')
    return None
