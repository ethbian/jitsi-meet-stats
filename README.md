# jitsi-meet-stats
Jitsi Meet stats to Graphite exporter

## Introduction
Jitsi (Videobridge) provides a lot of useful [statistics](https://github.com/jitsi/jitsi-videobridge/blob/master/doc/statistics.md).  
Graphite can be used to store them, Grafana to show them in a cool way.  

## Installation

Created and tested on Ubuntu 18 with Python 2.7

### (1/3) enabling Videobrige statistics reporting

In the **/etc/jitsi/videobridge/** directory two files need to be updated.  

**config** file - replace the empty JVB_OPTS with the following:  

```
# extra options to pass to the JVB daemon
#JVB_OPTS=""
JVB_OPTS="--apis=rest,xmpp"
```

**sip-communicator.properties** file - add the following lines:

```
org.jitsi.videobridge.ENABLE_STATISTICS=true
org.jitsi.videobridge.STATISTICS_TRANSPORT=muc,colibri
org.jitsi.videobridge.STATISTICS_INTERVAL=5000
```

The last one defines how often the stats should be updated (here: 5 seconds).  
Now - restart the **videobridge** service and check with **curl** if the stats are there:

> curl http://localhost:8080/colibri/stats

### (2/3) install jmstats service

to be continued





