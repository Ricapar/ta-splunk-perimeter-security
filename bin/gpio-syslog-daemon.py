#!/usr/bin/env python
import os
import sys
import time
import datetime
import logging
import RPi.GPIO as GPIO
from daemon import Daemon
from socket import gethostname

rpiPins = [
	[ 4, 17, 21, 22, 18, 23, 24, 25 ],
	[ 4, 17, 27, 22, 18, 23, 24, 25 ], 
	[ 4, 17, 27, 22, 5, 6, 13, 19, 26, 18, 23, 24, 25, 12, 16, 20, 21 ]
]

gpioPins = rpiPins[GPIO.RPI_REVISION - 1]

# Set up logging
logger = logging.getLogger("SplunkPerimeterSecurity")
logger.setLevel(logging.INFO)

# Log to /var/log 
handler = logging.FileHandler('/var/log/splunk-perimeter-security')
handler.setLevel(logging.INFO)

# Make the logs kinda look like syslog 
formatter = logging.Formatter('%(asctime)s app=\"Splunk Perimeter Security\" src_host="'+gethostname()+'" %(message)s', '%b %e %H:%M:%S')
handler.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(handler)


class SplunkPerimeterSecurity(Daemon):
	
	# The RaspberryPi has had a few different revisions,
	# each with their own GPIO pin configurations.
	# There are a few more pins that can be used for GPIO, but
	# they also serve other purposes, such as serial TX/RX 
	# and SPI 

	def zone_changed(self, pin):
		pinStatus = "closed" if GPIO.input(pin) else "open"
		zone = gpioPins.index(pin)
		logger.info("type=alert subject=\"Zone State Changed\" src=ZONE%02d src_category=zone_trigger pin=%d body=%s " % ( zone, pin, pinStatus))
	

	def setup_zones(self):
		GPIO.setmode(GPIO.BCM)
		for zone, pin in enumerate(gpioPins):
			logger.info('type=event severity=informational src=ZONE%02d src_category=startup pin=%d subject="Configuring GPIO pin" body=\"Configuring GPIO pin\"' % ( zone, pin ))
			GPIO.setup(pin, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
			GPIO.add_event_detect(
				pin,
				GPIO.BOTH,
				callback = self.zone_changed,
				bouncetime = 200
			)

	def output_status(self):
		outputStr = ""
		for zone, pin in enumerate(gpioPins):
			pinStatus = "closed" if GPIO.input(pin) else "open"
			logger.info("type=event severity=informational src=ZONE%02d src_category=zone pin=%d body=%s" % ( zone, pin, pinStatus))

	def run(self):
		try:
			logger.info('type=event severity=informational src_category=startup event=init body="SplunkPerimeterSecurity is starting up"')
			self.setup_zones()
			logger.info('type=event severity=informational src_category=startup event=init body="SplunkPerimeterSecurity is ready"')
			
			while True:
				self.output_status()
				time.sleep(60)
		except:
			print sys.exc_info()
			logger.critical('action=shutdown severity=critical event=shutdown body="SplunkPerimeterSecurity monitoring is SHUTTING DOWN" exception="%s"' % ( sys.exc_info()[0]) )
			sys.exit(1)
			
		
if __name__ == "__main__":
	daemon = SplunkPerimeterSecurity('/var/run/splunk-perimeter-security.pid')

	if len(sys.argv) == 2:
		if 'start' == sys.argv[1]:
			daemon.start()
		elif 'stop' == sys.argv[1]:
			daemon.stop()
		elif 'restart' == sys.argv[1]:
			daemon.restart()
		elif 'status' == sys.argv[1]:
			daemon.status()
		else:
			sys.stdout.write("Unknown command\n")
			sys.exit(2)
		sys.exit(0)
	else:
		sys.stdout.write("Usage: %s start | stop | restart | status\n" % sys.argv[0])
		sys.exit(2)


