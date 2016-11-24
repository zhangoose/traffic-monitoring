traffic monitoring
====

Consumes an actively written to w3c-formatted HTTP access log and provides metrics:

* Every 10s: section with the most hits
* Every 10s: total hits for each section
* Every 1s: average traffic for past 2 minutes
* Every 1s: alert/recovery message if average traffic > threshold

![img](https://d17oy1vhnax1f7.cloudfront.net/items/1l2P2l242U2x0m0l0F2B/Screen%20Recording%202016-11-23%20at%2009.15%20PM.gif?v=45c5f13d)

### Local Setup

Install requirements from requirements.txt

```
pip install -r requirements.txt
```

### Usage

I'm using [apache_log_gen](https://github.com/tamtam180/apache_log_gen) to generate fake Common Log Formatted access logs.

```
gem install --no-ri --no-rdoc apache-loggen
apache-loggen --rate=1 > access.log
```

Running the traffic monitoring app:

```
pip install -r requirements.txt
python traffic.py [ACCESS LOG FILE] [AVERAGE TRAFFIC THRESHOLD #]
```

Press control-C to escape out of the UI.

### Tests

Tests are powered by pytest.

```
pytest tests.py
```
