#!/usr/bin/python
import sys
import lutinDebug as debug
import threading
import time
import Queue
import os
import subprocess

def RunCommand(cmdLine, storeCmdLine=""):
	debug.debug(cmdLine)
	retcode = -1
	try:
		retcode = subprocess.call(cmdLine, shell=True)
	except OSError as e:
		print >>sys.stderr, "Execution failed:", e
	
	
	# write cmd line only after to prvent errors ...
	if storeCmdLine!="":
		file2 = open(storeCmdLine, "w")
		file2.write(cmdLine)
		file2.flush()
		file2.close()
	# TODO : Use "subprocess" instead ==> permit to pipline the renderings ...
	
	if retcode != 0:
		if retcode == 2:
			debug.error("can not compile file ... [keyboard interrrupt]")
		else:
			debug.error("can not compile file ... ret : " + str(retcode))

exitFlag = False

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
					debug.printElement( "[" + str(self.threadID) + "] " + comment[0], comment[1], comment[2], comment[3])
					RunCommand(cmdLine, cmdStoreFile)
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

queueLock = threading.Lock()
workQueue = Queue.Queue()
currentThreadWorking = 0
threads = []

isInit = False
processorAvaillable = 1

def ErrorOccured():
	global exitFlag
	exitFlag = True

def SetCoreNumber(numberOfcore):
	global processorAvaillable
	processorAvaillable = numberOfcore
	debug.debug(" set number of core for multi process compilation : " + str(processorAvaillable))
	# nothing else to do

def Init():
	global exitFlag
	global isInit
	if isInit==False:
		isInit=True
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
		


def UnInit():
	global exitFlag
	# Notify threads it's time to exit
	exitFlag = True
	if processorAvaillable > 1:
		# Wait for all threads to complete
		for tmp in threads:
			debug.verbose("join thread ...")
			tmp.join()
		debug.verbose("Exiting ALL Threads")



def RunInPool(cmdLine, comment, storeCmdLine=""):
	if processorAvaillable <= 1:
		debug.printElement(comment[0], comment[1], comment[2], comment[3])
		RunCommand(cmdLine, storeCmdLine)
		return
	# multithreaded mode
	Init()
	# Fill the queue
	queueLock.acquire()
	debug.verbose("add : in pool cmdLine")
	workQueue.put(["cmdLine", cmdLine, comment, storeCmdLine])
	queueLock.release()
	

def PoolSynchrosize():
	if processorAvaillable <= 1:
		#in this case : nothing to synchronise
		return
	
	debug.verbose("wait queue process ended\n")
	# Wait for queue to empty
	while not workQueue.empty():
		time.sleep(0.2)
		pass
	# Wait all thread have ended their current process
	while currentThreadWorking != 0:
		time.sleep(0.2)
		pass
	debug.verbose("queue is empty")
	
