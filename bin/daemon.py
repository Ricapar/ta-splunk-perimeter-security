#!/usr/bin/env python
"""
Daemon-Python (0.2)
Lightweight and no-nonsense POSIX daemon library
https://github.com/stackd/daemon-py
DOCUMENTATION
----------------------------------------
see README.md
LICENSE
----------------------------------------
MIT/X11, see LICENSE
DEPENDENCIES
----------------------------------------
Python 3.x.x
"""
import sys 
import os 
import time 
import atexit
import signal

class Daemon:
    """ A generic daemon class for Python 3.x.x
    
    Usage: subclass the Daemon class and override the run() method
    """
    def __init__(self, pidfile): self.pidfile = pidfile
    
    def daemonize(self):
        """UNIX double fork mechanism. 
        
        See Stevens' "Advanced Programming in the UNIX Environment" for details (ISBN 0201563177).
        """
        
        try: 
            pid = os.fork() 
            if pid > 0:
                # exit first parent
                sys.exit(0) 
        except OSError as err: 
            sys.stderr.write('fork #1 failed: {0}\n'.format(err))
            sys.exit(1)
    
        # decouple from parent environment
        os.chdir('/') 
        os.setsid() 
        os.umask(0) 
    
        # do second fork
        try: 
            pid = os.fork() 
            if pid > 0:

                # exit from second parent
                sys.exit(0) 
        except OSError as err: 
            sys.stderr.write('fork #2 failed: {0}\n'.format(err))
            sys.exit(1) 
    
        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = open(os.devnull, 'r')
        so = open(os.devnull, 'a+')
        se = open(os.devnull, 'a+')

        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())
    
        # write pidfile
        atexit.register(self.delpid)

        pid = str(os.getpid())
        with open(self.pidfile,'w+') as f:
            f.write(pid + '\n')
    
    def delpid(self):
        os.remove(self.pidfile)

    def start(self):
        """Start the daemon."""

        # Check for a pidfile to see if the daemon is already running
        try:
            with open(self.pidfile,'r') as pf:

                pid = int(pf.read().strip())
        except IOError:
            pid = None
    
        if pid:
            message = "pidfile {0} already exists. " + \
                    "{1} already running?\n"
            sys.stderr.write(message.format(self.pidfile, self.__class__.__name__))
            sys.exit(1)
        
        # Start the daemon
        self.daemonize()
        self.run()

    def stop(self):
        """Stop the daemon."""

        # Get the pid from the pidfile
        try:
            with open(self.pidfile,'r') as pf:
                pid = int(pf.read().strip())
        except IOError:
            pid = None
    
        if not pid:
            message = "pidfile {0} does not exist. " + \
                    "{1} not running?\n"
            sys.stderr.write(message.format(self.pidfile, self.__class__.__name__))
            return # not an error in a restart

        # Try killing the daemon process    
        try:
            while 1:
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.1)
        except OSError as err:
            e = str(err.args)
            if e.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print (str(err.args))
                sys.exit(1)

    def restart(self):
        """Restart the daemon."""
        
        self.stop()
        self.start()
        
    def status(self):
        """Return the daemon state."""
        
        # Check for a pidfile to see if the daemon is already running
        try:
            with open(self.pidfile,'r') as pf:
                pid = int(pf.read().strip())
        except IOError:
            pid = None
        
        if pid:
            message = "{0} ({1}) is running.\n"
            sys.stdout.write(message.format(self.__class__.__name__, self.pidfile))
        elif not pid:
            message = "pidfile {0} does not exist. " + \
                    "{1} not running.\n"
            sys.stdout.write(message.format(self.pidfile, self.__class__.__name__))

    def run(self):
        """Override this method when you subclass Daemon.
        
        It will be called after the process has been daemonized by 
        start() or restart().
        """
