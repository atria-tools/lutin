##
## Java builder
##
import lutinMultiprocess
import lutinTools
import lutinDebug as debug
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
def get_type():
	return "compiler"

##
## @brief Get builder input file type
## @return List of extention supported
##
def get_input_type():
	return ["java"]

##
## @brief Get builder output file type
## @return List of extention supported
##
def get_output_type():
	return ["class"]