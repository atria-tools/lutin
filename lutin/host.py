#!/usr/bin/python
##
## @author Edouard DUPIN
##
## @copyright 2012, Edouard DUPIN, all right reserved
##
## @license APACHE v2.0 (see license file)
##

import platform
import sys
from . import debug

# print os.name # ==> 'posix'
if platform.system() == "Linux":
	OS = "Linux"
elif platform.system() == "Windows":
	OS = "Windows"
elif platform.system() == "Darwin":
	OS = "MacOs"
else:
	debug.error("Unknow the Host OS ... '" + platform.system() + "'")

debug.debug("host.OS = " + OS)


if sys.maxsize > 2**32:
	BUS_SIZE = 64
else:
	BUS_SIZE = 32

debug.debug("host.BUS_SIZE = " + str(BUS_SIZE))

