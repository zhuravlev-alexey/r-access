#!/usr/bin/env python3

import sys
import os
import socket
import logging
import sqlite3
import datetime
import re
from threading import Thread




class r_proxy:
    """ Class doc """
    
    def __init__ (self, l_dst, l_port):
        """ Class initialiser """

        self.config = {}
        self.config['r_addr'] = '0.0.0.0'
        self.config['r_ports'] = (5900,5901,5902,5903,5904,5905,5906,)
        self.config['log'] = '/var/log/rd_access.log'
        self.config['r_access_dir'] = '/var/www/r-access/'
        self.config['ip_regexp'] = '^(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.' + \
                                '(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.' + \
                                '(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.' + \
                                '(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$'
        self.config['hostname_regexp'] = '^[a-zA-Z0-9-_\.]+$'

        logging.basicConfig(filename=self.config['log'], level=logging.DEBUG)
        logging.getLogger('rd_proxy')
        logging.debug('Starting')

        self.l_port = int(l_port)

        
        logging.debug('get l_dst ' + str(l_dst))

        if l_dst in ('127.0.0.1', 'localhost'):
            logging.error("Left address " + l_dst + " - denied.")
            print("Left address " + l_dst + " - denied.", flush=True)
            
            sys.exit()
        elif re.match(self.config['ip_regexp'], l_dst):
            self.l_ip = l_dst
            try:
                self.l_hostname = socket.gethostbyaddr(self.l_ip)
            except:
                self.l_hostname = 'none'
        elif re.match(self.config['hostname_regexp'], l_dst):
            self.l_hostname = l_dst
            try:
                self.l_ip = socket.gethostbyname(self.l_hostname)
            except:
                logging.error("Can't resolve hostname to IP-address")
                print("Can't resolve hostname to IP-address", flush=True)
                sys.exit()
        else:
            logging.error("Destination address invalid: not matches for IP or hostname")
            print("Destination address invalid: not matches for IP or hostname", flush=True)
            sys.exit()
        
        self.start()


    def start(self):
        # Пытаемся забиндиться на свободный порт
        for r_port in self.config['r_ports']:
            logging.info('Trying bind on ' + self.config['r_addr'] + ':' + str(r_port))
            try:
                r_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                r_socket.bind((self.config['r_addr'], r_port))
                r_socket.listen(5)
                logging.info('Listen on ' + self.config['r_addr'] + ':' + str(r_port))
                break
            except:
                logging.error('Fail: ')
        if not r_socket:
            logging.error('Can\'t bind')
            exit


        try:
            logging.debug("Trying connect to left side: " + self.l_ip + ":" + str(self.l_port))
            l_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            l_socket.connect((self.l_ip, self.l_port))
        except:
            logging.error("Can't connect to " + self.l_ip + ":" + str(self.l_port) + "!")
            print("Can't connect to " + self.l_ip + ":" + self.l_port + "!", flush=True)
            sys.exit()


        conn = sqlite3.connect(self.config['r_access_dir'] + '/db/r_access.sqlite')
        c = conn.cursor()
        # If binding success, old records with this r_ports are invalid. Delete them
        c.execute("DELETE FROM active_r_proxy WHERE r_port=:r_port", {'r_port':r_port});
        # Insert into active_r_proxy information about new active r_proxy
        c.execute("INSERT INTO active_r_proxy VALUES (?,?,?,?,?,?,?,?)", (self.l_ip,
                                                                        self.l_hostname, 
                                                                        self.l_port,
                                                                        r_port,
                                                                        os.getpid(),
                                                                        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                                        'waiting',
                                                                        None)
                )
        conn.commit()
        conn.close()

        # Return r_port to parent process
        print(str(r_port), flush=True)
        
        while True:
            logging.info('Waiting')
            r_socket, address = r_socket.accept()
            logging.info('Connected by ' + str(address))
            l_t = Thread(target=self.worker, args=(l_socket, r_socket))
            r_t = Thread(target=self.worker, args=(r_socket, l_socket))
            l_t.start()
            r_t.start()
            l_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            l_socket.connect((self.l_ip, self.l_port))
            
    
    
    def worker(self, socket1, socket2):
        while True:
            data = socket1.recv(1024)
            if not data:
                socket1.close()
                socket2.close()
                return
            socket2.send(data)


r_proxy(sys.argv[1], sys.argv[2])
