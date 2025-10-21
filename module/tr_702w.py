#!/usr/bin/env python3

import base64
import json
import re
import pathlib
import requests
import time
import logging

from urllib.parse import urlparse
from datetime import datetime, timezone, timedelta
from pathlib import Path

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('__main__').getChild(__name__)

class TR_702W():

  def __init__(self, url, timeout = 0.1, debug=False):
   self.url = url
   self.host = urlparse(url).netloc
   logger.debug('host = {}'.format(self.url))

  #______________________________________________________
  def __u32(self, b: bytes,  pos: int) -> int: # little-endian
    return (b[pos] +
            (b[pos+1] << 8) +
            (b[pos+1] << 16) +
            (b[pos+1] << 24))

  #______________________________________________________
  def __u16(self, b: bytes,  pos: int) -> int: # little-endian
    return b[pos] + (b[pos+1] << 8)

  #______________________________________________________
  def __to_value(self, raw_val: int, attrib: int, disp) -> float:
    v = raw_val - 1000
    if attrib == 0x0D and disp != 0:
      v = int(round(v * 1.8 + 320))
    return v / 10.0

  #______________________________________________________
  def read(self):
    try:
      response = requests.get(self.url,timeout=1)
      response.raise_for_status()
      txt = response.content.decode('utf-8-sig').replace("'",'"')

      data = json.loads(txt)

      d20_b64 = data["D20"]
      raw = base64.b64decode(d20_b64)
      time_raw = self.__u32(raw,14)
      disp_unit = raw[3]
      attrib1 = raw[18]
      ch1_raw = self.__u16(raw,26)
      attrib2 = raw[34]
      ch2_raw = self.__u16(raw,42)

      jst=timezone(timedelta(hours=9))
      dt=datetime.fromtimestamp(time_raw,tz=jst)

      temp = self.__to_value(ch1_raw, attrib1, disp_unit)
      humi = self.__to_value(ch2_raw, attrib2, disp_unit)

      logger.debug('time : {}'.format(dt))
      logger.debug('temp : {}'.format(temp))
      logger.debug('humi : {}'.format(humi))

      return temp, humi

    except requests.exceptions.RequestException as e:
      logger.error('Error : {}'.format(e))
    except json.JSONDecodeError:
      logger.error('JSON decoder Error')
      logger.error('Error : {}'.format(response.text))
    except Exception as e:
      logger.error('UFO Error')

#______________________________________________________
if __name__ == '__main__':

  tr_702w = TR_702W('http://192.168.30.34/current.inc',timeout = 1, debug = True)
#  while True:
  tr_702w.read()
 #   time.sleep(5)
