from datetime import datetime, timedelta
from dateutil.tz import tzoffset
from dateutil import parser
import re
import operator

from pytz import UTC

from helpers import utc_now, format_dt, add_to_dict


class LogParser(object):

    def __init__(self, start_time):
        self.start_time = start_time
        self.logs = {}
        self.is_alert = False
        self.alert_logs = []
        self.hits = {}

    def parse_log(self, line):
        """
        `parse_log` takes a Common Log Format line and separates it out into

        127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" 200 2326

        {
            datetime(2000, 10, 10, 13: 55): {
                "ip_address": "127.0.0.1",
                "user_identifier": "-",
                "requester": "frank",
                "timestamp": datetime(2000, 10, 10, 13, 55, 36),
                "request_method": "GET",
                "resource": "/apache_pb.gif",
                "protocol": "HTTP/1.0",
                "status_code": "200",
                "size": "2326"
            }
        }
        """
        split_line = map(''.join, re.findall(r'\"(.*?)\"|\[(.*?)\]|(\S+)', line))
        parsed_line = {
            "ip_address": split_line[0],
            "user_identifier": split_line[1],
            "requester": split_line[2],
            "status_code": split_line[5],
            "size": split_line[6]
        }

        # setting the timestamp
        parsed_line['timestamp'] = parser.parse(
            split_line[3].replace(':', ' ', 1)).astimezone(UTC)

        # setting the request method and resource
        split_http = split_line[4].split(" ")
        parsed_line['request_method'] = split_http[0]
        parsed_line['resource'] = split_http[1]
        parsed_line['protocol'] = split_http[2]

        # adding to a bucketed-by-second dictionary of all logs
        key_name = parsed_line['timestamp'].replace(microsecond=0)

        if self.logs.get(key_name):
            self.logs[key_name].append(parsed_line)
        else:
            self.logs[key_name] = [parsed_line]

        return parsed_line

    def most_hits(self):
        """
        `most_hits` goes through the logs list for the time period between now
        and 10 seconds ago and returns:

        (<section that got the most hits>, <how many hits>)
        """
        section_hits = {}
        now = datetime.utcnow().replace(tzinfo=UTC)

        # going through past 10 seconds of data
        for i in range(0, 10):
            time_key = (now - timedelta(seconds=i)).replace(microsecond=0)
            logs_list = self.logs.get(time_key) or []

            for log in logs_list:
                section = log['resource'].strip("/").split("/", 1)[0]
                add_to_dict(section_hits, section, 1)

        if section_hits != {}:
            # updating overall traffic data store with 10 seconds worth of data
            for section_name, num_hits in section_hits.items():
                add_to_dict(self.hits, section_name, num_hits)

            section_name = max(
                section_hits.iteritems(),
                key=operator.itemgetter(1)
            )[0]
            return "/{}".format(section_name), section_hits[section_name]
        return None, None

    def average_traffic(self, start, seconds):
        """
        `average_traffic` gets the average # of events that happened in the
        past `seconds` amount of seconds from the `start` date time.

        Returns the average traffic.
        """ 
        num_events = 0
        for i in range(0, seconds):
            time_key = (start - timedelta(seconds=i)).replace(microsecond=0) 
            logs_list = self.logs.get(time_key) or []
            
            num_events += len(logs_list)

        return float(num_events) / seconds

    def alert(self, alert_number):
        """
        `alert` goes through the past 120 seconds of traffic, determines the
        average # of events that occured, and compares that to the
        `alert_number`.

        Returns the average traffic.
        """
        now = utc_now()
        average_traffic = self.average_traffic(now, 120)

        if average_traffic > alert_number:
            self.is_alert = True
            self.alert_logs.append((now, True, average_traffic))

        elif self.is_alert:
            self.is_alert = False
            self.alert_logs.append((now, False, average_traffic))

        return average_traffic

    def summary(self):
        """
        `summary` goes through all hits and alert logs to get a high-level view
        of the overall traffic and alerts.

        Returns a formatted summary of the results.
        """
        summary = ""
        summary += "START: {}\nEND: {}\n\n".format(
            format_dt(self.start_time), format_dt(utc_now()))

        summary += "Overall Traffic:\n"
        for section_name, num_hits in self.hits.items():
            summary += "\t/{}: {}\n".format(section_name, num_hits)

        num_alerts = 0
        num_recoveries = 0
        for alert in self.alert_logs:
            if alert[1]:
                num_alerts += 1
            else:
                num_recoveries += 1

        summary += "\n\nNumber of high traffic alerts: {}\n".format(num_alerts)
        summary += "Number of recoveries: {}\n".format(num_recoveries)
        
        return summary
