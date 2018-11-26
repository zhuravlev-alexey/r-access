#!/usr/bin/env python3
# -*- coding:utf-8 -*-



import re
import sys
import socket
import sqlite3
import datetime
from threading import Thread



class scanner:
    def __init__ (self):
        self.config = {}
        self.config['scan_addresses'] = ('192.168.1.1-192.168.1.254', )
        self.config['scan_ports'] = (5900,3389,22)
        self.config['r_access_dir'] = '/var/www/r-access/'
        self.config['threads'] = 10

        values = []
        for item in self.config['scan_addresses']:
            addr1, addr2 = re.split('\s*\-\s*', item)
            addr_list = self.get_address_list(addr1, addr2)
        
            for l_ip in addr_list:
                for l_port in self.config['scan_ports']:
                    #print(l_ip + ":" + str(l_port))
                    try:
                        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        test_socket.settimeout(0.3)
                        test_socket.connect((l_ip, l_port))
                    except (ConnectionRefusedError, socket.timeout):
                        continue
                    except OSError:
                        continue

        
                    try:
                        l_hostname = socket.gethostbyaddr(l_ip)[0]
                        print(socket.gethostbyaddr(l_ip))
                    except:
                        l_hostname = 'unknown'
                    print("Detected: " + l_ip + ":" + str(l_port) + " (" + l_hostname + ")")
                    values.append((l_ip, l_port, l_hostname, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

        conn = sqlite3.connect(self.config['r_access_dir'] + '/db/r_access.sqlite')
        c = conn.cursor()
        c.execute("DELETE FROM detected_servers")
        c.execute("VACUUM")
        c.executemany("INSERT INTO detected_servers VALUES (?,?,?,?)", values)
        conn.commit()
        conn.close()


    # Get address list
    def get_address_list (self, address1, address2):
        address1 = address1.split('.')
        address2 = address2.split('.')
        address_list = []
        prefix = ''
    
        for i in range(len(address1)):
            address1[i] = int(address1[i])
    
        for i in range(len(address2)):
            address2[i] = int(address2[i])
    
        # Too many address to scan
        if address1[0] != address2[0] or address1[1] != address2[1]:
            print('Scan range too big.')
            sys.exit()
        
        prefix = str(address1[0]) + '.' + str(address1[1]) + '.'
    
        # 3 octet of IP-addresses is equal, generate only 4 octet
        if address1[2] == address2[2]:
            prefix += str(address1[2]) + '.'
            for i in range(address1[3], address2[3]+1):
                address_list.append(prefix + str(i))
    
        # 3 octet of IP-addresses is not equal, generate 3 octet and 4 octet
        else:
            n = 0
            print(len(range(address1[2], address2[2])))
            for i in range(address1[2], address2[2]+1):
                if n == 0:
                    for k in range (address1[3], 255):
                        address_list.append(prefix + str(i) + '.' + str(k))
                elif n == len(range(address1[2], address2[2])):
                    for k in range (1, address2[3]+1):
                        address_list.append(prefix + str(i) + '.' + str(k))
                else:
                    for k in range (1, 254):
                        address_list.append(prefix + str(i) + '.' + str(k))
                n += 1
                    
        return address_list


        

scanner()

