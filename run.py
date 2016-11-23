import argparse
import curses

import schedule
from sh import tail

from traffic import LogParser


def poop(border, screen, log_parser, alert_number):
    message = log_parser.alert(alert_number)
    messages = ""
    for alert_log in log_parser.alert_logs[-6:]:
        if alert_log[1]:
            messages += "High traffic generated an alert - hits = {}, triggered at {}\n".format(alert_log[2], alert_log[0])
        else:
            messages += "Recovered! hits = {} at {}\n".format(alert_log[2], alert_log[0])
    
    border.addstr(1,1,messages)
    #screen.refresh()
    border.refresh()



parser = argparse.ArgumentParser()
parser.add_argument("log_file", help="the access log file you want to get traffic for")
parser.add_argument("threshold", help="the threshold of traffic you want alerts for")
args = parser.parse_args()

access_log_file = args.log_file
alert_number = float(args.threshold)

log_parser = LogParser()
#schedule.every(10).seconds.do(log_parser.most_hits)
#schedule.every(1).seconds.do(log_parser.alert, alert_number=alert_number)

screen = curses.initscr()
curses.noecho()
curses.cbreak()
screen.keypad(1)
q = -1

border1 = curses.newwin(20, 100, 1, 1)
border1.box()
schedule.every(1).seconds.do(poop, border=border1, screen=screen, log_parser=log_parser, alert_number=alert_number)



for line in tail("-f", access_log_file, _iter=True):
    log_parser.parse_log(line)

    #screen.refresh()
    #border1.refresh()

    schedule.run_pending()
    """
    if screen.getch() == ord('q'):
        curses.nocbreak()
        screen.keypad(0)
        curses.echo()

        curses.endwin()       
        break

    """

