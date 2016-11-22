traffic monitoring
====

### Usage

Fake traffic logs:

```
gem install --no-ri --no-rdoc apache-loggen
apache-loggen --rate=1 > access.log
```

Running the traffic monitoring app:

```
python traffic.py [ACCESS LOG FILE]
```
