import argparse

import schedule
from sh import tail

from traffic import LogParser


parser = argparse.ArgumentParser()
parser.add_argument("log_file", help="the access log file you want to get traffic for")
parser.add_argument("threshold", help="the threshold of traffic you want alerts for")
args = parser.parse_args()

access_log_file = args.log_file
alert_number = float(args.threshold)

log_parser = LogParser()
schedule.every(10).seconds.do(log_parser.most_hits)
schedule.every(1).seconds.do(log_parser.alert, alert_number=alert_number)

for line in tail("-f", access_log_file, _iter=True):
    log_parser.parse_log(line)
    schedule.run_pending()
