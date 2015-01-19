#!/bin/bash

# Root Check
if [ $(whoami) != "root" ]; then
	echo "$(date) GPIO Syslog Daemon for Splunk Perimeter Security must be run as root. Exiting."
	exit 1
fi


ScriptPath="$( cd "$(dirname "$0")" ; pwd -P )"
$ScriptPath/gpio-syslog-daemon.py status | grep "not running"
RET="$?"

echo "ret = $RET"

if [ "$RET" == "0" ]; then
	echo "$(date) Daemon was not running. Starting daemon."
	$ScriptPath/gpio-syslog-daemon.py start
else
	echo "$(date) Daemon is running"
fi

