#!/usr/bin/python
# -*- coding: utf-8 -*-
##
## @author Edouard DUPIN
##
## @copyright 2012, Edouard DUPIN, all right reserved
##
## @license APACHE v2.0 (see license file)
##

from lutin import debug
from lutin import system
from lutin import tools
import os

class System(system.System):
	def __init__(self, target):
		system.System.__init__(self)
		# create some HELP:
		self.help = "C: Generic C library"
		self.valid = True
		# no check needed ==> just add this:
		#self.add_export_flag("c", "-D__STDCPP_GNU__")
		#self.add_export_flag("c++", "-nodefaultlibs")
		
		self.add_header_file([
		    "/usr/include/unistd*",
		    "/usr/include/assert.h*",
		    "/usr/include/ctype.h*",
		    "/usr/include/errno.h*",
		    "/usr/include/execinfo.h*",
		    "/usr/include/fenv.h*",
		    "/usr/include/float.h*",
		    "/usr/include/inttypes.h*",
		    "/usr/include/iso646.h*",
		    "/usr/include/limits.h*",
		    "/usr/include/locale.h*",
		    "/usr/include/setjmp.h*",
		    "/usr/include/signal.h*",
		    "/usr/include/string.h*",
		    "/usr/include/strings.h*",
		    "/usr/include/std*",
		    "/usr/include/tgmath.h*",
		    "/usr/include/time.h*",
		    "/usr/include/uchar.h*",
		    "/usr/include/wchar.h*",
		    "/usr/include/wctype.h*",
		    "/usr/include/features.h*",
		    "/usr/include/xlocale.h*",
		    "/usr/include/endian.h*",
		    "/usr/include/alloca.h*",
		    "/usr/include/libio.h*",
		    "/usr/include/_G_config.h*",
		    "/usr/include/fcntl.h*",
		    "/usr/include/utime.h*",
		    "/usr/include/dlfcn.h*",
		    "/usr/include/libintl.h*",
		    "/usr/include/getopt.h*",
		    "/usr/include/dirent.h*",
		    "/usr/include/setjmp.h*",
		    "/usr/include/netdb.h*",
		    "/usr/include/syslog.h*",
		    "/usr/include/memory.h*",
		    "/usr/include/poll.h*",
		    "/usr/include/termios.h*",
		    "/usr/include/regex.h*",
		    "/usr/include/semaphore.h*",
		    "/usr/include/libgen.h*",
		    "/usr/include/ifaddrs.h*",
		    "/usr/include/stropts.h*",
		    "/usr/include/pwd.h*",
		    ],
		    recursive=False)
		self.add_header_file([
		    "/usr/include/sys/*",
		    ],
		    destination_path="sys",
		    recursive=True)
		self.add_header_file([
		    "/usr/include/bits/*",
		    ],
		    destination_path="bits",
		    recursive=True)
		self.add_header_file([
		    "/usr/include/gnu/*",
		    ],
		    destination_path="gnu",
		    recursive=True)
		self.add_header_file([
		    "/usr/include/linux/*",
		    ],
		    destination_path="linux",
		    recursive=True)
		self.add_header_file([
		    "/usr/include/asm/*",
		    ],
		    destination_path="asm",
		    recursive=True)
		self.add_header_file([
		    "/usr/include/asm-generic/*",
		    ],
		    destination_path="asm-generic",
		    recursive=True)
		self.add_header_file([
		    "/usr/include/netinet/*",
		    ],
		    destination_path="netinet",
		    recursive=True)
		self.add_header_file([
		    "/usr/include/net/*",
		    ],
		    destination_path="net",
		    recursive=True)
		self.add_export_flag("link", "-B/usr/lib")


