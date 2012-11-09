#!/usr/bin/env python

'''
Python-Tail - Unix tail follow implementation in Python. 

python-tail can be used to monitor changes to a file.

Example:
    import tail

    # Create a tail instance
    t = tail.Tail('file-to-be-followed')

    # Register a callback function to be called when a new line is found in the followed file. 
    # If no callback function is registerd, new lines would be printed to standard out.
    t.register_callback(callback_function)

    # Follow the file with 5 seconds as sleep time between iterations. 
    # If sleep time is not provided 1 second is used as the default time.
    t.follow(s=5) '''

# Author - Alexis Okuwa <alexisokuwa at gmail.com>
# Source - https://github.com/wojons/python-tail
# Forked - https://github.com/kasun/python-tail

import os
import sys
import time

class Tail(object):
	''' Represents a tail command. '''
	def __init__(self, tailed_files):
		''' Initiate a Tail instance.
			Check for file validity, assigns callback function to standard out.
			
			Arguments:
				tailed_file - File to be followed. '''
		
		self.tailed_files = list()
		self.last = dict()
		self.last['filename'] = ""
		
		if type(tailed_files).__name__ == 'str': #we allow strings we will just handle the converstion
			tailed_files = [tailed_files]
		
		for tailed_file in tailed_files: #make sure we have good files all around
			self.check_file_validity(tailed_file)
			self.tailed_files.append(tailed_file)
		self.callback = sys.stdout.write
	
	def follow(self, s=1):
		''' Do a tail follow. If a callback function is registered it is called with every new line. 
		Else printed to standard out.

		Arguments:
			s - Number of seconds to wait between each iteration; Defaults to 1. '''
		
		tailed_points = []
		self.god_time = time.time()
		for filename in self.tailed_files:
			tailed_points.append(open(filename)) #get all the file points
			tailed_points[len(tailed_points)-1].seek(0, os.SEEK_END) #handle all the seeking
			
		while True:
			start_t = time.time() #gotta keep track of how long we been in this
			for num, file_ in enumerate(tailed_points):
				line = True #reset line value
				while line:
					curr_position = file_.tell() #get current postion
					line = file_.readline() #read the next line we use readline() and not readlines because we may read a line that is still being written to.
					if not line: 
						file_.seek(curr_position) #reset the seek point so we can try from the same point again
					else:
						self.exec_callback(line, self.tailed_files[num])
			time_lap = time.time()-start_t
			if(time_lap < s):
				time.sleep(s - time_lap)
	
	def exec_callback(self, line, filename):		
		if self.callback_mode == 0:
			self.callback(line)
		elif self.callback_mode == 1:
			if self.last['filename'] != filename:
				line = "===> "+filename+" <===\n"+line
				self.last['filename'] = filename
			self.callback(line, filename)
    
	def register_callback(self, func, mode=0):
		''' Overrides default callback function to provided function. '''
		self.callback = func
		self.callback_mode = mode

	def check_file_validity(self, file_):
		''' Check whether the a given file exists, readable and is a file '''
		if not os.access(file_, os.F_OK):
			raise TailError("File '%s' does not exist" % (file_))
		if not os.access(file_, os.R_OK):
			raise TailError("File '%s' not readable" % (file_))
		if os.path.isdir(file_):
			raise TailError("File '%s' is a directory" % (file_))

class TailError(Exception):
    def __init__(self, msg):
        self.message = msg
    def __str__(self):
        return self.message
