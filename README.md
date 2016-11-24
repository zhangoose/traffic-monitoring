traffic monitoring
====

Consumes an actively written to w3c-formatted HTTP access log and provides metrics:

* Every 10s: section with the most hits
* Every 10s: total hits for each section
* Every 1s: average traffic for past 2 minutes
* Every 1s: alert/recovery message if average traffic > threshold

![https://cl.ly/351e3f12243R](https://cl.ly/351e3f12243R)

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
