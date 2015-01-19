# TA - Splunk Perimeter Security
This is a Splunk TA package, meant to be deployed to a Raspberry Pi running Splunk.

For more information, see [Splunk Perimeter Security](https://github.com/Ricapar/splunk-perimeter-security) app.

# Raspberry Pi Requirements
* A Raspberry Pi
* An SD Card running Raspbian or other compatible Linux distribution for the Raspberry Pi 
* [Splunk Forwarder for Linux ARM](https://apps.splunk.com/app/1611/)
* Python 2.7 or greater
* Alarm system wired to GPIO pins

## Not required, but recommended if you are wiring your own alarm system: 

* [Raspberry Pi T Cobbler with Ribbon Cable](http://www.amazon.com/s/?_encoding=UTF8&camp=1789&creative=390957&field-keywords=raspberry%20pi%20t%20cobbler&linkCode=ur2&sprefix=raspb%2Caps%2C213&tag=ricaparnet-20&url=search-alias%3Daps&linkId=G7M2TCV7Q3UFSQSI)
* [Solderless Breadboard](http://www.amazon.com/s/?_encoding=UTF8&camp=1789&creative=390957&field-keywords=solderless%20breadboard&linkCode=ur2&sprefix=solderless%20b%2Caps%2C166&tag=ricaparnet-20&url=search-alias%3Dindustrial&linkId=Q3PFJCCCJU3DJ46Z) 
* [Jumper Wires](http://www.amazon.com/s/?_encoding=UTF8&camp=1789&creative=390957&field-keywords=jumper%20wires&linkCode=ur2&rh=n%3A16310091%2Ck%3Ajumper%20wires&tag=ricaparnet-20&url=search-alias%3Dindustrial&linkId=WV3WBY3PQ57OARDX)

# Sample Data
Included is a sample data file template (gzipped).

You may load this into Splunk by having it monitor the file directly, or using a `splunk add oneshot`
to load a point-in time.


# Raspberry Pi GPIO Setup
**Note:** Your wiring may (and probably will) vary, depending on how you design your alarm system.

All Raspberry Pi models have two rows of GPIO pins (how many per row varies on the Raspberry Pi model)
that can be programatically turned on or off, or have a HIGH or LOW value read. Please refer to the GPIO
pinout chart that was included with your specific model.

The sample script uses the basic premise of a traditional alarm system: When a monitored door or entryway is
in a secured or closed state, an electrical circuit is completed. When that entryway is opened (or someone cuts the alarm wire)
the electrical circuit is broken.

This configuration is demonstrated below using the 3.3v pin and four GPIO pins on a Raspberry Pi B+:

![Raspberry Pi GPIO Alarm Wiring](http://i.imgur.com/UIlZTQk.png)

As shown on the diagram, zones 1, 3 and 4 are closed. If you were to attach a multimeter between pins 1 and 27,
17, or 4, you should see a 3.3v reading. Zone 2 is currently in an open state; a multimeter reading across the same
circuit path would read 0v. When the Raspberry Pi reads from a GPIO pin, it sees either a HIGH or a LOW reading.
Closed zones with 3.3v register as HIGH, open zones with 0v register as LOW.

## Prerequisites 
* Splunk Universal Forwarder set up with outputs.conf going to your indexer.
* python-rpi.gpio package

The ```python-rpi.gpio``` package can be installed on Raspbian by running:

```sudo apt-get install python-rpi.gpio```

If you are running a different Linux distribution, consult that distro's package management
system for more information.

## Deploying TA-PerimeterSecurity

This guide assumes you already have a Splunk Universal Forwarder installed on your Raspberry Pi,
and it is configured to send to your Splunk indexer. 

The TA containing the Python scripts to monitor the GPIO pins should not require much modification,
but as with any script running on your system, it is encouraged you review and understand what it is doing.

The script detects what hardware version of the Raspbery Pi you are running, and sets up monitors
for all available GPIO pins.

```
rpiPins = [
        [ 4, 17, 21, 22, 18, 23, 24, 25 ],
        [ 4, 17, 27, 22, 18, 23, 24, 25 ],
        [ 4, 17, 27, 22, 5, 6, 13, 19, 26, 18, 23, 24, 25, 12, 16, 20, 21 ]
]
```

This array allows the Python script to use the hardware revision number (`RPi.GPIO.RPI_REVISION`) minus 1
to indicate what pins it should listen on.

If your setup does not utilize all of the available pins, you may wish to manually remove some from here
to reduce the amount of unnessecary information in your events. If you choose to leave them enabled,
alerting on pins can be disabled via a lookup table within Splunk.

The provided shell script enables Splunk to start the listening daemon and periodically check the status
of the running process.