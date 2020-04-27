# jitsi-meet-stats
Jitsi Meet stats to Graphite exporter + sample Grafana dashboards

## Introduction
Jitsi (Videobridge) provides a lot of useful [statistics](https://github.com/jitsi/jitsi-videobridge/blob/master/doc/statistics.md).  
Graphite can be used to store them, Grafana to show them in a cool way.  

## Installation

Created and tested on Ubuntu 18 with Python 2.7, Grafana 6.7.1 with Graphite as a data source.  
Working with Videobridge and Videobridge2.

> Jitsi Videobridge --> Colibri stats --> jmstats --> Graphite --> Grafana

### (0/3) requirements

* Python **requests** and **psutil** modules need to be installed:

```
apt-get install python-requests
apt-get install python-psutil
```

* Jitsi statistics are sent to and stored by **Graphite**  
  It should have the pickle listener enabled in the **carbon.conf** file:

```
PICKLE_RECEIVER_INTERFACE = 0.0.0.0
PICKLE_RECEIVER_PORT = 2004
```
  
* If you want to use provided dashboards you'll also need **Grafana**  
  with **the Graphite** configured as data source  
  
Graphite and Grafana installation is out of scope for this document.  
  
Note: looks like cpu_usage and used_memory metrics have been removed from the stats  
in the latest version (what a pity!). So we're using python's psutil module to report additionaly:  
**custom_cpu_usage**: current system-wide CPU utilization as a percentage (0-100)  
**custom_mem_usage**: physical memory usage as a percentage (0-100)
  
### (1/3) enabling Videobrige statistics reporting

In the **/etc/jitsi/videobridge/** directory two files need to be updated.  

**config** file - replace the empty JVB_OPTS with the following:  
  
**(a) videobridge:** 
```
# extra options to pass to the JVB daemon
# JVB_OPTS=""
JVB_OPTS="--apis=rest,xmpp"
```

**(b) videobridge2:**
```
# extra options to pass to the JVB daemon
# JVB_OPTS="--apis=,"
JVB_OPTS="--apis=rest"
```

**sip-communicator.properties** file - add/modify the following lines:

```
org.jitsi.videobridge.ENABLE_STATISTICS=true
org.jitsi.videobridge.STATISTICS_TRANSPORT=muc,colibri
org.jitsi.videobridge.STATISTICS_INTERVAL=5000
```

The last one defines how often the stats should be updated (here: 5 seconds).  
Now - restart the **videobridge** service and check with **curl** if the stats are there:

> curl http://localhost:8080/colibri/stats

### (2/3) install jmstats service

```
git clone --depth=1 https://github.com/ethbian/jitsi-meet-stats.git
cd jitsi-meet-stats
chmod +x jmstats.py
```

Edit the **jmstats.py** file and update the variables (at least the first one):

```
# change these:
CARBON_SERVER = 'graphite.example.com'
GRAPHITE_PREFIX = 'metrics.jitsi.{}'.format(socket.gethostname())
LOG_FILE = '/var/log/jitsi/jmstats.log'
SKIP_METRICS = ['current_timestamp', 'conference_sizes']
JITSI_STATS = 'http://localhost:8080/colibri/stats'
CARBON_PICKLE_PORT = 2004
SLEEP_SEC = 5
```

The **CARBON_SERVER** defines your graphite server.  
If you change **GRAPHITE_PREFIX** you'll have to update provided grafana dashboards as well  
(dashboard variables). Once finished - execute the jmstats.py script and see if it's working.

```
cp jmstats.py /usr/local/bin/
cp jmstats.service /lib/systemd/system/
systemctl start jmstats
systemctl enable jmstats
```

One last thing:  
in our configuration Jitsi exports statistics every 5 seconds (as per **sip-communicator.properties**),  
every 5 seconds as well **jmstats.py** (**SLEEP_SEC** variable) sends them Graphite.  
Remember to update Graphite retention accordingly (**storage-schemas.conf**), for example:  
> retentions = 5s:1h,1m:24h,5m:7d,1h:365d  


### (3/3) import sample grafana dashboards

Log in **as admin** to your Grafana and import the dashboard **json** files.  
  
Provided files were exported from **Grafana 6.7.1** with **Graphite** configured  
as a data source named '**graphite**'. If you're having problems importing the  
dashboards you may want to try to edit the json files manually - to change for example  
required Grafana version.


## Last but not least

...pull requests are more than welcome if you're adding or fixing something
