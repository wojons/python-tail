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
    follow_filename = False
    follows = dict()
    
    def __init__(self):
        ''' Initiate a Tail instance.
            Check for file validity, assigns callback function to standard out.
            
            Arguments:
                tailed_file - File to be followed. '''
    
    def tail(self, files, callback=None):
        if type(files).__name__ == 'str': #we allow strings we will just handle the converstion
            files = [files]
        
        for filename in files: #make sure we have good files all around
            try:
                self.check_file_validity(filename)
            except TailError as e:
                sys.stderr.write(str(e))
            
            if filename not in self.follows: #make sure we dont have the file already
                self.new_follow(filename)
                self.set_callback(filename, callback)
        
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
        
        for filename in self.follows:
            
            if self.get_filename_fd(filename) is None:
                self.open_file(filename) #get all the file points
                
                if self.get_filename_fd(filename) != None:
                    self.follows[filename]['fd'].seek(0, os.SEEK_END) #handle all the seeking
        
        follow_t = time.time()
        
        while loop_max != 0 and (max_time == None or time.time() <= max_time+follow_t):
            start_t  = time.time() #gotta keep track of how long we been in this
            
            for filename, file_ in self.follows.iteritems():
                if file_['fd'] != None:
                    file_ = self.read_2_EOF(filename, file_['fd'])
                else:
                    self.open_file(filename)
                
                if self.follow_filename == True: #check to see if inode has changed
                    self.check_inode(filename)
                    
            if loop_max != True:
                loop_max -= 1
                
                if loop_max == 0: continue
            
            time_lap = time.time()-start_t
            if(time_lap < s):  time.sleep(s - time_lap)
            
    def read_2_EOF(self, filename, file_):
        if file_ == None: return None
            
        line = True #reset line value
        while line:
            curr_position = file_.tell() #get current postion
            line = file_.readline() #read the next line we use readline() and not readlines because we may read a line that is still being written to.
            if not line:
                file_.seek(curr_position) #reset the seek point so we can try from the same point again
            else:
                self.exec_callback(line, filename)
        return file_
    
    def exec_callback(self, line, filename):
        if filename in self.follows and self.follows[filename].get('callback') is not None:
            self.follows[filename]['callback']({'line':line, 'filename':filename})
        else:
            print ({'line':line, 'filename':filename})
        
    def get_inode(self, filename):
        try:
            return os.stat(filename).st_ino
        except OSError as e:
            return None
            
    def get_filename_inode(self, filename):
        if filename in self.follows: return self.follows[filename].get('inode')
            
    def get_file_num(self, filename):
        try:
            return self.tailed_files.index(filename)
        except:
            return None
            
    def set_callback(self, filename, callback):
        self.follows[filename]['callback'] = callback
            
    def open_file(self, filename):
        try:
            if not os.access(filename, os.F_OK): return None
            if not os.access(filename, os.R_OK): return None
            if os.path.isdir(filename):  return None
                
            self.follows[filename]['fd'] = open(filename)
            self.follows[filename]['inode'] = self.get_inode(filename)
            
        except (IOError, OSError) as e:
            pass
    
    def get_filename_fd(self, filename):
        if filename in self.follows: return self.follows[filename].get('fd')
        
    def check_inode(self, filename):
        try:
            if self.get_inode(filename) != self.get_filename_inode(filename): #check if the inode has changed
                self.read_2_EOF(filename, self.get_filename_fd(filename)) #read the current but old file to EOF
                self.open_file(filename) # reopen the file pointer to the replacment file
                
        except OSError as e:
            pass
            
    def new_follow(self, filename, overwrite=False):
        if filename not in self.follows or overwrite is True:
            self.follows[filename] = {'fd': None, 'callback': None, 'inode': None}
            return True
            
        return True

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
