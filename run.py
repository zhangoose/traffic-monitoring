import sys

import schedule
from sh import tail

from traffic import LogParser


if len(sys.argv) < 2:
    print("Usage: python run.py <ACCESS_LOG_FILENAME>")
    exit


access_log_file = sys.argv[1]
alert_number = sys.argv[2]

log_parser = LogParser()
schedule.every(10).seconds.do(log_parser.most_hits)
schedule.every(1).seconds.do(log_parser.alert, alert_number=float(alert_number))

for line in tail("-f", access_log_file, _iter=True):
    log_parser.parse_log(line)
    schedule.run_pending()
