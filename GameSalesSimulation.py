import json

# logger
from logging import getLogger, config
with open('./log_config.json', 'r') as f:
    log_conf = json.load(f)
config.dictConfig(log_conf)
logger = getLogger(__name__)

player = 1000
play_fee = 2 # $
operation_fee = 0.1
play_count = 20
month = 30

def main():
    logger.info(player * play_fee * operation_fee * play_count * month)


if __name__ == '__main__':
    main()
