#!/usr/bin/python
import sys
import lutinDebug as debug
import threading
import time
import Queue
import os
import subprocess
import lutinTools
import lutinEnv

queueLock = threading.Lock()
workQueue = Queue.Queue()
currentThreadWorking = 0
threads = []

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


def run_command(cmdLine, storeCmdLine=""):
	debug.debug(lutinEnv.print_pretty(cmdLine))
	try:
		retcode = subprocess.call(cmdLine, shell=True)
	except OSError as e:
		print >>sys.stderr, "Execution failed:", e
	
	if retcode != 0:
		global errorOccured
		errorOccured = True
		global exitFlag
		exitFlag = True
		if retcode == 2:
			debug.error("can not compile file ... [keyboard interrrupt]")
		else:
			debug.error("can not compile file ... ret : " + str(retcode))
		return
	
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
		while False==exitFlag:
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
					debug.print_element( "[" + str(self.threadID) + "] " + comment[0], comment[1], comment[2], comment[3])
					run_command(cmdLine, cmdStoreFile)
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
	if processorAvaillable <= 1:
		debug.print_element(comment[0], comment[1], comment[2], comment[3])
		run_command(cmdLine, storeCmdLine)
		return
	# multithreaded mode
	init()
	# Fill the queue
	queueLock.acquire()
	debug.verbose("add : in pool cmdLine")
	workQueue.put(["cmdLine", cmdLine, comment, storeCmdLine])
	queueLock.release()
	

def pool_synchrosize():
	global errorOccured
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
		debug.debug("Thread return with error ... ==> stop all the pool")
		un_init()
		debug.error("Pool error occured ...")
	
