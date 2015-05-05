##
## Java builder
##
import lutinMultiprocess
import lutinTools
import lutinDepend as dependency

##
## Initialize the builder, if needed ... to get dependency between builder (for example)
##
def init():
	pass

##
## Get the current builder type.
## Return the type of builder
##
def getType():
	return "compiler"

##
## @brief Get builder input file type
## @return List of extention supported
##
def getInputType():
	return ["java"]

##
## @brief Get builder output file type
## @return List of extention supported
##
def getOutputType():
	return ["class"]