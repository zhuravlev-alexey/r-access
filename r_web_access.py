#!/usr/bin/env python3

from flask import Flask, request, redirect
from flask import render_template

import modules.r_access_helpers
from modules.r_proxy import r_proxy 

import subprocess
import sqlite3
import re

app = Flask(__name__)
app.config.from_object('config')


@app.route('/connect', methods=['GET', 'POST'])
def connect():
    if request.args.get('dst', '') and (
                                        re.match('^(\d{1,3}\.){3}\d{1,3}:\d+$', request.args.get('dst', ''))
                                        or
                                        re.match('^[a-zA-Z0-9-_\.]+$', request.args.get('dst', ''))
                                        ):
        l_dst, l_port = request.args.get('dst', '').split(':')
        # Starting proxy process
        r_proxy_proccess = subprocess.Popen([app.config['R_ACCESS_DIR'] + '/modules/r_proxy.py', l_dst, l_port], stdout=subprocess.PIPE, shell=False)
        r_port = r_proxy_proccess.stdout.readline()
    else:
        r_port = ''

    r_p = r_proxy()
    r_p.clean()
    # Get active proxy
    conn = sqlite3.connect(app.config['R_ACCESS_DIR'] + '/db/r_access.sqlite')
    c = conn.cursor()
    c.execute('SELECT l_ip, l_port, l_hostname, r_port, pid FROM active_r_proxy');
    active_proxy = c.fetchall()
    c.execute('SELECT l_ip, l_port, l_hostname FROM detected_servers');
    detected_servers = c.fetchall()
    conn.close()
    return render_template('connect.html', r_port=r_port, active_proxy=active_proxy, detected_servers=detected_servers)

@app.route('/disconnect', methods=['GET', 'POST'])
def disconnect():
    pids = request.args.get('pids')
    if not re.match('[\d,]+', pids):
        return redirect('/connect')
    pids = pids.split(',')
    r_p = r_proxy()
    r_p.stop(pids)
    return redirect('/connect')
    


if __name__ == '__main__':
    app.debug = True
    app.run()
