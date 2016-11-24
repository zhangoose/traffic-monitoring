import argparse
import curses
from datetime import datetime

import schedule
from sh import tail

from traffic import LogParser
from helpers import init_windows, utc_now, draw_alerts, draw_traffic, draw_time


parser = argparse.ArgumentParser()
parser.add_argument("log_file", help="the access log file you want to get traffic for")
parser.add_argument("threshold", help="the threshold of traffic you want alerts for")
args = parser.parse_args()

access_log_file = args.log_file
alert_number = float(args.threshold)

log_parser = LogParser(utc_now())

screen = curses.initscr()
curses.noecho()
curses.cbreak()
screen.keypad(1)

alerts, current_alert, traffic, current_traffic, current_time = init_windows()

schedule.every(1).seconds.do(draw_time, current_time=current_time)
schedule.every(1).seconds.do(
    draw_alerts,
    alerts=alerts,
    current_alert=current_alert,
    log_parser=log_parser,
    alert_number=alert_number
)
schedule.every(10).seconds.do(
    draw_traffic,
    traffic=traffic,
    current_traffic=current_traffic,
    log_parser=log_parser
)

try:
    for line in tail("-f", access_log_file, _iter=True):
        log_parser.parse_log(line)
        schedule.run_pending()
    
except KeyboardInterrupt:
    screen.keypad(0)
    curses.nocbreak()
    curses.echo()
    curses.endwin()

finally:
    print(log_parser.summary())
