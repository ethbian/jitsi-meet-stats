#!/usr/bin/env python

#
# Jitsi Meet to Graphite exporter
# version 0.1
# for latest version, howto, grafana dashboard visit
# https://github.com/ethbian/jitsi-meet-stats
#

import requests
import json
import time
import pickle
import struct
import socket
import logging

# change these:
CARBON_SERVER = 'graphite.example.com'
GRAPHITE_PREFIX = 'metrics.jitsi.{}'.format(socket.gethostname())
LOG_FILE = '/var/log/jitsi/jmstats.log'
SKIP_METRICS = ['current_timestamp', 'conference_sizes']
JITSI_STATS = 'http://localhost:8080/colibri/stats'
CARBON_PICKLE_PORT = 2004
SLEEP_SEC = 5


def get_stats():
    err = False
    result = {}
    try:
        r = requests.get(JITSI_STATS)
    except Exception as ex:
        logging.error('Error getting jitsi stats: {}'.format(ex))
        err = True
    if not err:
        try:
            result = r.json()
        except Exception as ex:
            logging.error('Error converting json to dict: {}'.format(ex))
            err = True
    return err, result


def stats2graphite(stats):
    metrics = ([])
    now = int(time.time())
    for key in stats.keys():
        if key in SKIP_METRICS:
            continue
        metric = '{}.{}'.format(GRAPHITE_PREFIX, key)
        metrics.append((metric, (now, stats[key])))
    payload = pickle.dumps(metrics, protocol=2)
    header = struct.pack("!L", len(payload))
    package = header + payload
    return package


logging.basicConfig(filename=LOG_FILE, filemode='a', level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler())
clientSocket = socket.socket()
clientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
try:
    clientSocket.connect((CARBON_SERVER, CARBON_PICKLE_PORT))
except Exception as ex:
    logging.error('Error creating socket: {}'.format(ex))
    raise SystemExit()
connected = True

while True:
    err, stats = get_stats()
    if not err:
        stats2send = stats2graphite(stats)
        try:
            logging.info('{} sending jitsi stats...'.format(time.ctime()))
            clientSocket.sendall(stats2send)
        except socket.error:
            connected = False
            clientSocket = socket.socket()
            logging.warning('Connection lost... ')
            while not connected:
                try:
                    clientSocket.connect((CARBON_SERVER, CARBON_PICKLE_PORT))
                    connected = True
                    logging.warning('re-connection successful')
                except socket.error:
                    logging.warning('{} reconnecting...'.format(time.ctime()))
                    time.sleep(SLEEP_SEC)
    time.sleep(SLEEP_SEC)

clientSocket.close()
