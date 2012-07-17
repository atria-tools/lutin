#!/usr/bin/env python
#
# @file make-final.py
# @author Y.M. Morgan
# @date 2012/07/09
#
# Generate the final directory by copying files from staging directories
# 

import sys, os, logging
import optparse
import shutil

#===============================================================================
# Global variables.
#===============================================================================

# Directories to exclude
EXCLUDE_DIRS = ["include", "man"]

# Extension to exclude
EXCLUDE_FILTERS = [".a", ".la"]

#===============================================================================
# Determine if a file is an executable.
#===============================================================================
def isExec(filePath):
	result = False
	try:
		file = open(filePath, "r")
		header = str(file.read(4))
		if header.find("ELF") >= 0:
			result = True
		file.close()
	except IOError as ex:
		logging.error("Unable to open %s ([err=%d] %s)",
			filePath, ex.errno, ex.strerror)
	return result

#===============================================================================
# Main function.
#===============================================================================
def main():
	(options, args) = parseArgs()
	setupLog(options)

	# get parameters
	stagingDir = args[0]
	finalDir = args[1]
	logging.info("staging-dir : %s", stagingDir)
	logging.info("final-dir : %s", finalDir)

	# check that staging directory exists
	if not os.path.isdir(stagingDir):
		logging.error("%s is not a directory", stagingDir)

	# browse staging directory
	for (dirPath, dirNames, fileNames) in os.walk(stagingDir):
		# exclude some directories
		for dirName in EXCLUDE_DIRS:
			if dirName in dirNames:
				logging.debug("Exclude directory : %s",
					os.path.relpath(os.path.join(dirPath, dirName), stagingDir))
				dirNames.remove(dirName)
		for fileName in fileNames:
			# skip dome extensions
			srcFileName = os.path.join(dirPath, fileName)
			relPath = os.path.relpath(srcFileName, stagingDir)
			if os.path.splitext(srcFileName)[1] in EXCLUDE_FILTERS:
				logging.debug("Exclude file : %s", relPath) 
				continue
			logging.info("File : %s", relPath)
			# destination
			dstFileName = os.path.join(finalDir, relPath)
			dstDirName = os.path.split(dstFileName)[0]
			if not os.path.exists(dstDirName):
				os.makedirs(dstDirName, 0755)
			# copy and strip executables
			if isExec(srcFileName):
				os.system("%s -o %s %s" % (options.strip, dstFileName, srcFileName))
			else:
				shutil.copy2(srcFileName, dstFileName)

#===============================================================================
# Setup option parser and parse command line.
#===============================================================================
def parseArgs():
	usage = "usage: %prog [options] <staging-dir> <final-dir>"
	parser = optparse.OptionParser(usage = usage)
	parser.add_option("--strip",
		dest="strip",
		default=None,
		help="strip program to use to remove symbols")
	parser.add_option("-q",
		dest="quiet",
		action="store_true",
		default=False,
		help="be quiet")
	parser.add_option("-v",
		dest="verbose",
		action="count",
		default=0,
		help="verbose output (more verbose if specified twice)")

	(options, args) = parser.parse_args()
	if len(args) > 2:
		parser.error("Too many parameters")
	elif len(args) < 2:
		parser.error("Not enough parameters")
	if options.strip == None:
		parser.error("Missing strip option")
	return (options, args)

#===============================================================================
# Setup logging system.
#===============================================================================
def setupLog(options):
	logging.basicConfig(
		level=logging.WARNING,
		format="[%(levelname)s] %(message)s",
		stream=sys.stderr)
	logging.addLevelName(logging.CRITICAL, "C")
	logging.addLevelName(logging.ERROR, "E")
	logging.addLevelName(logging.WARNING, "W")
	logging.addLevelName(logging.INFO, "I")
	logging.addLevelName(logging.DEBUG, "D")

	# setup log level
	if options.quiet == True:
		logging.getLogger().setLevel(logging.CRITICAL)
	elif options.verbose >= 2:
		logging.getLogger().setLevel(logging.DEBUG)
	elif options.verbose >= 1:
		logging.getLogger().setLevel(logging.INFO)

#===============================================================================
# Entry point.
#===============================================================================
if __name__ == "__main__":
	main()

