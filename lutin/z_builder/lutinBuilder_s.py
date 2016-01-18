##
## ASM builder
##
from lutin import multiprocess
from lutin import tools
from lutin import depend

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
	return ["s", "S"]

##
## @brief Get builder output file type
## @return List of extention supported
##
def get_output_type():
	return ["o"]

##
## @brief Get builder support multi-threading or not
## @return True Multithreading supported
## @return False Multithreading NOT supported
##
def get_support_multithreading():
	return True
