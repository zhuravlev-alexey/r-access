#!/usr/bin/env python3

from flask import Flask
from flask import request
from flask import render_template

import modules.r_access_helpers

import subprocess
import sqlite3
import re

app = Flask(__name__)
app.config.from_object('config')


@app.route('/connect', methods=['GET', 'POST'])
def connect():
    r_port = ''
    l_dst = modules.r_access_helpers.check_l_dst(request.args.get('l_dst', ''))
    if l_dst:
        # Starting proxy process
        l_port = request.args.get('l_port', '')
        r_proxy = subprocess.Popen([app.config['R_ACCESS_DIR'] + '/modules/r_proxy.py', l_dst, l_port], stdout=subprocess.PIPE, shell=False)
        r_port = r_proxy.stdout.readline()

    # Get active proxy
    conn = sqlite3.connect(app.config['R_ACCESS_DIR'] + '/db/r_access.sqlite')
    c = conn.cursor()
    c.execute('SELECT l_ip, l_port, l_hostname FROM active_r_proxy');
    active_proxy = c.fetchall()
    c.execute('SELECT l_ip, l_port, l_hostname FROM detected_servers');
    detected_servers = c.fetchall()
    conn.close()
    print(active_proxy)
    print(detected_servers)

    return render_template('connect.html', r_port=r_port, active_proxy=active_proxy, detected_servers=detected_servers)


if __name__ == '__main__':
    app.debug = True
    app.run()
