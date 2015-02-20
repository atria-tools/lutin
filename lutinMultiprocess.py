#!/usr/bin/python
##
## @author Edouard DUPIN
##
## @copyright 2012, Edouard DUPIN, all right reserved
##
## @license APACHE v2.0 (see license file)
##

import sys
import lutinDebug as debug
import threading
import time
import Queue
import os
import subprocess
import lutinTools
import lutinEnv
import shlex

queueLock = threading.Lock()
workQueue = Queue.Queue()
currentThreadWorking = 0
threads = []
# To know the first error arrive in the pool ==> to display all the time the same error file when multiple compilation
currentIdExecution = 0
errorExecution = {
	"id":-1,
	"cmd":"",
	"return":0,
	"err":"",
	"out":"",
}

exitFlag = False # resuest stop of the thread
isinit = False # the thread are initialized
errorOccured = False # a thread have an error
processorAvaillable = 1 # number of CPU core availlable

def store_command(cmdLine, file):
	# write cmd line only after to prevent errors ...
	if     file != "" \
	   and file != None:
		# Create directory:
		lutinTools.create_directory_of_file(file)
		# Store the command Line:
		file2 = open(file, "w")
		file2.write(cmdLine)
		file2.flush()
		file2.close()

##
## @brief Execute the command and ruturn generate data
##
def run_command_direct(cmdLine):
	# prepare command line:
	args = shlex.split(cmdLine)
	debug.verbose("cmd = " + str(args))
	try:
		# create the subprocess
		p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	except subprocess.CalledProcessError as e:
		debug.error("subprocess.CalledProcessError : " + str(args))
	# launch the subprocess:
	output, err = p.communicate()
	# Check error :
	if p.returncode == 0:
		if output == None:
			return err[:-1];
		return output[:-1];
	else:
		return False


def run_command(cmdLine, storeCmdLine="", buildId=-1, file=""):
	global errorOccured
	global exitFlag
	global currentIdExecution
	# prepare command line:
	args = shlex.split(cmdLine)
	debug.verbose("cmd = " + str(args))
	try:
		# create the subprocess
		p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	except subprocess.CalledProcessError as e:
		debug.error("subprocess.CalledProcessError : TODO ...")
	# launch the subprocess:
	output, err = p.communicate()
	# Check error :
	if p.returncode == 0:
		debug.debug(lutinEnv.print_pretty(cmdLine))
		queueLock.acquire()
		# TODO : Print the output all the time .... ==> to show warnings ...
		if buildId >= 0 and (output != "" or err != ""):
			debug.warning("output in subprocess compiling: '" + file + "'")
		if output != "":
			debug.print_compilator(output)
		if err != "":
			debug.print_compilator(err)
		queueLock.release()
	else:
		errorOccured = True
		exitFlag = True
		# if No ID : Not in a multiprocess mode ==> just stop here
		if buildId < 0:
			debug.debug(lutinEnv.print_pretty(cmdLine), force=True)
			debug.print_compilator(output)
			debug.print_compilator(err)
			if p.returncode == 2:
				debug.error("can not compile file ... [keyboard interrrupt]")
			else:
				debug.error("can not compile file ... ret : " + str(p.returncode))
		else:
			# in multiprocess interface
			queueLock.acquire()
			# if an other write an error before, check if the current process is started before ==> then is the first error
			if errorExecution["id"] >= buildId:
				# nothing to do ...
				queueLock.release()
				return;
			errorExecution["id"] = buildId
			errorExecution["cmd"] = cmdLine
			errorExecution["return"] = p.returncode
			errorExecution["err"] = err,
			errorExecution["out"] = output,
			queueLock.release()
		# not write the command file...
		return
	debug.verbose("done 3")
	# write cmd line only after to prevent errors ...
	store_command(cmdLine, storeCmdLine)



class myThread(threading.Thread):
	def __init__(self, threadID, lock, queue):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = "Thread " + str(threadID)
		self.queue = queue
		self.lock = lock
	def run(self):
		debug.verbose("Starting " + self.name)
		global exitFlag
		global currentThreadWorking
		workingSet = False
		while exitFlag == False:
			self.lock.acquire()
			if not self.queue.empty():
				if workingSet==False:
					currentThreadWorking += 1
					workingSet = True
				data = self.queue.get()
				self.lock.release()
				debug.verbose(self.name + " processing '" + data[0] + "'")
				if data[0]=="cmdLine":
					comment = data[2]
					cmdLine = data[1]
					cmdStoreFile = data[3]
					debug.print_element( "[" + str(data[4]) + "][" + str(self.threadID) + "] " + comment[0], comment[1], comment[2], comment[3])
					run_command(cmdLine, cmdStoreFile, buildId=data[4], file=comment[3])
				else:
					debug.warning("unknow request command : " + data[0])
			else:
				if workingSet==True:
					currentThreadWorking -= 1
					workingSet=False
				# no element to parse, just wait ...
				self.lock.release()
				time.sleep(0.2)
		# kill requested ...
		debug.verbose("Exiting " + self.name)


def error_occured():
	global exitFlag
	exitFlag = True

def set_core_number(numberOfcore):
	global processorAvaillable
	processorAvaillable = numberOfcore
	debug.debug(" set number of core for multi process compilation : " + str(processorAvaillable))
	# nothing else to do

def init():
	global exitFlag
	global isinit
	if isinit==False:
		isinit=True
		global threads
		global queueLock
		global workQueue
		# Create all the new threads
		threadID = 0
		while threadID < processorAvaillable:
			thread = myThread(threadID, queueLock, workQueue)
			thread.start()
			threads.append(thread)
			threadID += 1
		


def un_init():
	global exitFlag
	# Notify threads it's time to exit
	exitFlag = True
	if processorAvaillable > 1:
		# Wait for all threads to complete
		for tmp in threads:
			debug.verbose("join thread ...")
			tmp.join()
		debug.verbose("Exiting ALL Threads")



def run_in_pool(cmdLine, comment, storeCmdLine=""):
	global currentIdExecution
	if processorAvaillable <= 1:
		debug.print_element(comment[0], comment[1], comment[2], comment[3])
		run_command(cmdLine, storeCmdLine, file=comment[3])
		return
	# multithreaded mode
	init()
	# Fill the queue
	queueLock.acquire()
	debug.verbose("add : in pool cmdLine")
	workQueue.put(["cmdLine", cmdLine, comment, storeCmdLine, currentIdExecution])
	currentIdExecution +=1;
	queueLock.release()
	

def pool_synchrosize():
	global errorOccured
	global errorExecution
	if processorAvaillable <= 1:
		#in this case : nothing to synchronise
		return
	
	debug.verbose("wait queue process ended\n")
	# Wait for queue to empty
	while not workQueue.empty() \
	      and False==errorOccured:
		time.sleep(0.2)
		pass
	# Wait all thread have ended their current process
	while currentThreadWorking != 0 \
	      and False==errorOccured:
		time.sleep(0.2)
		pass
	if False==errorOccured:
		debug.verbose("queue is empty")
	else:
		un_init()
		debug.debug("Thread return with error ... ==> stop all the pool")
		if errorExecution["id"] == -1:
			debug.error("Pool error occured ... (No return information on Pool)")
			return
		debug.error("Error in an pool element : [" + str(errorExecution["id"]) + "]", crash=False)
		debug.debug(lutinEnv.print_pretty(errorExecution["cmd"]), force=True)
		debug.print_compilator(str(errorExecution["out"][0]))
		debug.print_compilator(str(errorExecution["err"][0]))
		if errorExecution["return"] == 2:
			debug.error("can not compile file ... [keyboard interrrupt]")
		else:
			debug.error("can not compile file ... return value : " + str(errorExecution["return"]))
	
