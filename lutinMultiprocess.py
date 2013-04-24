#!/usr/bin/python
import sys
import lutinDebug as debug
import threading
import time
import Queue
import os


def RunCommand(cmdLine):
	debug.debug(cmdLine)
	ret = os.system(cmdLine)
	# TODO : Use "subprocess" instead ==> permit to pipline the renderings ...
	if ret != 0:
		if ret == 2:
			debug.error("can not compile file ... [keyboard interrrupt]")
		else:
			debug.error("can not compile file ... ret : " + str(ret))

exitFlag = False

class myThread(threading.Thread):
	def __init__(self, threadID, lock, queue):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = "Thread " + str(threadID)
		self.queue = queue
		self.lock = lock
	def run(self):
		print("Starting " + self.name)
		global exitFlag
		global queueLock
		global workQueue
		while False==exitFlag:
			self.lock.acquire()
			if not self.queue.empty():
				data = self.queue.get()
				self.lock.release()
				print "%s processing %s" % (self.name, data[0])
				if data[0]=="cmdLine":
					comment = data[2]
					cmdLine = data[1]
					debug.printElement(comment[0], comment[1], comment[2], comment[3])
					RunCommand(cmdLine)
				else:
					debug.warning("unknow request command : " + data[0])
			else:
				# no element to parse, just wait ...
				self.lock.release()
				time.sleep(0.2)
		# kill requested ...
		print("Exiting " + self.name)

queueLock = threading.Lock()
workQueue = Queue.Queue()
threads = []

isInit = False
processorAvaillable = 1

def ErrorOccured():
	global exitFlag
	exitFlag = True

def SetCoreNumber(numberOfcore):
	processorAvaillable = numberOfcore
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
			print("join thread ... \n")
			tmp.join()
		print "Exiting Main Thread"



def RunInPool(cmdLine, comment):
	if processorAvaillable <= 1:
		debug.printElement(comment[0], comment[1], comment[2], comment[3])
		RunCommand(cmdLine)
		return
	# multithreaded mode
	Init()
	# Fill the queue
	queueLock.acquire()
	debug.verbose("add : in pool cmdLine")
	workQueue.put(["cmdLine", cmdLine, comment])
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
	debug.verbose("queue is empty")
	os.path.flush()
	
