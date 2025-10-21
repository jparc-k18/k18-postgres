#!/usr/bin/env python3

import datetime
import logging
import pytz
import psycopg
import random
import time
import threading
from myenv import db_config

import tr_702w

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('__main__').getChild(__name__)

class AIR:
  def __init__(self, url, interval=10):
    self.url = url
    self.interval = interval
    self.will_stop = False
    self.wait = True

  def __updater(self):
    logger.debug(datetime.datetime.now())
    with psycopg.connect(**db_config) as conn:
      with conn.cursor() as cur:
        insert_list = []
        now = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
        device = tr_702w.TR_702W(self.url, timeout=1.0, debug=False)
        meas_temp, meas_humi = device.read() # temp, humi
        tap = (device.host, now, meas_temp, meas_humi)
        insert_list.append(tap)
        sql = ('insert into air '+
               '(ip_address, timestamp, meas_temp, meas_humi)' +
               'values(%s,%s,%s,%s)')
        cur.executemany(sql, insert_list)

  def run(self):
    base_time = time.time()
    next_time = 0
    while not self.will_stop:
      try:
        self.__updater()
        next_time = ((base_time - time.time()) % self.interval) or self.interval
        time.sleep(next_time)
      except KeyboardInterrupt:
        break

  def start(self):
    logger.debug('start')
    t = threading.Thread(target=self.run)
    t.daemon = True
    t.start()

  def stop(self):
    logger.debug('stop')
    self.will_stop = True

devices = [

  AIR('http://192.168.30.31/current.inc'),#BH1 rack
  AIR('http://192.168.30.33/current.inc'),#S2S Q1
  AIR('http://192.168.30.34/current.inc'),#hbxx rack
  AIR('http://192.168.30.37/current.inc')#TRG rack

]

def start():
  for d in devices:
    d.start()

def stop():
  for d in devices:
    d.stop()


if __name__== '__main__':
  try:
    start()
    while True:
      time.sleep(3600)
  except KeyboardInterrupt:
    stop()
