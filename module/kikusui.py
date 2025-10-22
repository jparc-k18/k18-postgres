#!/usr/bin/env python3

import datetime
import logging
import pytz
import psycopg
import random
import time
import threading
from myenv import db_config

import pmx_a

logger = logging.getLogger('__main__').getChild(__name__)

class KIKUSUI:
  def __init__(self, ip_address, interval=10):
    self.ip_address = ip_address
    self.interval = interval
    self.will_stop = False
    self.wait = True

  def __updater(self):
    logger.debug(datetime.datetime.now())
    with psycopg.connect(**db_config) as conn:
      with conn.cursor() as cur:
        insert_list = []
        now = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
        device = pmx_a.PMX_A(self.ip_address, timeout=1.0, debug=False)
        if not device.is_open:
          logger.warning(f'{self.__class__.__name__} cannot connect to {self.ip_address}')
          return
        idn = device.idn()
        channel = 0
        meas_volt = device.volt()
        meas_curr = device.curr()
        output = device.outp()
        stat = device.stat()
        tap = (device.host, idn, channel, now, output, meas_volt, meas_curr)
        insert_list.append(tap)
        sql = ('insert into kikusui '+
               '(ip_address, idn, channel, timestamp, output, meas_volt, meas_curr)' +
               'values(%s,%s,%s,%s,%s,%s,%s)')
        cur.executemany(sql,insert_list)

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

  KIKUSUI('192.168.30.201'), #RC-X
  KIKUSUI('192.168.30.202'), #RC+X
  KIKUSUI('192.168.30.205'), #LSO1
  KIKUSUI('192.168.30.206'), #LSO2
  KIKUSUI('192.168.30.45'), #SDC3 Vth
  KIKUSUI('192.168.30.46'), #SDC4 Vth
  KIKUSUI('192.168.30.47') #SDC5 Vth

]

def start():
  for d in devices:
    d.start()

def stop():
  for d in devices:
    d.stop()


if __name__ == '__main__':
  try:
    start()
    while True:
      time.sleep(3600)
  except KeyboardInterrupt:
    stop()
