import argparse
import curses
from datetime import datetime

import schedule
from sh import tail

from traffic import LogParser
from helpers import init_windows, utc_now, draw_alerts, draw_traffic


"""
def draw_alerts(alerts, current_alert, log_parser, alert_number):
    alerts.clear()
    current_alert.clear()
    alerts.box()
    current_alert.box()

    message, average_traffic = log_parser.alert(alert_number)
    messages = ""
    for alert_log in log_parser.alert_logs[-6:]:
        formatted_time = format_dt(alert_log[0])
        if alert_log[1]:
            messages += "   [{}] High traffic generated an alert - hits = {}\n".format(formatted_time, alert_log[2])
        else:
            messages += "   [{}] Recovered! hits = {}\n".format(formatted_time, alert_log[2])
    
    if average_traffic > alert_number:
        current_alert.addstr(5, 3, str(average_traffic), curses.A_STANDOUT)
    else:
        current_alert.addstr(5, 3, str(average_traffic))

    alerts.addstr(5, 0, messages)
    alerts.addstr(1, 1, "Alert log: for average traffic > {}".format(alert_number), curses.A_BOLD)
    current_alert.addstr(1, 1, "Current Average Traffic for last 2 minutes", curses.A_BOLD)

    alerts.refresh()
    current_alert.refresh()


def draw_traffic(traffic, current_traffic, log_parser):
    traffic.clear()
    current_traffic.clear()
    traffic.box()
    current_traffic.box()

    hit = log_parser.most_hits()
    traffic_log = ""
    if hit != (None, None):
        current_traffic.addstr(5, 3, "{}: {}".format(hit[0], hit[1]))
    else:
        current_traffic.addstr(5, 3, "(none)")

    for section_name, num_hits in log_parser.hits.items():
        traffic_log += "   /{}: {}\n".format(section_name, num_hits)

    traffic.addstr(5, 0, traffic_log)
    traffic.addstr(1, 1, "Overall traffic\n(updated every 10 sec)", curses.A_BOLD)
    current_traffic.addstr(1, 1, "Section with most traffic\n(updated every 10 sec)", curses.A_BOLD)
    traffic.refresh()
    current_traffic.refresh()

"""

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

alerts, current_alert, traffic, current_traffic = init_windows()

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
