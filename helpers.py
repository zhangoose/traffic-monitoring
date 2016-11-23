from datetime import datetime
import curses

from pytz import UTC


def utc_now():
    """
    `now` returns a timezone aware date time in UTC .
    """
    return datetime.utcnow().replace(tzinfo=UTC)


def format_dt(dt):
    """
    `format_dt` returns a formatted date time `dt`.
    """
    return datetime.strftime(dt, "%m/%d/%y - %H:%M:%S %z")


def init_windows():
    """
    `init_windows` returns the 4 curses windows.
    """
    alerts = curses.newwin(20, 100, 1, 1)
    current_alert = curses.newwin(20, 30, 1, 101)
    traffic = curses.newwin(20, 100, 21, 31)
    current_traffic = curses.newwin(20, 30, 21, 1)
    current_time = curses.newwin(3, 100, 42, 1)

    alerts.box()
    current_alert.box()
    traffic.box()
    current_traffic.box()
    current_time.box()

    alerts.addstr(1, 1, "Alert log: for average traffic", curses.A_BOLD)
    current_alert.addstr(1, 1, "Current Average Traffic for last 2 minutes", curses.A_BOLD)
    current_traffic.addstr(1, 1, "Section with most traffic\n(updated every 10 sec)", curses.A_BOLD)
    traffic.addstr(1, 1, "Overall traffic\n(updated every 10 sec)", curses.A_BOLD)

    alerts.refresh()
    current_alert.refresh()
    traffic.refresh()
    current_traffic.refresh()
    current_time.refresh()

    return alerts, current_alert, traffic, current_traffic, current_time


def draw_time(current_time):
    """
    `draw_time` adds the current time in UTC to the `current_time` window.
    """
    current_time.clear()
    current_time.box()

    current_time.addstr(1, 1, format_dt(utc_now()))

    current_time.refresh()


def draw_alerts(alerts, current_alert, log_parser, alert_number):
    """
    `draw_alerts` adds the last 6 alert logs to the `alerts` window and adds
    the current average traffic in the last 2 minutes to the `current_alert`
    window.
    """
    alerts.clear()
    current_alert.clear()
    alerts.box()
    current_alert.box()

    average_traffic = log_parser.alert(alert_number)
    messages = ""
    for alert_log in log_parser.alert_logs[-6:]:
        formatted_time = format_dt(alert_log[0])
        if alert_log[1]:
            messages += "   [{}] High traffic generated an alert - hits = {}\n".format(formatted_time, alert_log[2])
        else:
            messages += "   [{}] Recovered! hits = {}\n".format(formatted_time, alert_log[2])

    if log_parser.is_alert:
        current_alert.addstr(5, 3, str(average_traffic), curses.A_STANDOUT)
    else:
        current_alert.addstr(5, 3, str(average_traffic))

    alerts.addstr(5, 0, messages)
    alerts.addstr(1, 1, "Alert log: for average traffic > {}".format(alert_number), curses.A_BOLD)
    current_alert.addstr(1, 1, "Current Average Traffic for last 2 minutes", curses.A_BOLD)

    alerts.refresh()
    current_alert.refresh()


def draw_traffic(traffic, current_traffic, log_parser):
    """
    `draw_traffic` adds the overall traffic to the `traffic` window and adds
    the section name with the most traffic to the `current_traffic` window.
    """
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
