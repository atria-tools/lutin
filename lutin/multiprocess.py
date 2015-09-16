#!/usr/bin/python
##
## @author Edouard DUPIN
##
## @copyright 2012, Edouard DUPIN, all right reserved
##
## @license APACHE v2.0 (see license file)
##

import sys
import threading
import time
import sys
if sys.version_info >= (3, 0):
	import queue
else:
	import Queue as queue
import os
import subprocess
import shlex
# Local import
from . import debug
from . import tools
from . import env
from . import depend

queueLock = threading.Lock()
workQueue = queue.Queue()
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

##
## @brief Execute the command and ruturn generate data
##
def run_command_direct(cmd_line):
	# prepare command line:
	args = shlex.split(cmd_line)
	debug.verbose("cmd = " + str(args))
	try:
		# create the subprocess
		p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	except subprocess.CalledProcessError as e:
		debug.error("subprocess.CalledProcessError : " + str(args))
	except:
		debug.error("Exception on : " + str(args))
	# launch the subprocess:
	output, err = p.communicate()
	if sys.version_info >= (3, 0):
		output = output.decode("utf-8")
		err = err.decode("utf-8")
	# Check error :
	if p.returncode == 0:
		if output == None:
			return err[:-1];
		return output[:-1];
	else:
		return False


def run_command(cmd_line, store_cmd_line="", build_id=-1, file="", store_output_file="", depend_data=None):
	global errorOccured
	global exitFlag
	global currentIdExecution
	# prepare command line:
	args = shlex.split(cmd_line)
	debug.verbose("cmd = " + str(args))
	try:
		# create the subprocess
		p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	except subprocess.CalledProcessError as e:
		debug.error("subprocess.CalledProcessError : TODO ...")
	except:
		debug.error("Exception on : " + str(args))
	# launch the subprocess:
	output, err = p.communicate()
	if sys.version_info >= (3, 0):
		output = output.decode("utf-8")
		err = err.decode("utf-8")
	# store error if needed:
	tools.store_warning(store_output_file, output, err)
	# Check error :
	if p.returncode == 0:
		debug.debug(env.print_pretty(cmd_line))
		queueLock.acquire()
		if depend_data != None:
			depend.create_dependency_file(depend_data['file'], depend_data['data'])
		# TODO : Print the output all the time .... ==> to show warnings ...
		if build_id >= 0 and (output != "" or err != ""):
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
		if build_id < 0:
			debug.debug(env.print_pretty(cmd_line), force=True)
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
			if errorExecution["id"] >= build_id:
				# nothing to do ...
				queueLock.release()
				return;
			errorExecution["id"] = build_id
			errorExecution["cmd"] = cmd_line
			errorExecution["return"] = p.returncode
			errorExecution["err"] = err,
			errorExecution["out"] = output,
			queueLock.release()
		# not write the command file...
		return
	debug.verbose("done 3")
	# write cmd line only after to prevent errors ...
	tools.store_command(cmd_line, store_cmd_line)



class myThread(threading.Thread):
	def __init__(self, threadID, lock, queue):
		threading.Thread.__init__(self)
		self.thread_id = threadID
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
					debug.print_element( "[" + str(data[4]) + "][" + str(self.thread_id) + "] " + comment[0], comment[1], comment[2], comment[3])
					run_command(cmdLine, cmdStoreFile, build_id=data[4], file=comment[3], store_output_file=data[5], depend_data=data[6])
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



def run_in_pool(cmd_line, comment, store_cmd_line="", store_output_file="", depend_data=None):
	global currentIdExecution
	if processorAvaillable <= 1:
		debug.print_element(comment[0], comment[1], comment[2], comment[3])
		run_command(cmd_line, store_cmd_line, file=comment[3], store_output_file=store_output_file, depend_data=depend_data)
		return
	# multithreaded mode
	init()
	# Fill the queue
	queueLock.acquire()
	debug.verbose("add : in pool cmdLine")
	workQueue.put(["cmdLine", cmd_line, comment, store_cmd_line, currentIdExecution, store_output_file, depend_data])
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
		debug.debug(env.print_pretty(errorExecution["cmd"]), force=True)
		debug.print_compilator(str(errorExecution["out"][0]))
		debug.print_compilator(str(errorExecution["err"][0]))
		if errorExecution["return"] == 2:
			debug.error("can not compile file ... [keyboard interrrupt]")
		else:
			debug.error("can not compile file ... return value : " + str(errorExecution["return"]))
	
