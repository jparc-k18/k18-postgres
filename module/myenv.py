import logging


db_config = {
  'host': 'localhost',
  'port': 5432,
  'dbname': 'k18db',
  'user': 'sks',
  'password': 'beamtime'
  }

def get_logger(name: str = "default", level=logging.INFO) -> logging.Logger:
  logger = logging.getLogger(name)
  if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
      '(%(nam)s) [%(levelname)s] %(message)s',
      )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(level)
  return logger
