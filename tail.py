#!/usr/bin/env python

'''
Python-Tail - Unix tail follow implementation in Python. 

python-tail can be used to monitor changes to a file.

Example:
    import tail

    # Create a tail instance
    t = self.Tail('file-to-be-followed')

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
    tailed_files  = list()
    tailed_points = list()
    callbacks     = dict()
    inode         = list()
    
    def __init__(self):
        ''' Initiate a Tail instance.
            Check for file validity, assigns callback function to standard out.
            
            Arguments:
                tailed_file - File to be followed. '''
    
    def tail(self, tailed_files, callback=None):
        if type(tailed_files).__name__ == 'str': #we allow strings we will just handle the converstion
            tailed_files = [tailed_files]
        
        for tailed_file in tailed_files: #make sure we have good files all around
            try:
                self.check_file_validity(tailed_file)
            except TailError as e:
                sys.stderr.write(str(e))
                
            if tailed_file not in self.tailed_files: #make sure we dont have the file already
                self.tailed_files.append(tailed_file)
                self.callbacks[tailed_file] = callback #if callback == None else sys.stdout.write
        
        #self.callback = sys.stdout.write
    
    def set_follow_filename(self, boolean):
        """
        Set true or false if you want program to follow file even if inode changes like when logrotate runes see gnu tail --folow=name
        """
        self.follow_filename = boolean
    
    def follow(self, s=1, max_time=None, loop_max=True):
        ''' Do a tail follow. If a callback function is registered it is called with every new line. 
        Else printed to standard out.

        Arguments:
            s - Number of seconds to wait between each iteration; Defaults to 1.
            max_time - the appoxment number of seocnds the loop should run for
            loop_max - the max number of times the loop should run over
        '''
        
        for filename in self.tailed_files:
            if len(self.tailed_points)-1 < self.tailed_files.index(filename):
                self.tailed_points.append(self.open_file(filename)) #get all the file points
                
                if self.tailed_points[len(self.tailed_points)-1] != None:
                    self.tailed_points[len(self.tailed_points)-1].seek(0, os.SEEK_END) #handle all the seeking
        
        follow_t = time.time()
        
        while loop_max != 0 and (max_time == None or time.time() <= max_time+follow_t):
            start_t  = time.time() #gotta keep track of how long we been in this
                
            for num, file_ in enumerate(self.tailed_points):
                if file_ != None:
                    file_ = self.read_2_EOF(num, file_)
                else:
                    self.tailed_points[num] = self.open_file(self.tailed_files[num])
                
                if self.follow_filename == True: #check to see if inode has changed
                    self.check_inode(num, self.tailed_files[num])
                    
            if loop_max != True:
                loop_max -= 1
                
                if loop_max == 0: continue
            
            time_lap = time.time()-start_t
            if(time_lap < s):  time.sleep(s - time_lap)
            
    def read_2_EOF(self, dex, file_):
        if file_ == None: return None
            
        line = True #reset line value
        while line:
            curr_position = file_.tell() #get current postion
            line = file_.readline() #read the next line we use readline() and not readlines because we may read a line that is still being written to.
            if not line:
                file_.seek(curr_position) #reset the seek point so we can try from the same point again
            else:
                self.exec_callback(line, self.tailed_files[dex])
        return file_
    
    def exec_callback(self, line, filename):
        if filename in self.callabcks:
            self.callbacks[filename]({'line':line, 'filename':filename})
        else:
            print ({'line':line, 'filename':filename})
        
    def get_inode(self, filename):
        try:
            return os.stat(filename).st_ino
        except OSError as e:
            return None
            
    def get_file_num(self, filename):
        try:
            return self.tailed_files.index(filename)
        except:
            return None
            
    def open_file(self, filename):
        try:
            if not os.access(filename, os.F_OK): return None
            if not os.access(filename, os.R_OK): return None
            if os.path.isdir(filename):  return None
                
            file_ = open(filename)
            
            if self.get_file_num(filename) in self.inode:
                self.inode[self.get_file_num(filename)] = self.get_inode(filename)
            else:
                self.inode.append(self.get_inode(filename))
            
            return file_
        
        except (IOError, OSError) as e:
            return None
            
    def check_inode(self, num, filename):
        try:
            if self.get_inode(filename) != self.inode[num]: #check if the inode has changed
                self.read_2_EOF(num, self.tailed_points[num]) #read the current but old file to EOF
                self.tailed_points[num] = self.open_file(filename) # reopen the file pointer to the replacment file
                
        except OSError as e:
            pass

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

