#!/usr/bin/env python

''' 
python-tail example.
Does a tail follow against /var/log/syslog with a time interval of 5 seconds.
Prints recieved new lines to standard out '''

import tail

history = {'filename' : ''}

def print_line(txt, filename):
	''' Prints received text '''
	global history
	if history['filename'] != filename:
		txt = "===> "+filename+" <===\n"+txt
		history['filename'] = filename
	print txt.strip("\n")

t = tail.Tail(['/var/log/syslog'])
t.register_callback(print_line, 1)
t.follow(10)


