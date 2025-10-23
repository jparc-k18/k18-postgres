#!/usr/bin/env python3

import time
import datetime
from epics import caget
import json
import os
import psycopg
import pytz
import logging

from myenv import db_config

module_name = os.path.splitext(os.path.basename(__file__))[0]
#logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('__main__').getChild(__name__)

magnet_list = [

  'AK18D1', 'AH18',
  'K18Q1', 'K18Q2', 'K18D2', 'K18Q3', 'K18O1', 'K18Q4', 'K18S1', 'K18CM1',
  'K18CM2', 'K18S2', 'K18Q5', 'K18Q6', 'K18D3', 'K18Q7', 'K18O2', 'K18S3',
  'K18CM3', 'K18CM4', 'K18S4', 'K18Q8', 'K18O3', 'K18Q9',
  'K18Q10', 'K18Q11', 'K18D4', 'K18Q12', 'K18Q13',
  'S2SQ1','S2SQ2','S2SD1'

]

def main():
  while True:
    try:
      timestamp = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
      values = {}
      for name in magnet_list:
        try:
          cset = caget(f'HDPS:{name}:CSET')
          cmon = caget(f'HDPS:{name}:CMON')
          pol  = caget(f'HDPS:{name}:POL', as_string=True)
          values[name] = {'cset': cset, 'cmon': cmon, 'pol': pol}
        except Exception as e:
          logger.warning(f'Failed to get {name}: {e}')
      with psycopg.connect(**db_config) as conn:
        with conn.cursor() as cur:
          sql = f'INSERT INTO {module_name} (timestamp, magnet_data) VALUES (%s, %s)'
          cur.execute(sql, (timestamp, json.dumps(values)))# JSONB type data
        logger.debug("Logged %d magnets at %s", len(values), timestamp.isoformat())
    except Exception as e:
      logger.error(e)
    time.sleep(30)


if __name__ == '__main__':
  main()
